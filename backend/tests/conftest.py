"""
Configuração de fixtures para testes com Pytest.

Estratégia:
- FLASK_ENV=testing é definido ANTES de importar qualquer módulo da aplicação,
  garantindo que TestingConfig seja carregada (sem precisar de .env).
- Banco de dados: SQLite em memória — sem dependência de PostgreSQL nos testes.
- Redis: desabilitado em TestingConfig (RATELIMIT_ENABLED=False) — sem
  dependência de Redis nos testes unitários/integração.
"""
import os

# Define o ambiente ANTES de qualquer import da aplicação —
# isso garante que get_config() retorne TestingConfig sem erros de SECRET_KEY.
os.environ.setdefault("FLASK_ENV", "testing")

import pytest
from backend.app import create_app, db as _db
from backend.app.services.gemini_provider import MockLLMProvider


@pytest.fixture(scope="session")
def app():
    """
    Cria uma instância Flask configurada para testes.

    Escopo 'session': uma única instância por suite de testes —
    mais rápido que criar/destruir por função.
    """
    flask_app = create_app()

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Cliente HTTP de teste Flask."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """
    Sessão de banco de dados isolada por teste.

    Faz rollback ao final de cada teste para manter o banco limpo.
    """
    with app.app_context():
        yield _db.session
        _db.session.rollback()
        _db.session.remove()


@pytest.fixture
def mock_llm_provider():
    """
    Mock determinístico do LLM Provider.

    Use este fixture para testar services sem fazer chamadas reais à Gemini API.
    """
    return MockLLMProvider()
