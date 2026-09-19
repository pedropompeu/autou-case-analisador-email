"""
Rotas legacy — Mantém compatibilidade com o frontend HTML/JS existente.

Nota: estas rotas são mantidas apenas para o frontend legado servido pelo
Flask. Novos clientes devem usar a API versionada em /api/v1/.
"""
import logging
from flask import render_template, request, jsonify, current_app

from backend.app.api.legacy import legacy_bp
from backend.app.services.email_analysis_service import EmailAnalysisService
from backend.app.services.llm_provider_factory import create_llm_provider
from backend.app.repositories.email_analysis_repository import EmailAnalysisRepository
from backend.app.utils.file_processor import FileProcessor

logger = logging.getLogger(__name__)


@legacy_bp.route("/")
def index():
    """Renderiza a página principal (frontend existente)."""
    return render_template("index.html")


@legacy_bp.route("/processar-email", methods=["POST"])
def processar_email():
    """
    Rota legacy - Mantém compatibilidade com o frontend existente.
    Processa email e retorna análise (formato original).
    """
    body_text = request.form.get("text", "").strip()
    attachment_text = ""

    # Processar arquivo anexo
    if "file" in request.files and request.files["file"].filename != "":
        file = request.files["file"]
        try:
            attachment_text = FileProcessor.process_file(file, file.filename)
            if attachment_text is None:
                return (
                    jsonify(
                        {
                            "error": "Formato de ficheiro não suportado. Use .txt ou .pdf."
                        }
                    ),
                    400,
                )
        except Exception as e:
            logger.error(f"Erro ao processar ficheiro: {e}")
            return (
                jsonify({"error": "Ocorreu um erro ao processar o ficheiro."}),
                500,
            )

    # Combinar texto do corpo e anexo
    full_email_text = body_text
    if attachment_text:
        full_email_text += f"\n\n--- CONTEÚDO DO ANEXO ---\n{attachment_text}"

    if not full_email_text.strip():
        return (
            jsonify({"error": "Nenhum texto ou ficheiro válido foi enviado."}),
            400,
        )

    # Usar o novo serviço enterprise
    try:
        service = EmailAnalysisService(
            llm_provider=create_llm_provider(),
            repository=EmailAnalysisRepository(),
        )

        result = service.analyze_email(full_email_text)

        # Verificar se houve erro
        if "error" in result:
            return jsonify(result), 503

        # Retornar no formato esperado pelo frontend
        return jsonify(result), 200

    except Exception as e:
        logger.exception(f"Erro ao processar email: {e}")
        return (
            jsonify({"error": "Ocorreu um erro ao comunicar com a IA."}),
            500,
        )
