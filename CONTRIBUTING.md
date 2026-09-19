# Guia de Contribuição

## 🚀 Setup do Ambiente de Desenvolvimento

### Pré-requisitos

- Docker & Docker Compose
- Python 3.11+
- Git

### Configuração Inicial

1. **Clone o repositório**
```bash
git clone <repository-url>
cd email-analyzer
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o .env com suas credenciais
```

3. **Inicie os serviços com Docker**
```bash
docker-compose up -d
```

4. **Execute as migrações do banco de dados**
```bash
docker-compose exec backend flask db upgrade
```

5. **Acesse a aplicação**
- Backend: http://localhost:5000
- Health Check: http://localhost:5000/health
- API Docs: http://localhost:5000/api/v1/status

## 🧪 Executando Testes

### Testes Locais (sem Docker)

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Rodar todos os testes
pytest

# Rodar com cobertura
pytest --cov=backend/app --cov-report=html

# Rodar apenas testes unitários
pytest -m unit

# Rodar apenas testes de integração
pytest -m integration
```

### Testes no Docker

```bash
docker-compose exec backend pytest
```

## 📝 Padrões de Código

### Formatação

Usamos **Black** para formatação automática:

```bash
black backend/
```

### Linting

```bash
# Flake8
flake8 backend/

# MyPy (type checking)
mypy backend/
```

### Imports

Usamos **isort** para organizar imports:

```bash
isort backend/
```

### Executar todos os checks de qualidade

```bash
# Formatar código
black backend/

# Organizar imports
isort backend/

# Verificar linting
flake8 backend/

# Type checking
mypy backend/

# Rodar testes
pytest
```

## 🏗️ Arquitetura

### Estrutura de Pastas

```
backend/
├── app/
│   ├── api/v1/          # Endpoints da API (versionados)
│   ├── models/          # Modelos SQLAlchemy
│   ├── repositories/    # Camada de acesso a dados
│   ├── services/        # Lógica de negócio
│   ├── middleware/      # Middlewares customizados
│   └── utils/           # Utilitários
├── tests/
│   ├── unit/            # Testes unitários
│   └── integration/     # Testes de integração
├── migrations/          # Migrações Alembic
└── config.py            # Configurações por ambiente
```

### Padrões Arquiteturais

- **Factory Pattern**: Criação da aplicação Flask
- **Repository Pattern**: Isolamento de acesso a dados
- **Service Layer**: Lógica de negócio isolada
- **Dependency Injection**: Para facilitar testes

## 🔄 Workflow de Desenvolvimento

### Branches

- `main`: Código em produção
- `develop`: Código em desenvolvimento
- `feature/*`: Novas funcionalidades
- `bugfix/*`: Correções de bugs
- `hotfix/*`: Correções urgentes em produção

### Commits

Seguimos o padrão [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: adiciona endpoint de histórico de análises
fix: corrige validação de email vazio
docs: atualiza README com instruções Docker
test: adiciona testes para EmailAnalysisService
refactor: melhora estrutura do LLM Provider
```

### Pull Requests

1. Crie uma branch a partir de `develop`
2. Faça suas alterações
3. Execute os testes e linting
4. Abra um PR para `develop`
5. Aguarde aprovação e CI passar

## 🐛 Reportando Bugs

Ao reportar um bug, inclua:

- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. atual
- Logs relevantes
- Ambiente (OS, versão do Python, etc.)

## 💡 Sugerindo Melhorias

Abra uma issue com:

- Descrição da melhoria
- Justificativa (por que é útil?)
- Exemplos de uso (se aplicável)

## 📚 Recursos Úteis

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Docker Documentation](https://docs.docker.com/)
- [Pytest Documentation](https://docs.pytest.org/)

## ❓ Dúvidas?

Abra uma issue ou entre em contato com a equipe de desenvolvimento.
