<div align="center">
<img src="https://notion-emojis.s3-us-west-2.amazonaws.com/prod/svg-twitter/1f680.svg" alt="Foguete" width="100">
<h1>Analisador de Emails com IA — AutoU</h1>
<p>Aplicação web que utiliza a API do Google Gemini para classificar emails e sugerir respostas automaticamente.</p>
<p>
<img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python 3.11+">
<img src="https://img.shields.io/badge/Flask-3.0-black.svg" alt="Flask 3.0">
<img src="https://img.shields.io/badge/React-19-61DAFB.svg" alt="React 19">
<img src="https://img.shields.io/badge/Gemini-2.0--flash-orange.svg" alt="Gemini">
</p>
</div>

## 🚀 Demo

- **Online:** [analisador-email.onrender.com](https://analisador-email.onrender.com)
- **Vídeo:** [YouTube](https://youtu.be/SMAO35yRlm8)

## 📋 Sobre

Solução para o desafio da AutoU: otimizar a gestão de emails numa empresa do setor financeiro. A IA classifica emails como **Produtivo** ou **Improdutivo** e gera sugestões de resposta, liberando tempo da equipe.

### Features

- 🤖 **Classificação por IA** — Google Gemini analisa conteúdo textual
- 💬 **Sugestão de respostas** — respostas automáticas contextuais
- 📎 **Upload de ficheiros** — suporte para `.txt` e `.pdf`
- 📊 **Dashboard de métricas** — análises totais, taxa de produtividade, tempo economizado
- 👤 **Feedback humano** — aprove ou corrija a classificação da IA (human-in-the-loop)
- 🌗 **Tema claro/escuro** — alternância com um clique
- 🔄 **Retry com backoff** — resiliência contra limites de taxa da API
- ⚡ **Processamento assíncrono** — análises em background via Celery

## 🛠️ Stack

| Camada | Tecnologias |
|---|---|
| **Frontend** | React 19, Vite, React Router, Axios |
| **Backend** | Python 3.11+, Flask 3.0, Gunicorn |
| **IA** | Google Gemini API (`google-genai` SDK) |
| **Banco de dados** | PostgreSQL 15, SQLAlchemy, Flask-Migrate |
| **Cache / Filas** | Redis 7, Celery |
| **Segurança** | Flask-JWT-Extended, Flask-Talisman, Flask-Limiter, Flask-CORS |
| **Observabilidade** | Sentry, Prometheus |
| **Infraestrutura** | Docker Compose, Nginx |

## ⚙️ Como Executar

### Com Docker (recomendado)

```bash
# 1. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY e SECRET_KEY

# 2. Build + inicie tudo (backend + frontend + PostgreSQL + Redis + Celery)
make init

# Backend API: http://localhost:5000/api/v1/
# Frontend:    http://localhost:3000
```

### Desenvolvimento local (sem Docker)

```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python wsgi.py  # http://localhost:5000

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev  # http://localhost:5173
```

### Comandos úteis (Makefile)

```bash
make help              # Lista todos os comandos
make test              # Executa testes (backend)
make test-cov          # Testes com cobertura
make lint              # Linting (flake8 + mypy)
make format            # Formata código (black + isort)
make frontend-install  # Instala deps do frontend
make frontend-dev      # Dev server do frontend
make frontend-build    # Build de produção do frontend
make docker-up         # Inicia containers
make docker-down       # Para containers
make docker-logs       # Logs dos containers
make migrate           # Executa migrações do banco
```

## 🏗️ Estrutura do Projeto

```
autou-case/
├── frontend/                    # React SPA (Vite)
│   ├── Dockerfile               # Multi-stage: Node → Nginx
│   ├── nginx.conf               # Proxy reverso para API
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── api/client.js        # Axios com interceptors JWT
│       ├── pages/
│       │   ├── EmailAnalyzer.jsx
│       │   ├── Dashboard.jsx
│       │   └── Login.jsx
│       ├── components/Navbar.jsx
│       └── styles/App.css
├── backend/                     # Flask API (headless)
│   ├── config.py                # Configuração multi-ambiente
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── api/v1/              # API REST versionada
│   │   │   ├── email_routes.py  # Análise de email
│   │   │   ├── stats_routes.py  # Métricas do dashboard
│   │   │   ├── feedback_routes.py # Human-in-the-loop
│   │   │   ├── auth_routes.py   # Autenticação JWT
│   │   │   └── health_routes.py # Health check
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/       # Repository pattern
│   │   ├── services/           # Lógica de negócio + LLM providers
│   │   └── utils/              # File processor, cache
│   ├── migrations/              # Alembic migrations
│   └── tests/                   # Testes (unit + integration)
├── docker-compose.yml           # Orquestração (5 serviços)
├── Dockerfile.backend           # Imagem Docker do backend
├── Makefile                     # Comandos utilitários
├── context/                     # Memória de projeto (para IAs)
└── fontes/                      # Fontes brutas auditáveis
```

## 🔌 API Endpoints

### Autenticação

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Registrar novo usuário |
| `POST` | `/api/v1/auth/login` | Login (retorna JWT) |
| `GET` | `/api/v1/auth/me` | Dados do usuário autenticado |

### Análise de Emails (JWT obrigatório)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/analyze` | Analisa email (JSON) |
| `POST` | `/api/v1/analyze-with-file` | Analisa email com ficheiro |
| `GET` | `/api/v1/tasks/<id>` | Status de tarefa assíncrona |

### Dashboard e Feedback (JWT obrigatório)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/stats` | Métricas agregadas |
| `POST` | `/api/v1/feedback` | Feedback sobre classificação |

### Infraestrutura

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/health` | Health check detalhado |
| `GET` | `/health` | Health check (load balancer) |

## 🤔 Decisões Técnicas

- **Gemini vs. NLP Tradicional:** LLMs modernos entendem contexto e semântica sem pré-processamento manual.
- **Monorepo (frontend + backend):** Simplifica CI/CD e compartilha configs (Docker Compose, .env).
- **Backend headless:** API pura `/api/v1/*` — frontend React desacoplado consome via Axios.
- **Human-in-the-loop:** Feedback do usuário armazenado para métricas e eventual fine-tuning.
- **LLM Provider abstrato:** Interface que permite trocar Gemini por OpenAI/Claude sem alterar lógica de negócio.
- **Cache por hash SHA-256:** Emails idênticos servidos do banco sem chamar a API novamente.