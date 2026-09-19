"""
Rota de métricas agregadas para o dashboard.
"""
import logging
from flask import jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from backend.app.api.v1 import api_v1_bp
from backend.app import db
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.feedback import AnalysisFeedback

logger = logging.getLogger(__name__)

# Estimativa conservadora: cada email analisado automaticamente poupa
# ~2 minutos de trabalho manual de triagem e resposta.
_MINUTES_SAVED_PER_ANALYSIS = 2


@api_v1_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """
    Retorna métricas agregadas para o dashboard.

    ---
    tags:
      - Dashboard
    responses:
      200:
        description: Métricas agregadas
        schema:
          type: object
          properties:
            total_analyses:
              type: integer
            productive_count:
              type: integer
            unproductive_count:
              type: integer
            productive_percentage:
              type: number
            unproductive_percentage:
              type: number
            avg_processing_time_ms:
              type: number
            cached_count:
              type: integer
            total_feedbacks:
              type: integer
            corrections_count:
              type: integer
            time_saved_estimate_hours:
              type: number
    """
    try:
        # Contagens por categoria
        base_query = EmailAnalysis.query.filter_by(is_deleted=False)
        total = base_query.count()

        productive = base_query.filter_by(category="Produtivo").count()
        unproductive = base_query.filter_by(category="Improdutivo").count()

        # Tempo médio de processamento (em ms)
        avg_time_result = db.session.query(
            func.avg(EmailAnalysis.processing_time_ms)
        ).filter(
            EmailAnalysis.is_deleted.is_(False),
            EmailAnalysis.processing_time_ms.isnot(None),
        ).scalar()
        avg_processing_time_ms = round(float(avg_time_result), 1) if avg_time_result else 0

        # Análises que vieram do cache (hash duplicado)
        cached_subquery = (
            db.session.query(EmailAnalysis.content_hash)
            .filter(EmailAnalysis.is_deleted.is_(False))
            .group_by(EmailAnalysis.content_hash)
            .having(func.count(EmailAnalysis.id) > 1)
        )
        cached_count = cached_subquery.count()

        # Feedbacks
        total_feedbacks = AnalysisFeedback.query.filter_by(is_deleted=False).count()
        corrections_count = AnalysisFeedback.query.filter_by(
            is_deleted=False, approved=False
        ).count()

        # Estimativa de tempo economizado
        time_saved_hours = round((total * _MINUTES_SAVED_PER_ANALYSIS) / 60, 1)

        stats = {
            "total_analyses": total,
            "productive_count": productive,
            "unproductive_count": unproductive,
            "productive_percentage": round((productive / total) * 100, 1) if total > 0 else 0,
            "unproductive_percentage": round((unproductive / total) * 100, 1) if total > 0 else 0,
            "avg_processing_time_ms": avg_processing_time_ms,
            "cached_count": cached_count,
            "total_feedbacks": total_feedbacks,
            "corrections_count": corrections_count,
            "time_saved_estimate_hours": time_saved_hours,
        }

        return jsonify(stats), 200

    except Exception as e:
        logger.exception(f"Error computing stats: {e}")
        return jsonify({"error": "Failed to compute stats"}), 500
