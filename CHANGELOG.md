# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2025-11-10

### 🎉 Lançamento Inicial - Arquitetura Enterprise

#### Adicionado

**Infraestrutura & DevOps**
- Docker multi-stage builds para Backend e Frontend
- Docker Compose para ambiente de desenvolvimento local
- PostgreSQL como banco de dados principal
- Redis para cache e rate limiting
- GitHub Actions CI/CD pipeline com:
  - Linting automático (Black, Flake8, MyPy)
  - Testes automatizados com cobertura
  - Build e validação de imagens Docker
  - Security scanning com Trivy

**Backend - Arquitetura**
- Application Factory Pattern para Flask
- Blueprints versionados (`/api/v1`)
- Repository Pattern para isolamento de dados
- Service Layer para lógica de negócio
- Middleware customizado para logging de requisições
- Global error handlers com respostas JSON padronizadas

**Backend - Segurança**
- Flask-Talisman para security headers (HSTS, CSP)
- Flask-Limiter com Redis para rate limiting
- CORS configurável por ambiente
- Validação de inputs com Marshmallow schemas
- Soft delete em modelos (auditoria)

**Backend - IA & Serviços**
- Interface abstrata `LLMProvider` (agnóstico de IA)
- Implementação `GeminiProvider` com:
  - Retry exponencial para rate limits
  - Circuit breaker pattern
  - Logging estruturado
- `MockLLMProvider` para testes sem gastar créditos
- Cache de análises por hash de conteúdo
- Histórico de análises no banco de dados

**Backend - API**
- `POST /api/v1/analyze` - Análise de texto
- `POST /api/v1/analyze-with-file` - Análise com upload (.txt, .pdf)
- `GET /api/v1/health` - Health check detalhado
- `GET /api/v1/status` - Informações da API
- `GET /health` - Health check simples

**Qualidade & Testes**
- Pytest configurado com fixtures
- Testes unitários para Services
- Testes de integração para API endpoints
- Cobertura de código com pytest-cov
- Configuração de linting (Flake8, Black, MyPy)

**Documentação**
- README.md com badges e instruções
- CONTRIBUTING.md com guia de desenvolvimento
- CHANGELOG.md (este arquivo)
- Comentários inline e docstrings
- Swagger/OpenAPI ready (docstrings preparadas)

**Configuração**
- Suporte a múltiplos ambientes (Development, Testing, Production)
- Validação de variáveis críticas no startup
- `.env.example` com todas as configurações necessárias
- Configuração centralizada em `config.py`

#### Mudanças em relação à versão anterior

- **Refatoração completa** do código monolítico para arquitetura em camadas
- **Migração** de SQLite para PostgreSQL
- **Adição** de cache com Redis
- **Implementação** de rate limiting
- **Separação** de responsabilidades (Repository, Service, API)
- **Melhoria** de segurança com headers e validação
- **Adição** de testes automatizados
- **Dockerização** completa da aplicação

#### Segurança

- Implementação de rate limiting para prevenir abuso
- Headers de segurança (HSTS, CSP, X-Frame-Options)
- Validação rigorosa de inputs
- Secrets gerenciados via variáveis de ambiente
- Usuário não-root no container Docker

#### Performance

- Cache de análises repetidas (Redis + Database)
- Multi-stage Docker builds (imagens otimizadas)
- Connection pooling no PostgreSQL
- Retry exponencial para APIs externas

---

## [0.1.0] - 2025-01-01 (Versão Original — pré-refatoração)

### Adicionado
- Aplicação Flask básica monolítica
- Integração com Google Gemini API
- Interface web simples (HTML/CSS/JS)
- Suporte a upload de arquivos .txt e .pdf
- Retry básico para rate limits

### Limitações da versão original
- Código monolítico em um único arquivo
- Sem testes automatizados
- Sem cache
- Sem rate limiting
- Sem versionamento de API
- Sem containerização
- SQLite (não adequado para produção)
- Sem CI/CD

---

## Tipos de Mudanças

- `Adicionado` para novas funcionalidades
- `Mudado` para alterações em funcionalidades existentes
- `Depreciado` para funcionalidades que serão removidas
- `Removido` para funcionalidades removidas
- `Corrigido` para correções de bugs
- `Segurança` para vulnerabilidades corrigidas
