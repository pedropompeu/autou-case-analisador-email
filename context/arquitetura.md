---
tipo: contexto
projeto: memoria-de-projeto
descricao: Stack e o mapa da estrutura do projeto verificado por leitura em disco.
estado: estavel
criado: 2026-09-12
relacionado:
  - context/achados.md
---

# Arquitetura

> Documentação técnica da estrutura do repositório, validada diretamente contra os arquivos em disco.

## Baseline declarada vs. verificada {#baseline}

- [2026-09-12] (e) ← `lint.py` Estrutura de memória validada pelo linter local sem erros.
- [2026-09-18] (i) Reestruturação profunda: remoção de ~35 arquivos redundantes/obsoletos, consolidação de docs em README.md único.

| Componente | Declarado | Verificado? | Real |
|---|---|---|---|
| Módulos de Contexto | `context/` | ✅ | 4 arquivos centrais (`index`, `arquitetura`, `achados`, `decisoes`) + `discussoes/` |
| Camada de Fontes Brutas | `fontes/` | ✅ | `fontes/index.md` presente e preparado |
| Script de Verificação | `lint.py` | ✅ | Operacional com Python 3 |
| Backend Flask | `backend/` | ✅ | App factory com blueprints, services, repositories, models |
| Frontend React | `frontend/` | ✅ | SPA Vite 5 + React 19, servido por Nginx; consome exclusivamente `/api/v1/*` |
| Migrations | `backend/migrations/versions/` | ✅ | 0001_initial_schema: users, email_analyses, analysis_feedbacks |
| Infraestrutura | Docker/Compose | ✅ | `Dockerfile.backend` + `frontend/Dockerfile` + `docker-compose.yml` (5 serviços) |

## Stack {#stack}

- [2026-09-12] (e) ← `lint.py` Python 3 para script de linting e validação de consistência.
- [2026-09-12] (e) ← `context/index.md` Documentação estruturada em Markdown puro com convenções tipadas.
- [2026-09-18] (e) ← `requirements.txt` Backend: Flask 3.0, SQLAlchemy 2.0, Celery 5.3, Redis 5.0, google-genai, pypdf.
- [2026-09-18] (e) ← `backend/app/services/gemini_provider.py` IA: Google Gemini 2.0 Flash via SDK `google-genai` com retry exponencial + jitter.
- [2026-09-18] (e) ← `templates/index.html` Frontend legado: Bootstrap 5.3, JavaScript vanilla, tema claro/escuro.
- [2026-09-19] (e) ← `frontend/package.json` Frontend React: Vite 5, React 19, React Router v7, Axios.

## O mapa {#mapa}

