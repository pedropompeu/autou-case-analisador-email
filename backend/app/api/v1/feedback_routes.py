"""
Rota de feedback (Human-in-the-loop).

Permite ao usuário aprovar ou corrigir a classificação feita pela IA,
armazenando o feedback no banco para métricas e eventual fine-tuning.
"""
import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from backend.app.api.v1 import api_v1_bp
from backend.app.api.v1.schemas import FeedbackRequestSchema
from backend.app import db
from backend.app.services.audit_service import AuditService
from backend.app.utils.tenant_context import get_current_tenant_id
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.feedback import AnalysisFeedback
from backend.app.models.user import User

logger = logging.getLogger(__name__)

feedback_schema = FeedbackRequestSchema()


@api_v1_bp.route("/feedback", methods=["POST"])
@jwt_required()
def submit_feedback():
    """
    Registra feedback do usuário sobre uma análise.
    """
    try:
        data = feedback_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    # Verificar se a análise existe e respeita o tenant
    tenant_id = get_current_tenant_id()
    query = EmailAnalysis.query.filter_by(id=data["analysis_id"], is_deleted=False)
    if tenant_id is not None:
        query = query.filter_by(tenant_id=tenant_id)
    
    analysis = query.first()
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    # Resolver user_id a partir do JWT
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()

    feedback = AnalysisFeedback(
        tenant_id=tenant_id,
        analysis_id=data["analysis_id"],
        approved=data["approved"],
        corrected_category=data.get("corrected_category"),
        corrected_summary=data.get("corrected_summary"),
        notes=data.get("notes"),
        user_id=user.id if user else None,
    )

    db.session.add(feedback)
    db.session.commit()

    action = "approved" if data["approved"] else "corrected"
    AuditService.log(
        action=f"feedback.{action}",
        resource_type="AnalysisFeedback",
        resource_id=str(feedback.id),
        details={
            "analysis_id": data["analysis_id"],
            "approved": data["approved"],
            "corrected_category": data.get("corrected_category"),
        },
        user_id=user.id if user else None,
        tenant_id=tenant_id,
    )

    logger.info(
        f"Feedback {action} for analysis {data['analysis_id']} "
        f"by user {current_username}"
    )

    return jsonify({
        "message": f"Feedback registered successfully",
        "feedback_id": feedback.id,
    }), 201
