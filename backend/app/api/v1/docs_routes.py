"""
Swagger UI e documentação OpenAPI 3.0 para a API v1.
"""
from typing import Any, Dict
from flask import Blueprint, jsonify, render_template_string

docs_bp = Blueprint("docs", __name__)

OPENAPI_SPEC: Dict[str, Any] = {
    "openapi": "3.0.3",
    "info": {
        "title": "Email Analyzer Enterprise API",
        "description": (
            "API de alto desempenho para triagem inteligente de emails, extração de entidades financeiras (NER), "
            "detecção de fraude, roteamento/SLA automatizado, múltiplos tons de resposta e compliance LGPD."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "Pedro Pompeu / AutoU Case",
            "url": "https://github.com/pedropompeu/autou-case-analisador-email",
        },
    },
    "servers": [
        {"url": "/api/v1", "description": "API v1 Base Endpoint"},
        {"url": "/", "description": "Root Server"},
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Insira o token JWT no formato: Bearer <seu_token>",
            },
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-Key",
                "description": "Chave de API B2B para integrações diretas",
            },
        },
        "schemas": {
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Bad Request"},
                    "message": {"type": "string", "example": "Campo 'text' é obrigatório."},
                },
            },
            "AuthRegisterRequest": {
                "type": "object",
                "required": ["username", "email", "password"],
                "properties": {
                    "username": {"type": "string", "example": "operador1"},
                    "email": {"type": "string", "format": "email", "example": "operador@empresa.com"},
                    "password": {"type": "string", "format": "password", "example": "SenhaForte123!"},
                    "role": {"type": "string", "enum": ["viewer", "operator", "manager", "admin"], "default": "operator"},
                    "tenant_id": {"type": "string", "example": "default"},
                },
            },
            "AuthLoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email", "example": "operador@empresa.com"},
                    "password": {"type": "string", "format": "password", "example": "SenhaForte123!"},
                },
            },
            "AuthTokenResponse": {
                "type": "object",
                "properties": {
                    "access_token": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsIn..."},
                    "refresh_token": {"type": "string", "example": "eyJhbGciOiJIUzI1NiIsIn..."},
                    "user": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "example": 1},
                            "username": {"type": "string", "example": "operador1"},
                            "email": {"type": "string", "example": "operador@empresa.com"},
                            "role": {"type": "string", "example": "operator"},
                            "tenant_id": {"type": "string", "example": "default"},
                        },
                    },
                },
            },
            "EmailAnalysisRequest": {
                "type": "object",
                "required": ["text"],
                "properties": {
                    "text": {"type": "string", "description": "Texto completo do email a ser analisado", "example": "Prezados, favor enviar a 2ª via do boleto vencido no valor de R$ 1.250,00 referente ao contrato 99281."},
                    "tone": {"type": "string", "enum": ["formal", "empatico", "negociacao", "juridico", "direto"], "default": "formal"},
                },
            },
            "EntityExtraction": {
                "type": "object",
                "properties": {
                    "monetary_values": {"type": "array", "items": {"type": "string"}, "example": ["R$ 1.250,00"]},
                    "due_dates": {"type": "array", "items": {"type": "string"}, "example": ["2026-10-15"]},
                    "contract_numbers": {"type": "array", "items": {"type": "string"}, "example": ["99281"]},
                    "cpf_cnpj": {"type": "array", "items": {"type": "string"}, "example": ["123.456.789-00"]},
                },
            },
            "EmailAnalysisResponse": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 104},
                    "category": {"type": "string", "example": "Segunda via de boleto"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"], "example": "high"},
                    "urgency": {"type": "string", "enum": ["baixa", "media", "alta", "critica"], "example": "alta"},
                    "sentiment": {"type": "string", "enum": ["positivo", "neutro", "negativo", "irritado"], "example": "neutro"},
                    "confidence_score": {"type": "number", "format": "float", "example": 0.94},
                    "fraud_score": {"type": "number", "format": "float", "example": 0.05},
                    "is_quarantined": {"type": "boolean", "example": False},
                    "quarantine_reason": {"type": "string", "nullable": True, "example": None},
                    "entities": {"$ref": "#/components/schemas/EntityExtraction"},
                    "suggested_reply": {"type": "string", "example": "Olá, recebemos sua solicitação e estamos gerando a 2ª via atualizada do seu boleto."},
                    "status": {"type": "string", "enum": ["pending", "in_review", "approved", "rejected", "quarantined", "closed"], "example": "pending"},
                    "created_at": {"type": "string", "format": "date-time", "example": "2026-09-19T15:00:00Z"},
                },
            },
            "RegenerateToneRequest": {
                "type": "object",
                "required": ["tone"],
                "properties": {
                    "tone": {"type": "string", "enum": ["formal", "empatico", "negociacao", "juridico", "direto"], "example": "empatico"},
                },
            },
            "UpdateStatusRequest": {
                "type": "object",
                "required": ["status"],
                "properties": {
                    "status": {"type": "string", "enum": ["pending", "in_review", "approved", "rejected", "quarantined", "closed"], "example": "approved"},
                },
            },
            "AssignOperatorRequest": {
                "type": "object",
                "required": ["assigned_to_user_id"],
                "properties": {
                    "assigned_to_user_id": {"type": "integer", "example": 2},
                },
            },
            "InternalNoteRequest": {
                "type": "object",
                "required": ["note"],
                "properties": {
                    "note": {"type": "string", "example": "Cliente VIP. Priorizar atendimento via canal prioritário."},
                },
            },
            "RoutingRuleRequest": {
                "type": "object",
                "required": ["name", "field", "operator", "value", "action"],
                "properties": {
                    "name": {"type": "string", "example": "Escalar emails de cancelamento"},
                    "field": {"type": "string", "enum": ["category", "urgency", "sentiment", "fraud_score", "confidence_score"], "example": "category"},
                    "operator": {"type": "string", "enum": ["equals", "contains", "greater_than", "less_than"], "example": "equals"},
                    "value": {"type": "string", "example": "Cancelamento"},
                    "action": {"type": "string", "enum": ["set_priority_critical", "quarantine", "assign_manager"], "example": "set_priority_critical"},
                    "priority": {"type": "integer", "default": 10, "example": 10},
                },
            },
            "WebhookCreateRequest": {
                "type": "object",
                "required": ["url", "events"],
                "properties": {
                    "url": {"type": "string", "format": "uri", "example": "https://meu-erp.com/webhooks/autou"},
                    "events": {"type": "array", "items": {"type": "string"}, "example": ["analysis.completed", "quarantine.flagged"]},
                    "secret": {"type": "string", "example": "whsec_supersecreta123"},
                },
            },
            "ApiKeyCreateRequest": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "example": "Integração Salesforce B2B"},
                },
            },
            "LgpdSubjectRequest": {
                "type": "object",
                "required": ["identifier"],
                "properties": {
                    "identifier": {"type": "string", "description": "Email, CPF ou documento do titular", "example": "cliente@email.com"},
                },
            },
            "RoiResponse": {
                "type": "object",
                "properties": {
                    "total_processed": {"type": "integer", "example": 1420},
                    "hours_saved": {"type": "number", "format": "float", "example": 118.3},
                    "financial_savings_brl": {"type": "number", "format": "float", "example": 5915.0},
                    "accuracy_rate": {"type": "number", "format": "float", "example": 0.96},
                    "quarantine_rate": {"type": "number", "format": "float", "example": 0.03},
                },
            },
        },
    },
    "paths": {
        "/auth/register": {
            "post": {
                "tags": ["Autenticação & RBAC"],
                "summary": "Cadastrar novo usuário",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthRegisterRequest"}}},
                },
                "responses": {
                    "201": {"description": "Usuário criado com sucesso"},
                    "400": {"description": "Erro de validação ou email duplicado"},
                },
            },
        },
        "/auth/login": {
            "post": {
                "tags": ["Autenticação & RBAC"],
                "summary": "Autenticar usuário e obter tokens JWT",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthLoginRequest"}}},
                },
                "responses": {
                    "200": {
                        "description": "Login bem-sucedido",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthTokenResponse"}}},
                    },
                    "401": {"description": "Credenciais inválidas"},
                },
            },
        },
        "/auth/refresh": {
            "post": {
                "tags": ["Autenticação & RBAC"],
                "summary": "Renovar Access Token usando Refresh Token",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Token renovado com sucesso"},
                    "401": {"description": "Refresh token expirado ou inválido"},
                },
            },
        },
        "/auth/logout": {
            "post": {
                "tags": ["Autenticação & RBAC"],
                "summary": "Revogar token JWT ativo (logout)",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Sessão encerrada e token revogado"},
                },
            },
        },
        "/auth/me": {
            "get": {
                "tags": ["Autenticação & RBAC"],
                "summary": "Obter perfil do usuário autenticado",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Dados do usuário e permissões de tenant"},
                    "401": {"description": "Não autorizado"},
                },
            },
        },
        "/analyze": {
            "post": {
                "tags": ["Triagem de Emails & IA"],
                "summary": "Analisar email com IA de forma síncrona (NER, Sentimento, Fraude, Tons)",
                "security": [{"BearerAuth": []}, {"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EmailAnalysisRequest"}}},
                },
                "responses": {
                    "200": {
                        "description": "Análise concluída",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EmailAnalysisResponse"}}},
                    },
                    "400": {"description": "Requisição inválida"},
                    "429": {"description": "Rate limit excedido"},
                },
            },
        },
        "/analyze-async": {
            "post": {
                "tags": ["Triagem de Emails & IA"],
                "summary": "Enfileirar análise assíncrona de email via Celery",
                "security": [{"BearerAuth": []}, {"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EmailAnalysisRequest"}}},
                },
                "responses": {
                    "202": {"description": "Tarefa enfileirada com task_id"},
                },
            },
        },
        "/analyze-with-file": {
            "post": {
                "tags": ["Triagem de Emails & IA"],
                "summary": "Analisar email com anexo (PDF ou TXT)",
                "security": [{"BearerAuth": []}, {"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "file": {"type": "string", "format": "binary"},
                                    "tone": {"type": "string", "enum": ["formal", "empatico", "negociacao", "juridico", "direto"]},
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "200": {"description": "Análise do email e texto extraído do anexo"},
                },
            },
        },
        "/emails/ingest-eml": {
            "post": {
                "tags": ["Triagem de Emails & IA"],
                "summary": "Ingerir e processar arquivo .eml bruto (RFC 822)",
                "security": [{"BearerAuth": []}, {"ApiKeyAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "file": {"type": "string", "format": "binary"},
                                },
                            },
                        },
                    },
                },
                "responses": {
                    "200": {"description": "Email EML processado com sucesso"},
                },
            },
        },
        "/emails/{id}/regenerate-tone": {
            "post": {
                "tags": ["Triagem de Emails & IA"],
                "summary": "Regenerar resposta sugerida em tom específico",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RegenerateToneRequest"}}},
                },
                "responses": {
                    "200": {"description": "Resposta sugerida regenerada"},
                },
            },
        },
        "/emails/{id}/status": {
            "patch": {
                "tags": ["Workflows & SLA"],
                "summary": "Atualizar status de triagem do email",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UpdateStatusRequest"}}},
                },
                "responses": {
                    "200": {"description": "Status atualizado"},
                },
            },
        },
        "/emails/{id}/assign": {
            "patch": {
                "tags": ["Workflows & SLA"],
                "summary": "Atribuir email para um operador responsável",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AssignOperatorRequest"}}},
                },
                "responses": {
                    "200": {"description": "Email atribuído ao operador"},
                },
            },
        },
        "/emails/{id}/notes": {
            "get": {
                "tags": ["Workflows & SLA"],
                "summary": "Listar notas internas da thread",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {
                    "200": {"description": "Lista de notas internas em ordem cronológica"},
                },
            },
            "post": {
                "tags": ["Workflows & SLA"],
                "summary": "Adicionar nota interna na thread",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/InternalNoteRequest"}}},
                },
                "responses": {
                    "201": {"description": "Nota interna adicionada com sucesso"},
                },
            },
        },
        "/admin/rules": {
            "get": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Listar regras de roteamento e SLA configuradas",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Lista de regras ativas"},
                },
            },
            "post": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Criar nova regra de roteamento / escalonamento",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RoutingRuleRequest"}}},
                },
                "responses": {
                    "201": {"description": "Regra cadastrada com sucesso"},
                },
            },
        },
        "/admin/rules/{id}": {
            "delete": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Excluir regra de roteamento",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {
                    "200": {"description": "Regra removida"},
                },
            },
        },
        "/admin/categories": {
            "get": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Listar categorias dinâmicas do tenant",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Lista de categorias ativas"},
                },
            },
            "post": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Adicionar nova categoria personalizada",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "201": {"description": "Categoria cadastrada"},
                },
            },
        },
        "/admin/api-keys": {
            "get": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Listar API Keys corporativas",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Lista de chaves de API com metadados"},
                },
            },
            "post": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Gerar nova API Key B2B",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ApiKeyCreateRequest"}}},
                },
                "responses": {
                    "201": {"description": "Chave gerada (exibida apenas uma vez)"},
                },
            },
        },
        "/admin/api-keys/{id}": {
            "delete": {
                "tags": ["Regras & Automação SLA"],
                "summary": "Revogar API Key",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {
                    "200": {"description": "Chave revogada com sucesso"},
                },
            },
        },
        "/webhooks": {
            "get": {
                "tags": ["Webhooks & Eventos"],
                "summary": "Listar webhooks registrados",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Lista de endpoints e eventos inscritos"},
                },
            },
            "post": {
                "tags": ["Webhooks & Eventos"],
                "summary": "Registrar endpoint para recebimento de webhooks com assinatura HMAC",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/WebhookCreateRequest"}}},
                },
                "responses": {
                    "201": {"description": "Webhook cadastrado"},
                },
            },
        },
        "/webhooks/{id}": {
            "delete": {
                "tags": ["Webhooks & Eventos"],
                "summary": "Remover endpoint de webhook",
                "security": [{"BearerAuth": []}],
                "parameters": [
                    {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}},
                ],
                "responses": {
                    "200": {"description": "Webhook removido"},
                },
            },
        },
        "/compliance/export": {
            "post": {
                "tags": ["Compliance LGPD & Governança"],
                "summary": "Exportar relatório de dados do titular (LGPD Art. 19)",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LgpdSubjectRequest"}}},
                },
                "responses": {
                    "200": {"description": "Dados exportados com hash de auditoria"},
                },
            },
        },
        "/compliance/forget": {
            "post": {
                "tags": ["Compliance LGPD & Governança"],
                "summary": "Direito ao Esquecimento / Anonimização irreversível (LGPD Art. 18)",
                "security": [{"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LgpdSubjectRequest"}}},
                },
                "responses": {
                    "200": {"description": "Registros anonimizados irreversivelmente"},
                },
            },
        },
        "/compliance/purge": {
            "post": {
                "tags": ["Compliance LGPD & Governança"],
                "summary": "Executar expurgo periódico por retenção de dados",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Expurgo de registros antigos executado"},
                },
            },
        },
        "/stats/roi": {
            "get": {
                "tags": ["Analytics & ROI"],
                "summary": "Calcular métricas de ROI financeiro e horas economizadas",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {
                        "description": "Métricas de ROI calculadas",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RoiResponse"}}},
                    },
                },
            },
        },
        "/stats": {
            "get": {
                "tags": ["Analytics & ROI"],
                "summary": "Estatísticas agregadas de triagem e sentimentos",
                "security": [{"BearerAuth": []}],
                "responses": {
                    "200": {"description": "Estatísticas agregadas"},
                },
            },
        },
        "/health": {
            "get": {
                "tags": ["Observabilidade & Saúde"],
                "summary": "Health check detalhado de dependências (PostgreSQL, Redis)",
                "responses": {
                    "200": {"description": "Sistema saudável"},
                    "503": {"description": "Degradação em dependências críticas"},
                },
            },
        },
        "/status": {
            "get": {
                "tags": ["Observabilidade & Saúde"],
                "summary": "Informações gerais da API e versão",
                "responses": {
                    "200": {"description": "Metadados do serviço"},
                },
            },
        },
    },
}

