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

    # Reservado para uso futuro. O prompt enviado ao LLM é atualmente fixo em
    # português (pt-BR) independentemente deste valor. Quando o suporte
    # multi-idioma for implementado, este campo controlará o idioma do prompt.
    language = fields.Str(
        load_default="pt",
        validate=validate.OneOf(["pt", "en", "es"]),
    )

    store_in_db = fields.Bool(load_default=True)
    async_mode = fields.Bool(load_default=False, data_key="async")


class EmailAnalysisResponseSchema(Schema):
    """Schema para resposta de análise."""

    categoria = fields.Str(required=True)
    resumo = fields.Str(required=True)
    sugestao_resposta = fields.Str(required=True)
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
