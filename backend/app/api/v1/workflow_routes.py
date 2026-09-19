"""
Rotas para Workflows, Notas Internas, Atribuições e Regras de Roteamento (#11, #41, #44, #45).
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from backend.app import db
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.internal_note import InternalNote
from backend.app.models.routing_rule import RoutingRule
from backend.app.models.user import User
from backend.app.utils.rbac import roles_required, get_current_user
from backend.app.utils.tenant_context import get_current_tenant_id
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

workflow_bp = Blueprint("workflow", __name__)


# ─── NOTAS INTERNAS (#45) ───────────────────────────────────────────────────

@workflow_bp.route("/analyze/<int:analysis_id>/notes", methods=["GET"])
@jwt_required()
def list_internal_notes(analysis_id):
    """Lista as notas internas da equipe para uma análise."""
    tenant_id = get_current_tenant_id()
    analysis = EmailAnalysis.query.filter_by(id=analysis_id, is_deleted=False).first()
    if not analysis or (tenant_id and analysis.tenant_id != tenant_id):
        return jsonify({"error": "not_found", "message": "Analysis not found"}), 404

    notes = InternalNote.query.filter_by(analysis_id=analysis_id, is_deleted=False).order_by(InternalNote.created_at.asc()).all()
    return jsonify({
        "notes": [
            {
                "id": n.id,
                "user_id": n.user_id,
                "username": n.user.username if n.user else "System",
                "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in notes
        ]
    }), 200


@workflow_bp.route("/analyze/<int:analysis_id>/notes", methods=["POST"])
@jwt_required()
@roles_required("admin", "operator")
def add_internal_note(analysis_id):
    """Adiciona uma nova nota interna privada."""
    tenant_id = get_current_tenant_id()
    analysis = EmailAnalysis.query.filter_by(id=analysis_id, is_deleted=False).first()
    if not analysis or (tenant_id and analysis.tenant_id != tenant_id):
        return jsonify({"error": "not_found", "message": "Analysis not found"}), 404

    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "validation_error", "message": "Content is required"}), 400

    current_user = get_current_user()
    user_id = current_user.id if current_user else None

    note = InternalNote(
        tenant_id=analysis.tenant_id,
        analysis_id=analysis.id,
        user_id=user_id,
        content=content
    )
    db.session.add(note)
    db.session.commit()

    return jsonify({
        "message": "Note added successfully",
        "note": {
            "id": note.id,
            "user_id": note.user_id,
            "username": current_user.username if current_user else "System",
            "content": note.content,
            "created_at": note.created_at.isoformat()
        }
    }), 201


# ─── STATUS & ATRIBUIÇÃO (#41, #44) ─────────────────────────────────────────

@workflow_bp.route("/analyze/<int:analysis_id>/status", methods=["PATCH"])
@jwt_required()
@roles_required("admin", "operator")
def update_analysis_status(analysis_id):
    """Atualiza o status de atendimento da análise (pending, in_progress, resolved, escalated)."""
    tenant_id = get_current_tenant_id()
    analysis = EmailAnalysis.query.filter_by(id=analysis_id, is_deleted=False).first()
    if not analysis or (tenant_id and analysis.tenant_id != tenant_id):
        return jsonify({"error": "not_found", "message": "Analysis not found"}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    allowed_statuses = ["pending", "in_progress", "resolved", "escalated"]
    if new_status not in allowed_statuses:
        return jsonify({
            "error": "validation_error",
            "message": f"Invalid status '{new_status}'. Allowed: {allowed_statuses}"
        }), 400

    old_status = analysis.status
    analysis.status = new_status
    db.session.commit()

    AuditService.log(
        action="workflow.status_change",
        resource_type="EmailAnalysis",
        resource_id=str(analysis.id),
        details={"old_status": old_status, "new_status": new_status},
        tenant_id=analysis.tenant_id
    )

    return jsonify({
        "message": "Status updated successfully",
        "id": analysis.id,
        "status": analysis.status
    }), 200


@workflow_bp.route("/analyze/<int:analysis_id>/assign", methods=["PATCH"])
@jwt_required()
@roles_required("admin", "operator")
def assign_analysis(analysis_id):
    """Atribui a análise a um operador da equipe."""
    tenant_id = get_current_tenant_id()
    analysis = EmailAnalysis.query.filter_by(id=analysis_id, is_deleted=False).first()
    if not analysis or (tenant_id and analysis.tenant_id != tenant_id):
        return jsonify({"error": "not_found", "message": "Analysis not found"}), 404

    data = request.get_json(silent=True) or {}
    target_user_id = data.get("user_id")

    if target_user_id is not None:
        target_user = User.query.filter_by(id=target_user_id, is_active=True, is_deleted=False).first()
        if not target_user or (tenant_id and target_user.tenant_id != tenant_id):
            return jsonify({"error": "not_found", "message": "Target user not found in organization"}), 404
        analysis.assigned_to_user_id = target_user.id
    else:
        analysis.assigned_to_user_id = None

    db.session.commit()

    AuditService.log(
        action="workflow.assigned",
        resource_type="EmailAnalysis",
        resource_id=str(analysis.id),
        details={"assigned_to_user_id": analysis.assigned_to_user_id},
        tenant_id=analysis.tenant_id
    )

    return jsonify({
        "message": "Assignment updated successfully",
        "id": analysis.id,
        "assigned_to_user_id": analysis.assigned_to_user_id
    }), 200


# ─── REGRAS DE ROTEAMENTO & SLA (#11, #17) ──────────────────────────────────

@workflow_bp.route("/routing-rules", methods=["GET"])
@jwt_required()
def list_routing_rules():
    """Lista as regras de automação ativas no tenant."""
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return jsonify({"error": "tenant_context_required", "message": "Tenant not identified"}), 400

    rules = RoutingRule.query.filter_by(tenant_id=tenant_id, is_deleted=False).order_by(RoutingRule.priority.asc()).all()
    return jsonify({
        "rules": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "condition_field": r.condition_field,
                "condition_operator": r.condition_operator,
                "condition_value": r.condition_value,
                "action_type": r.action_type,
                "action_payload": r.action_payload,
                "priority": r.priority,
                "is_active": r.is_active,
            }
            for r in rules
        ]
    }), 200


@workflow_bp.route("/routing-rules", methods=["POST"])
@jwt_required()
@roles_required("admin")
def create_routing_rule():
    """Cria uma nova regra de roteamento / SLA automatizada."""
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return jsonify({"error": "tenant_context_required", "message": "Tenant not identified"}), 400

    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    condition_field = data.get("condition_field", "").strip()
    condition_value = str(data.get("condition_value", "")).strip()
    action_type = data.get("action_type", "").strip()

    if not all([name, condition_field, condition_value, action_type]):
        return jsonify({
            "error": "validation_error",
            "message": "Fields 'name', 'condition_field', 'condition_value', and 'action_type' are required"
        }), 400

    rule = RoutingRule(
        tenant_id=tenant_id,
        name=name,
        description=data.get("description"),
        condition_field=condition_field,
        condition_operator=data.get("condition_operator", "equals"),
        condition_value=condition_value,
        action_type=action_type,
        action_payload=data.get("action_payload", {}),
        priority=int(data.get("priority", 100)),
        is_active=bool(data.get("is_active", True))
    )
    db.session.add(rule)
    db.session.commit()

    return jsonify({
        "message": "Routing rule created successfully",
        "rule": {
            "id": rule.id,
            "name": rule.name,
            "condition_field": rule.condition_field,
            "action_type": rule.action_type,
            "priority": rule.priority
        }
    }), 201


@workflow_bp.route("/routing-rules/<int:rule_id>", methods=["DELETE"])
@jwt_required()
@roles_required("admin")
def delete_routing_rule(rule_id):
    """Deleta uma regra de automação."""
    tenant_id = get_current_tenant_id()
    rule = RoutingRule.query.filter_by(id=rule_id, tenant_id=tenant_id, is_deleted=False).first()
    if not rule:
        return jsonify({"error": "not_found", "message": "Routing rule not found"}), 404

    rule.is_deleted = True
    db.session.commit()

    return jsonify({"message": "Routing rule deleted successfully"}), 200
