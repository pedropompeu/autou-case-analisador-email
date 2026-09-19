"""
Rotas de Ingestão de Canais e API Pública B2B (#23, #27).
Suporta ingestão direta de arquivos RFC822 / .eml e webhooks de caixas postais.
"""
import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from backend.app import limiter
from backend.app.repositories.email_analysis_repository import EmailAnalysisRepository
from backend.app.services.email_analysis_service import EmailAnalysisService
from backend.app.services.llm_provider_factory import create_llm_provider
from backend.app.services.webhook_service import WebhookService
from backend.app.utils.email_parser import parse_eml
from backend.app.utils.rbac import get_current_user
from backend.app.utils.tenant_context import get_current_tenant_id

logger = logging.getLogger(__name__)

ingest_bp = Blueprint("ingest", __name__)


def _get_analysis_service() -> EmailAnalysisService:
    return EmailAnalysisService(
        llm_provider=create_llm_provider(),
        repository=EmailAnalysisRepository(),
    )


@ingest_bp.route("/eml", methods=["POST"])
@jwt_required(optional=True)
@limiter.limit("30 per minute")
def ingest_eml():
    """
    Ingestão e análise automática de arquivo RFC822 (.eml) ou payload MIME bruto (#23).
    Autenticação suportada via JWT ou Header X-API-Key (B2B).
    """
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return (
            jsonify({"error": "Authentication required via JWT Bearer token or X-API-Key header"}),
            401,
        )

    user = get_current_user()
    user_id = user.id if user else None

    # 1. Obter conteúdo do arquivo .eml ou raw payload
    raw_content = None
    if "file" in request.files and request.files["file"].filename != "":
        raw_content = request.files["file"].read()
    elif request.data:
        raw_content = request.data
    else:
        return jsonify({"error": "No .eml file or raw MIME content provided"}), 400

    # 2. Parsear RFC822
    try:
        parsed_email = parse_eml(raw_content)
    except Exception as e:
        logger.error(f"Failed to parse EML: {e}")
        return jsonify({"error": "Failed to parse email message", "details": str(e)}), 400

    # 3. Analisar com o motor de IA
    tone = request.args.get("tone", "formal")
    service = _get_analysis_service()

    result = service.analyze_email(
        email_content=parsed_email["full_text"],
        store_in_db=True,
        tenant_id=tenant_id,
        user_id=user_id,
        thread_id=parsed_email.get("message_id") or None,
        tone=tone,
    )

    if "error" in result:
        return jsonify(result), 503

    # 4. Disparar webhooks de saída assíncronos configurados pelo tenant (#26)
    try:
        webhook_payload = {
            "analysis_id": result.get("id"),
            "subject": parsed_email["subject"],
            "from": parsed_email["from"],
            "to": parsed_email["to"],
            "category": result["categoria"],
            "urgency": result["urgencia"],
            "sentiment": result["sentimento"],
            "in_quarantine": result["in_quarantine"],
            "fraud_risk": result["risco_fraude"],
            "summary": result["resumo"],
            "suggested_response": result["sugestao_resposta"],
            "attachments_count": len(parsed_email["attachments"]),
        }
        WebhookService.dispatch_event(tenant_id, "email.analyzed", webhook_payload)

        if result.get("in_quarantine"):
            WebhookService.dispatch_event(tenant_id, "quarantine.flagged", webhook_payload)
    except Exception as e:
        logger.error(f"Error dispatching webhooks after EML ingestion: {e}")

    return (
        jsonify(
            {
                "message": "Email ingested and analyzed successfully",
                "email_metadata": {
                    "subject": parsed_email["subject"],
                    "from": parsed_email["from"],
                    "to": parsed_email["to"],
                    "date": parsed_email["date"],
                    "attachments": parsed_email["attachments"],
                },
                "analysis": result,
            }
        ),
        200,
    )
