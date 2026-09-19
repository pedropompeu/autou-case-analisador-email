"""
Configuração da aplicação com suporte a múltiplos ambientes.
"""
import os
from typing import List

# ──────────────────────────────────────────────
# Constantes globais (usadas em toda a aplicação)
# ──────────────────────────────────────────────
# Tamanho máximo do conteúdo de email armazenado no banco (caracteres)
EMAIL_CONTENT_MAX_STORE: int = 1000


class Config:
    """Configuração base — valores comuns a todos os ambientes."""

    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))  # 1 dia

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # AI Service
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

    # Rate Limiting
    RATELIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_STORAGE_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_DEFAULT: str = "10 per minute"

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")

    # Upload
    MAX_CONTENT_LENGTH: int = 2 * 1024 * 1024  # 2MB

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Sentry (Observability)
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    PROMETHEUS_METRICS_ENABLED: bool = (
        os.getenv("PROMETHEUS_METRICS_ENABLED", "true").lower() == "true"
    )

    # Cache TTL
    CACHE_DEFAULT_TIMEOUT: int = 3600  # 1 hora

    def validate(self) -> None:
        """
        Valida variáveis críticas em tempo de execução (não em import-time).
        Chamado explicitamente em create_app() para não quebrar testes.
        """
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY não definida. Adicione ao seu arquivo .env")
        if not self.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não definida. Adicione ao seu arquivo .env")


def _normalize_db_url(url: str) -> str:
    """Normaliza 'postgres://' (padrão antigo de PaaS como Render/Heroku) para 'postgresql://'."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento."""

    ENV = "development"
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI: str = _normalize_db_url(
        os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/email_analyzer",
        )
    )


class TestingConfig(Config):
    """Configuração para testes automatizados."""

    ENV = "testing"
    DEBUG = False
    TESTING = True
    SQLALCHEMY_ECHO = False
    # SQLite em memória — sem necessidade de PostgreSQL para testes unitários
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    RATELIMIT_ENABLED = False

    # Valores fixos para testes — não precisam de .env
    SECRET_KEY = "test-secret-key-for-ci-only"
    GEMINI_API_KEY = "test-gemini-api-key-for-ci"

    def validate(self) -> None:
        """Testes não validam variáveis de ambiente — valores fixos são suficientes."""
        pass


class ProductionConfig(Config):
    """Configuração para ambiente de produção."""

    ENV = "production"
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI: str = _normalize_db_url(os.getenv("DATABASE_URL", ""))

    # Security headers via Flask-Talisman
    TALISMAN_FORCE_HTTPS = True
    TALISMAN_STRICT_TRANSPORT_SECURITY = True
    TALISMAN_CONTENT_SECURITY_POLICY = {
        "default-src": "'self'",
        "script-src": ["'self'", "'unsafe-inline'"],
        "style-src": ["'self'", "'unsafe-inline'"],
    }

    def validate(self) -> None:
        """Valida config de produção — mais restritiva que a base."""
        super().validate()
        if not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL não definida. Obrigatória em produção.")


# Mapeamento de ambientes
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config() -> Config:
    """Retorna a configuração apropriada baseada na variável FLASK_ENV."""
    env = os.getenv("FLASK_ENV", "development")
    config_class = config_by_name.get(env, DevelopmentConfig)
    return config_class()
