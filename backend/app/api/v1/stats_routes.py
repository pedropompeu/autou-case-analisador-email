"""
Rota de métricas agregadas e ROI para o dashboard enterprise.
"""
import logging

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from backend.app import db
from backend.app.api.v1 import api_v1_bp
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.feedback import AnalysisFeedback

logger = logging.getLogger(__name__)

# Estimativa conservadora de triagem manual:
# ~2.5 minutos de trabalho manual de leitura, categorização e resposta por email.
_DEFAULT_MINUTES_SAVED_PER_ANALYSIS = 2.5
# Custo médio hora/operador de atendimento financeiro (BRL)
_DEFAULT_HOURLY_OPERATOR_RATE_BRL = 45.0


@api_v1_bp.route("/stats", methods=["GET"])
@jwt_required()
def get_stats():
    """
    Retorna métricas agregadas, ROI corporativo e quebras de análise para o dashboard.
    """
    try:
        from backend.app.utils.tenant_context import get_current_tenant_id

        tenant_id = get_current_tenant_id()

        # Parâmetros de ROI configuráveis via query params
        hourly_rate = request.args.get(
            "hourly_rate", default=_DEFAULT_HOURLY_OPERATOR_RATE_BRL, type=float
        )
        minutes_saved = request.args.get(
            "minutes_saved", default=_DEFAULT_MINUTES_SAVED_PER_ANALYSIS, type=float
        )

        # Base query
        base_query = EmailAnalysis.query.filter_by(is_deleted=False)
        if tenant_id is not None:
            base_query = base_query.filter_by(tenant_id=tenant_id)

        total = base_query.count()

        # Contagens por categoria padrão
        productive = base_query.filter_by(category="Produtivo").count()
        unproductive = base_query.filter_by(category="Improdutivo").count()

        # Quarentena
        quarantined_count = base_query.filter_by(in_quarantine=True).count()
        quarantine_percentage = round((quarantined_count / total) * 100, 1) if total > 0 else 0.0

        # Quebra por Categoria dinâmica
        category_query = db.session.query(
            EmailAnalysis.category, func.count(EmailAnalysis.id)
        ).filter(EmailAnalysis.is_deleted.is_(False))
        if tenant_id is not None:
            category_query = category_query.filter(EmailAnalysis.tenant_id == tenant_id)
        category_counts = dict(category_query.group_by(EmailAnalysis.category).all())

        # Quebra por Sentimento
        sentiment_query = db.session.query(
            EmailAnalysis.sentiment, func.count(EmailAnalysis.id)
        ).filter(EmailAnalysis.is_deleted.is_(False), EmailAnalysis.sentiment.isnot(None))
        if tenant_id is not None:
            sentiment_query = sentiment_query.filter(EmailAnalysis.tenant_id == tenant_id)
        sentiment_breakdown = dict(sentiment_query.group_by(EmailAnalysis.sentiment).all())

        # Quebra por Urgência
        urgency_query = db.session.query(
            EmailAnalysis.urgency, func.count(EmailAnalysis.id)
        ).filter(EmailAnalysis.is_deleted.is_(False), EmailAnalysis.urgency.isnot(None))
        if tenant_id is not None:
            urgency_query = urgency_query.filter(EmailAnalysis.tenant_id == tenant_id)
        urgency_breakdown = dict(urgency_query.group_by(EmailAnalysis.urgency).all())

        # Tempo médio de processamento (em ms)
        avg_query = db.session.query(func.avg(EmailAnalysis.processing_time_ms)).filter(
            EmailAnalysis.is_deleted.is_(False),
            EmailAnalysis.processing_time_ms.isnot(None),
        )
        if tenant_id is not None:
            avg_query = avg_query.filter(EmailAnalysis.tenant_id == tenant_id)
        avg_time_result = avg_query.scalar()
        avg_processing_time_ms = round(float(avg_time_result), 1) if avg_time_result else 0

        # Análises em cache
        cached_subquery = db.session.query(EmailAnalysis.content_hash).filter(
            EmailAnalysis.is_deleted.is_(False)
        )
        if tenant_id is not None:
            cached_subquery = cached_subquery.filter(EmailAnalysis.tenant_id == tenant_id)
        cached_subquery = cached_subquery.group_by(EmailAnalysis.content_hash).having(
            func.count(EmailAnalysis.id) > 1
        )
        cached_count = cached_subquery.count()

        # Feedbacks e acurácia
        feedback_query = AnalysisFeedback.query.filter_by(is_deleted=False)
        if tenant_id is not None:
            feedback_query = feedback_query.filter_by(tenant_id=tenant_id)
        total_feedbacks = feedback_query.count()
        approved_count = feedback_query.filter_by(approved=True).count()
        corrections_count = feedback_query.filter_by(approved=False).count()

        accuracy_rate = (
            round((approved_count / total_feedbacks) * 100, 1) if total_feedbacks > 0 else 100.0
        )

        # ROI Corporativo
        time_saved_hours = round((total * minutes_saved) / 60.0, 1)
        estimated_savings_brl = round(time_saved_hours * hourly_rate, 2)

        stats = {
            "total_analyses": total,
            "productive_count": productive,
            "unproductive_count": unproductive,
            "productive_percentage": round((productive / total) * 100, 1) if total > 0 else 0,
            "unproductive_percentage": round((unproductive / total) * 100, 1) if total > 0 else 0,
            "quarantined_count": quarantined_count,
            "quarantine_percentage": quarantine_percentage,
            "avg_processing_time_ms": avg_processing_time_ms,
            "cached_count": cached_count,
            "total_feedbacks": total_feedbacks,
            "approved_count": approved_count,
            "corrections_count": corrections_count,
            "accuracy_rate": accuracy_rate,
            "time_saved_estimate_hours": time_saved_hours,
            "estimated_savings_brl": estimated_savings_brl,
            "category_breakdown": category_counts,
            "sentiment_breakdown": sentiment_breakdown,
            "urgency_breakdown": urgency_breakdown,
        }

        return jsonify(stats), 200

    except Exception as e:
        logger.exception(f"Error computing stats: {e}")
        return jsonify({"error": "Failed to compute stats"}), 500
