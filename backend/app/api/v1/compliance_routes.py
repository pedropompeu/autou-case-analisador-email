"""
Rotas de conformidade, privacidade e LGPD da API v1.
Permite exportação de dados do titular, direito ao esquecimento e execução de retenção.
"""
import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.app.services.compliance_service import ComplianceService
from backend.app.utils.rbac import get_current_user, roles_required
from backend.app.utils.tenant_context import get_current_tenant_id

logger = logging.getLogger(__name__)

compliance_bp = Blueprint("compliance", __name__)


@compliance_bp.route("/export", methods=["POST"])
@jwt_required()
@roles_required("admin", "auditor")
def export_subject_data():
    """
    Exporta todos os dados vinculados a um titular específico para atendimento à LGPD.
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return (
            jsonify({"error": "tenant_context_required", "message": "Tenant not identified"}),
            400,
        )

    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier") or data.get("email")
    if not identifier:
        return (
            jsonify(
                {"error": "validation_error", "message": "'identifier' or 'email' is required"}
            ),
            400,
        )

    try:
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        result = ComplianceService.export_subject_data(
            tenant_id=tenant_id, subject_identifier=identifier, requester_user_id=user_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Error during LGPD export: {e}")
        return jsonify({"error": "compliance_error", "message": str(e)}), 500


@compliance_bp.route("/erasure", methods=["POST"])
@jwt_required()
@roles_required("admin")
def erase_subject_data():
    """
    Executa anonimização/expurgo de dados para atender ao Direito ao Esquecimento (LGPD Art. 18).
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return (
            jsonify({"error": "tenant_context_required", "message": "Tenant not identified"}),
            400,
        )

    data = request.get_json(silent=True) or {}
    identifier = data.get("identifier") or data.get("email")
    if not identifier:
        return (
            jsonify(
                {"error": "validation_error", "message": "'identifier' or 'email' is required"}
            ),
            400,
        )

    try:
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        result = ComplianceService.erase_subject_data(
            tenant_id=tenant_id, subject_identifier=identifier, requester_user_id=user_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Error during LGPD erasure: {e}")
        return jsonify({"error": "compliance_error", "message": str(e)}), 500


@compliance_bp.route("/retention-run", methods=["POST"])
@jwt_required()
@roles_required("admin")
def run_retention_cleanup():
    """
    Executa limpeza dos dados anteriores ao período de retenção configurado.
    """
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return (
            jsonify({"error": "tenant_context_required", "message": "Tenant not identified"}),
            400,
        )

    data = request.get_json(silent=True) or {}
    retention_days = data.get("retention_days")
    if retention_days is not None:
        try:
            retention_days = int(retention_days)
        except (ValueError, TypeError):
            return (
                jsonify(
                    {"error": "validation_error", "message": "'retention_days' must be an integer"}
                ),
                400,
            )

    try:
        current_user = get_current_user()
        user_id = current_user.id if current_user else None
        result = ComplianceService.run_retention_cleanup(
            tenant_id=tenant_id, retention_days=retention_days, requester_user_id=user_id
        )
        return jsonify(result), 200
    except Exception as e:
        logger.exception(f"Error during retention cleanup: {e}")
        return jsonify({"error": "compliance_error", "message": str(e)}), 500
