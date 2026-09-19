"""
Rotas administrativas e de auditoria para compliance e gestão de tenants (RBAC: Admin / Auditor).
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.app import db
from backend.app.models.audit_log import AuditLog
from backend.app.models.user import User
from backend.app.models.tenant import Tenant
from backend.app.utils.rbac import roles_required, get_current_user
from backend.app.utils.tenant_context import get_current_tenant_id
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/audit-logs", methods=["GET"])
@jwt_required()
@roles_required("admin", "auditor")
def list_audit_logs():
    """
    Retorna a trilha de auditoria imutável do tenant atual.
    Acesso restrito para Administradores e Auditores de Compliance.
    """
    tenant_id = get_current_tenant_id()
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)

    query = AuditLog.query
    if tenant_id is not None:
        query = query.filter_by(tenant_id=tenant_id)

    # Filtros opcionais
    action_filter = request.args.get("action")
    if action_filter:
        query = query.filter(AuditLog.action.ilike(f"%{action_filter}%"))

    pagination = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    logs = []
    for entry in pagination.items:
        logs.append({
            "id": entry.id,
            "action": entry.action,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "user_id": entry.user_id,
            "ip_address": entry.ip_address,
            "details": entry.details,
            "created_at": entry.created_at.isoformat(),
        })

    return jsonify({
        "items": logs,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
    }), 200


@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@roles_required("admin")
def list_tenant_users():
    """Lista todos os usuários pertencentes ao tenant atual."""
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return jsonify({"error": "No tenant associated"}), 400

    users = User.query.filter_by(tenant_id=tenant_id, is_deleted=False).all()
    return jsonify({
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
    }), 200


@admin_bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@jwt_required()
@roles_required("admin")
def update_user_role(user_id):
    """Atualiza o papel (RBAC) de um usuário do mesmo tenant."""
    tenant_id = get_current_tenant_id()
    current_admin = get_current_user()

    user = User.query.filter_by(id=user_id, tenant_id=tenant_id, is_deleted=False).first()
    if not user:
        return jsonify({"error": "User not found in current organization"}), 404

    data = request.get_json() or {}
    new_role = data.get("role")
    if new_role not in ["admin", "operator", "viewer", "auditor"]:
        return jsonify({"error": "Invalid role", "allowed": ["admin", "operator", "viewer", "auditor"]}), 400

    old_role = user.role
    user.role = new_role
    db.session.commit()

    AuditService.log(
        action="user.role_change",
        resource_type="User",
        resource_id=str(user.id),
        details={"old_role": old_role, "new_role": new_role},
        user_id=current_admin.id if current_admin else None,
        tenant_id=tenant_id,
    )

    logger.info(f"User {user.username} role changed from {old_role} to {new_role} by {current_admin.username if current_admin else 'admin'}")
    return jsonify({
        "message": "Role updated successfully",
        "user_id": user.id,
        "new_role": user.role,
    }), 200