| Área | Onde mora | O que faz | Risco conhecido |
|---|---|---|---|
| Roteamento IA | `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` | Roteamento rápido para IAs em toda sessão | → [[achados#formato]] |
| Conhecimento | `context/` | Memória destilada consultada sob demanda | Risco de desatualização se linter não for executado |
| Camada Bruta | `fontes/` | Arquivos imutáveis de entrada externa | Risco de perda de rastreabilidade se editado diretamente |
| Linter | `lint.py` | Valida sintaxe, links, âncoras e procedência | N/A |
| App Factory | `backend/app/__init__.py` | Cria e configura a aplicação Flask | N/A |
| Config | `backend/config.py` | Configuração multi-ambiente (dev/test/prod) | N/A |
| API Legacy | `backend/app/api/legacy/` | Rotas do frontend HTML (`/`, `/processar-email`) | N/A |
| API v1 | `backend/app/api/v1/` | API REST versionada com JWT, rate limit, schemas | N/A |
| Services | `backend/app/services/` | Lógica de negócio, LLM providers (abstrato + Gemini + Mock) | N/A |
| Models | `backend/app/models/` | SQLAlchemy models (EmailAnalysis, AnalysisFeedback, User, BaseModel) | N/A |
| Repositories | `backend/app/repositories/` | Repository pattern para acesso a dados | N/A |
| Utils | `backend/app/utils/` | FileProcessor (txt/pdf), cache helpers | N/A |
| Middleware | `backend/app/middleware/` | Request logger (JSON estruturado) | N/A |
| Tasks | `backend/app/tasks.py` | Tarefas Celery (análise assíncrona) | N/A |
| Frontend legado | `templates/` + `static/` | HTML/CSS/JS servido pelo Flask | Mantido para compatibilidade |
| Frontend React | `frontend/` | SPA headless, rotas: `/`, `/dashboard`, `/login`, `/register` | N/A |
| Testes | `backend/tests/` | Unit + Integration tests com pytest | N/A |
| Entry Points | `wsgi.py`, `celery_worker.py` | Gunicorn WSGI + Celery worker | N/A |
| Infra | `docker-compose.yml`, `Dockerfile.backend` | PostgreSQL 15, Redis 7, Flask, Celery worker | N/A |

## Estado do código em disco {#disco}

- [2026-09-18] (i) Após reestruturação: removidos ~35 arquivos redundantes (docs gerados por IA, scripts shell duplicados, `app.py` obsoleto, lixo de pip, artefatos de build).
- [2026-09-18] (i) O `app.py` original da raiz (Flask simples com `google-generativeai` + `PyPDF2`) foi deletado. Toda a lógica real vive em `backend/` usando `google-genai` + `pypdf`.
- [2026-09-18] (i) README.md reescrito consolidando informações de ~20 documentos removidos.
- [2026-09-19] (i) Adicionados: `backend/app/models/feedback.py` (AnalysisFeedback), `backend/app/api/v1/feedback_routes.py`, `backend/app/api/v1/stats_routes.py`, schemas FeedbackRequestSchema + StatsResponseSchema.
- [2026-09-19] (i) Migration inicial criada: `backend/migrations/versions/0001_initial_schema.py` cobre users, email_analyses, analysis_feedbacks.
- [2026-09-19] (i) Frontend React criado em `frontend/`: Vite 5, React 19, React Router v7, Axios; páginas Login, Register, Analyze, Dashboard; Nginx proxy reverso para `/api/`.
- [2026-09-19] (i) Fase 0 Enterprise implementada: modelos `Tenant` (`models/tenant.py`) e `AuditLog` (`models/audit_log.py`), RBAC (`utils/rbac.py` com papéis admin/operator/viewer/auditor), PII Sanitizer (`utils/pii_sanitizer.py`), Criptografia At-Rest (`utils/crypto.py`), JWT Blocklist via Redis (`utils/jwt_blocklist.py`), blueprint administrativo `/api/v1/admin` e migration `b4c0bd8ae6f7_phase_0_multi_tenant_rbac_audit.py`.
- [2026-09-19] (i) Fase 1 Motor de IA implementada: `CustomCategory` (`models/category.py`), `FallbackLLMProvider` (`services/fallback_llm_provider.py`), extração de NER, sentimento, urgência, score de fraude, quarentena de baixa confiança, múltiplos tons de resposta (`/analyze/<id>/regenerate-response`), memória de thread e migration `c87e4445dd70_phase_1_advanced_ai_engine.py`.
- [2026-09-19] (i) Fase 2 Integrações Corporativas implementada: `WebhookSubscription` e `WebhookDelivery` (`models/webhook.py`), `WebhookService` (`services/webhook_service.py` com HMAC-SHA256), parser de email RFC822/MIME (`utils/email_parser.py`), rotas `/api/v1/webhooks` e `/api/v1/ingest/eml`, e migration `39030255bf15_phase_2_webhooks_and_ingestion.py`.
- [2026-09-19] (i) Fase 3 Compliance & Observabilidade implementada: `ComplianceService` (`services/compliance_service.py`) com Direito ao Esquecimento e Exportação LGPD, filtro DLP de saída (`utils/dlp_filter.py`), expurgo por retenção de dados, rotas `/api/v1/compliance/*` e dashboard avançado de ROI e distribuição em `/api/v1/stats`.
- [2026-09-19] (i) Fase 4 Workflows & Automação implementada: modelos `InternalNote` (`models/internal_note.py`) e `RoutingRule` (`models/routing_rule.py`), `RoutingEngineService` (`services/routing_engine_service.py`), rotas de notas, status e atribuição em `/api/v1/workflow_routes.py` e migration `d9e71ab523f1_phase_4_workflows_notes_rules.py`.

## Pontos de integração {#integracoes}

- [2026-09-12] (e) Ferramentas de IA suportadas nativamente: Claude Code CLI (`CLAUDE.md`), Antigravity / Gemini CLI (`GEMINI.md` e `AGENTS.md`).
- [2026-09-18] (e) ← `backend/app/services/llm_provider.py` Interface `LLMProvider` abstrata permite trocar entre Gemini, OpenAI, Claude etc.
- [2026-09-18] (e) ← `docker-compose.yml` Serviços: PostgreSQL 15, Redis 7, Flask backend, Celery worker.

