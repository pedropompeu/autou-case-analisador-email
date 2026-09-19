"""
Schemas de validação usando Marshmallow.
"""
from marshmallow import Schema, fields, validate, ValidationError


class EmailAnalysisRequestSchema(Schema):
    """Schema para validar requisição de análise de email."""

    text = fields.Str(
        required=True,
        validate=validate.Length(min=10, max=10000),
        error_messages={
            "required": "Email text is required",
            "invalid": "Email text must be a string",
        },
    )

    thread_id = fields.Str(load_default=None, validate=validate.Length(max=100))
    tone = fields.Str(
        load_default="formal",
        validate=validate.OneOf(["formal", "empatico", "negociacao", "juridico", "direto"]),
    )

    language = fields.Str(
        load_default="pt",
        validate=validate.OneOf(["pt", "en", "es"]),
    )

    store_in_db = fields.Bool(load_default=True)
    async_mode = fields.Bool(load_default=False, data_key="async")


class EmailAnalysisResponseSchema(Schema):
    """Schema para resposta de análise com inteligência da Fase 1."""

    id = fields.Int(allow_none=True)
    categoria = fields.Str(required=True)
    subcategoria = fields.Str(allow_none=True)
    resumo = fields.Str(required=True)
    sugestao_resposta = fields.Str(required=True)
    sentimento = fields.Str(dump_default="Neutro")
    urgencia = fields.Str(dump_default="Media")
    score_confianca = fields.Float(dump_default=1.0)
    in_quarantine = fields.Bool(dump_default=False)
    risco_fraude = fields.Float(dump_default=0.0)
    indicios_fraude = fields.List(fields.Str(), dump_default=list)
    entidades = fields.Dict(dump_default=dict)
    tone = fields.Str(dump_default="formal")
    pii_masked = fields.Bool(dump_default=False)
    cached = fields.Bool(dump_default=False)


class TaskStatusResponseSchema(Schema):
    """Schema para resposta de status de tarefa assíncrona."""

    task_id = fields.Str(required=True)
    status = fields.Str(required=True)  # PENDING, STARTED, SUCCESS, FAILURE
    result = fields.Dict(required=False, allow_none=True)
    error = fields.Str(required=False, allow_none=True)


class ErrorResponseSchema(Schema):
    """Schema para respostas de erro."""

    error = fields.Str(required=True)
    message = fields.Str(required=False)
    details = fields.Dict(required=False)


class FeedbackRequestSchema(Schema):
    """Schema para validar requisição de feedback (human-in-the-loop)."""

    analysis_id = fields.Int(
        required=True,
        error_messages={"required": "analysis_id is required"},
    )
    approved = fields.Bool(
        required=True,
        error_messages={"required": "approved is required"},
    )
    corrected_category = fields.Str(
        load_default=None,
        validate=validate.OneOf(["Produtivo", "Improdutivo"]),
    )
    corrected_summary = fields.Str(load_default=None)
    notes = fields.Str(load_default=None, validate=validate.Length(max=2000))


class StatsResponseSchema(Schema):
    """Schema para resposta de métricas agregadas."""

    total_analyses = fields.Int(required=True)
    productive_count = fields.Int(required=True)
    unproductive_count = fields.Int(required=True)
    productive_percentage = fields.Float(required=True)
    unproductive_percentage = fields.Float(required=True)
    avg_processing_time_ms = fields.Float(required=True)
    cached_count = fields.Int(required=True)
    total_feedbacks = fields.Int(required=True)
    corrections_count = fields.Int(required=True)
    time_saved_estimate_hours = fields.Float(required=True)

