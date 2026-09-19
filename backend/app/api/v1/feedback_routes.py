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

    ---
    tags:
      - Feedback
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - analysis_id
            - approved
          properties:
            analysis_id:
              type: integer
              description: ID da análise a avaliar
            approved:
              type: boolean
              description: Se o usuário aprova a classificação da IA
            corrected_category:
              type: string
              enum: [Produtivo, Improdutivo]
              description: Categoria corrigida (obrigatório se approved=false)
            corrected_summary:
              type: string
              description: Resumo corrigido (opcional)
            notes:
              type: string
              description: Observações adicionais
    responses:
      201:
        description: Feedback registrado com sucesso
      400:
        description: Dados de entrada inválidos
      404:
        description: Análise não encontrada
    """
    try:
        data = feedback_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    # Verificar se a análise existe
    analysis = EmailAnalysis.query.filter_by(
        id=data["analysis_id"], is_deleted=False
    ).first()

    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404

    # Resolver user_id a partir do JWT
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()

    feedback = AnalysisFeedback(
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
    logger.info(
        f"Feedback {action} for analysis {data['analysis_id']} "
        f"by user {current_username}"
    )

    return jsonify({
        "message": f"Feedback registered successfully",
        "feedback_id": feedback.id,
    }), 201
