"""
Rotas da API v1 para análise de emails.
"""
import io
import logging

import pypdf
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from backend.app import limiter
from backend.app.api.v1 import api_v1_bp
from backend.app.api.v1.schemas import EmailAnalysisRequestSchema
from backend.app.repositories.email_analysis_repository import EmailAnalysisRepository
from backend.app.services.email_analysis_service import EmailAnalysisService
from backend.app.services.llm_provider_factory import create_llm_provider
from backend.app.tasks import analyze_email_background
from backend.app.utils.rbac import get_current_user
from backend.app.utils.tenant_context import get_current_tenant_id

logger = logging.getLogger(__name__)

# Schema para validação de entrada
email_schema = EmailAnalysisRequestSchema()


def _get_analysis_service() -> EmailAnalysisService:
    """
    Cria EmailAnalysisService com suas dependências injetadas.
    Centralizado aqui para facilitar override em testes.
    """
    return EmailAnalysisService(
        llm_provider=create_llm_provider(),
        repository=EmailAnalysisRepository(),
    )


@api_v1_bp.route("/analyze", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def analyze_email():
    """
    Analisa um email usando IA.

    ---
    tags:
      - Email Analysis
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              description: Conteúdo do email a analisar
              minLength: 10
              maxLength: 10000
            language:
              type: string
              description: Idioma do email (reservado — prompt sempre em pt-BR)
              enum: [pt, en, es]
              default: pt
            store_in_db:
              type: boolean
              description: Se deve armazenar no banco de dados
              default: true
    responses:
      200:
        description: Análise realizada com sucesso
        schema:
          type: object
          properties:
            categoria:
              type: string
              enum: [Produtivo, Improdutivo]
            resumo:
              type: string
            sugestao_resposta:
              type: string
            cached:
              type: boolean
      400:
        description: Dados de entrada inválidos
      429:
        description: Rate limit excedido
      503:
        description: Serviço de IA indisponível
    """
    try:
        data = email_schema.load(request.get_json())
    except ValidationError as e:
        logger.warning(f"Validation error: {e.messages}")
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    email_text = data["text"]
    thread_id = data.get("thread_id")
    tone = data.get("tone", "formal")
    store_in_db = data.get("store_in_db", True)
    is_async = data.get("async_mode", False)

    user = get_current_user()
    tenant_id = get_current_tenant_id()
    user_id = user.id if user else None

    if is_async:
        task = analyze_email_background.delay(
            email_text, store_in_db=store_in_db, tenant_id=tenant_id, user_id=user_id
        )
        return (
            jsonify(
                {
                    "task_id": task.id,
                    "status": "ACCEPTED",
                    "message": "Analysis started in background",
                }
            ),
            202,
        )

    service = _get_analysis_service()
    result = service.analyze_email(
        email_text,
        store_in_db=store_in_db,
        tenant_id=tenant_id,
        user_id=user_id,
        thread_id=thread_id,
        tone=tone,
    )

    if "error" in result:
        return jsonify(result), 503

    return jsonify(result), 200


@api_v1_bp.route("/analyze/<int:analysis_id>/regenerate-response", methods=["POST"])
@jwt_required()
@limiter.limit("20 per minute")
def regenerate_response_tone(analysis_id):
    """
    Regenera a resposta sugerida com um novo tom comunicativo (#8).
    Tons disponíveis: formal, empatico, negociacao, juridico, direto.
    """
    data = request.get_json() or {}
    new_tone = data.get("tone", "formal")
    tenant_id = get_current_tenant_id()

    service = _get_analysis_service()
    result = service.regenerate_response(
        analysis_id=analysis_id, new_tone=new_tone, tenant_id=tenant_id
    )

    if "error" in result:
        return jsonify(result), 400 if result["error"] == "Analysis not found" else 503

    return jsonify(result), 200


@api_v1_bp.route("/categories", methods=["GET", "POST"])
@jwt_required()
def manage_categories():
    """
    GET: Lista as categorias customizadas do tenant ativo (#16).
    POST: Cria uma nova categoria dinâmica (Requer role Admin ou Operator).
    """
    from backend.app import db
    from backend.app.models.category import CustomCategory

    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return jsonify({"error": "No tenant context found"}), 400

    if request.method == "POST":
        data = request.get_json() or {}
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Category name is required"}), 400

        existing = CustomCategory.query.filter_by(tenant_id=tenant_id, name=name).first()
        if existing:
            return jsonify({"error": "Category already exists for this organization"}), 409

        cat = CustomCategory(
            tenant_id=tenant_id,
            name=name,
            description=data.get("description"),
            action_required=data.get("action_required", True),
        )
        db.session.add(cat)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Category created successfully",
                    "category": {
                        "id": cat.id,
                        "name": cat.name,
                        "action_required": cat.action_required,
                    },
                }
            ),
            201,
        )

    # GET
    categories = CustomCategory.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    return (
        jsonify(
            {
                "categories": [
                    {
                        "id": c.id,
                        "name": c.name,
                        "description": c.description,
                        "action_required": c.action_required,
                    }
                    for c in categories
                ]
            }
        ),
        200,
    )


@api_v1_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required()
def get_task_status(task_id):
    """
    Consulta o status de uma tarefa assíncrona.
    """
    from celery.result import AsyncResult

    result = AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.ready():
        if result.successful():
            response["result"] = result.result
        else:
            response["error"] = str(result.result)
            return jsonify(response), 500

    return jsonify(response), 200


@api_v1_bp.route("/analyze-with-file", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
def analyze_email_with_file():
    """
    Analisa email com suporte a upload de arquivo (.txt ou .pdf).

    ---
    tags:
      - Email Analysis
    consumes:
      - multipart/form-data
    parameters:
      - in: formData
        name: text
        type: string
        description: Texto do corpo do email
      - in: formData
        name: file
        type: file
        description: Arquivo anexo (.txt ou .pdf)
    responses:
      200:
        description: Análise realizada com sucesso
      400:
        description: Formato de arquivo não suportado ou conteúdo vazio
      413:
        description: Arquivo muito grande
      503:
        description: Serviço de IA indisponível
    """
    body_text = request.form.get("text", "").strip()
    attachment_text = ""

    # Processar arquivo anexo
    if "file" in request.files and request.files["file"].filename != "":
        file = request.files["file"]
        filename = file.filename.lower()

        try:
            if filename.endswith(".txt"):
                attachment_text = file.read().decode("utf-8")
            elif filename.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(io.BytesIO(file.read()))
                attachment_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
            else:
                return (
                    jsonify({"error": "Unsupported file format. Use .txt or .pdf files only."}),
                    400,
                )
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return jsonify({"error": "Failed to process uploaded file"}), 500

    # Combinar texto do corpo e anexo
    full_email_text = body_text
    if attachment_text:
        full_email_text += f"\n\n--- CONTEÚDO DO ANEXO ---\n{attachment_text}"

    if not full_email_text.strip():
        return jsonify({"error": "No valid text or file provided"}), 400

    if len(full_email_text) > 10000:
        return (
            jsonify({"error": "Email content too large (max 10000 characters)"}),
            400,
        )

    user = get_current_user()
    tenant_id = get_current_tenant_id()
    user_id = user.id if user else None

    service = _get_analysis_service()
    result = service.analyze_email(
        full_email_text,
        tenant_id=tenant_id,
        user_id=user_id,
    )

    if "error" in result:
        return jsonify(result), 503

    return jsonify(result), 200