SWAGGER_UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Documentação OpenAPI — Email Analyzer</title>
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/favicon-32x32.png" sizes="32x32" />
  <style>
    body {
      margin: 0;
      background: #0f172a;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }
    .topbar { display: none !important; }
    .swagger-ui .info .title {
      color: #38bdf8 !important;
      font-size: 28px;
    }
    .swagger-ui .info p, .swagger-ui .info li {
      color: #94a3b8 !important;
    }
    .swagger-ui .scheme-container {
      background: #1e293b !important;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
      padding: 16px !important;
      border-radius: 8px;
      margin-bottom: 20px;
    }
    .swagger-ui .opblock {
      border-radius: 8px !important;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
      margin-bottom: 12px !important;
    }
    .swagger-ui .opblock-tag {
      color: #e2e8f0 !important;
      border-bottom: 1px solid #334155 !important;
    }
    .swagger-ui section.models {
      border-radius: 8px;
      background: #1e293b;
      border: 1px solid #334155;
    }
    .swagger-ui section.models h4 {
      color: #cbd5e1;
    }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
  <script>
    window.onload = function() {
      window.ui = SwaggerUIBundle({
        url: "{{ spec_url }}",
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "BaseLayout"
      });
    };
  </script>
</body>
</html>
"""


@docs_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    """Retorna a especificação OpenAPI 3.0 completa em JSON."""
    return jsonify(OPENAPI_SPEC)


@docs_bp.route("/docs", methods=["GET"])
def swagger_ui():
    """Renderiza a interface interativa Swagger UI."""
    return render_template_string(SWAGGER_UI_TEMPLATE, spec_url="/api/v1/openapi.json")
