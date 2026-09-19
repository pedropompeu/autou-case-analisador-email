<div align="center">
<img src="https://notion-emojis.s3-us-west-2.amazonaws.com/prod/svg-twitter/1f680.svg" alt="Foguete" width="100">
<h1>Analisador de Emails com IA — AutoU</h1>
<p>Aplicação web que utiliza a API do Google Gemini para classificar emails e sugerir respostas automaticamente.</p>
<p>
<img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python 3.11+">
<img src="https://img.shields.io/badge/Flask-3.0-black.svg" alt="Flask 3.0">
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
- 🌗 **Tema claro/escuro** — alternância com um clique
- 📋 **Copiar resposta** — botão de cópia rápida
- 🔄 **Retry com backoff** — resiliência contra limites de taxa da API

## 🛠️ Stack

| Camada | Tecnologias |
|---|---|
| **Backend** | Python 3.11+, Flask 3.0, Gunicorn |
| **IA** | Google Gemini API (`google-genai` SDK) |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Banco de dados** | PostgreSQL 15, SQLAlchemy, Flask-Migrate |
| **Cache / Filas** | Redis 7, Celery |
| **Segurança** | Flask-JWT-Extended, Flask-Talisman, Flask-Limiter, Flask-CORS |
| **Observabilidade** | Sentry, Prometheus |
| **Infraestrutura** | Docker, Docker Compose, Nginx |

## ⚙️ Como Executar

### Desenvolvimento local (sem Docker)

```bash
# 1. Clone o repositório
git clone https://github.com/pedropompeu/autou-case-analisador-email.git
cd autou-case-analisador-email

# 2. Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY

# 5. Inicie o servidor
python wsgi.py
# Acesse http://localhost:5000
```

### Com Docker (recomendado)

```bash
# 1. Configure as variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GEMINI_API_KEY e SECRET_KEY

# 2. Build + inicie tudo (backend + PostgreSQL + Redis + Celery)
make init
# Acesse http://localhost:5000
```

### Comandos úteis (Makefile)

```bash
make help          # Lista todos os comandos
make test          # Executa testes
make test-cov      # Testes com cobertura
make lint          # Linting (flake8 + mypy)
make format        # Formata código (black + isort)
make clean         # Remove artefatos de build
make docker-up     # Inicia containers
make docker-down   # Para containers
make docker-logs   # Logs dos containers
make migrate       # Executa migrações do banco
```

## 🏗️ Estrutura do Projeto

```
autou-case/
├── backend/                     # Código-fonte principal
│   ├── config.py                # Configuração multi-ambiente
│   ├── app/
│   │   ├── __init__.py          # App factory (Flask)
│   │   ├── api/
│   │   │   ├── legacy/          # Rotas do frontend HTML (/, /processar-email)
│   │   │   └── v1/              # API REST versionada (/api/v1/*)
│   │   ├── middleware/          # Request logger
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/       # Repository pattern (acesso a dados)
│   │   ├── services/           # Lógica de negócio + LLM providers
│   │   └── utils/              # File processor, cache
│   ├── migrations/              # Alembic migrations
│   └── tests/                   # Testes (unit + integration)
├── templates/index.html         # Frontend (Jinja2 + Bootstrap 5)
├── static/                      # CSS + JS do frontend
├── wsgi.py                      # Entry point WSGI (Gunicorn)
├── celery_worker.py             # Entry point Celery
├── docker-compose.yml           # Orquestração (dev)
├── Dockerfile.backend           # Imagem Docker do backend
├── Makefile                     # Comandos utilitários
├── requirements.txt             # Dependências de produção
├── context/                     # Memória de projeto (para IAs)
└── fontes/                      # Fontes brutas auditáveis
```

## 🔌 API Endpoints

### Frontend (legacy)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Página principal |
| `POST` | `/processar-email` | Analisa email (form-data) |

### API v1 (autenticada via JWT)

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/analyze` | Analisa email (JSON) |
| `POST` | `/api/v1/analyze-with-file` | Analisa email com ficheiro |
| `GET` | `/api/v1/tasks/<id>` | Status de tarefa assíncrona |
| `GET` | `/health` | Health check |

## 🤔 Decisões Técnicas

- **Gemini vs. NLP Tradicional:** LLMs modernos entendem contexto e semântica sem pré-processamento manual (stop words, stemming).
- **Retry com Exponential Backoff + Jitter:** Distribui retentativas no tempo, evitando "thundering herd" quando múltiplos requests atingem rate limit.
- **Arquitetura enterprise (backend/):** Repository Pattern, Service Layer, Abstract LLM Provider — permite trocar de modelo facilmente e testar com mocks.
- **Cache por hash SHA-256:** Emails idênticos são servidos do banco sem chamar a API novamente.