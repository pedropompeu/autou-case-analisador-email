"""
Application Factory Pattern para Flask.
"""
import json
import logging
import os
import sys
import time
from typing import Optional

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from prometheus_flask_exporter import PrometheusMetrics

from backend.app.celery_app import celery_init_app
from backend.config import get_config

# Extensões globais (inicializadas no create_app)
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)
metrics = PrometheusMetrics.for_app_factory()
jwt = JWTManager()


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Factory para criar e configurar a aplicação Flask.

    Args:
        config_name: Nome do ambiente (development, testing, production).
                     Se None, usa a variável FLASK_ENV.

    Returns:
        Instância configurada do Flask.
    """
    # Configurar caminhos de templates/static (prioriza build do React SPA se existir)
    dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
    if os.path.exists(os.path.join(dist_dir, "index.html")):
        app = Flask(
            __name__,
            template_folder=dist_dir,
            static_folder=os.path.join(dist_dir, "assets"),
            static_url_path="/assets",
        )
    else:
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../templates"))
        static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../static"))
        app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Carregar configuração
    config = get_config()

    # Validar variáveis críticas (levanta ValueError se faltar algo obrigatório).
    # TestingConfig.validate() é no-op — sem necessidade de .env em testes.
    config.validate()

    app.config.from_object(config)

    # Configurar logging estruturado (JSON)
    setup_logging(app)

    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    celery_init_app(app)

    # CORS
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Rate Limiting
    if app.config.get("RATELIMIT_ENABLED", True):
        limiter.init_app(app)

    # Metrics
    if app.config.get("PROMETHEUS_METRICS_ENABLED", True):
        metrics.init_app(app)
        metrics.info("app_info", "Application info", version="1.0.0", env=app.config.get("ENV"))

    # Security Headers (apenas fora de testes e desenvolvimento)
    if not app.config.get("DEBUG") and not app.config.get("TESTING"):
        Talisman(
            app,
            force_https=app.config.get("TALISMAN_FORCE_HTTPS", False),
            strict_transport_security=app.config.get("TALISMAN_STRICT_TRANSPORT_SECURITY", True),
            content_security_policy=app.config.get("TALISMAN_CONTENT_SECURITY_POLICY"),
        )

    # Registrar middlewares customizados
    register_middlewares(app)

    # Registrar blueprints (rotas)
    register_blueprints(app)

    # Registrar error handlers globais
    register_error_handlers(app)

    # Sentry (se configurado)
    if app.config.get("SENTRY_DSN"):
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            dsn=app.config["SENTRY_DSN"],
            integrations=[FlaskIntegration()],
            traces_sample_rate=0.1,
        )

    app.logger.info(
        json.dumps(
            {
                "event": "app_started",
                "env": app.config.get("ENV", "unknown"),
                "debug": app.config.get("DEBUG", False),
            }
        )
    )

    return app


# ── Logging ──────────────────────────────────────────────────────────────────


class _JsonFormatter(logging.Formatter):
    """Formata cada log como uma linha JSON — compatível com Loki/ELK/CloudWatch."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "msg": record.getMessage(),
        }
        # Campos extras injetados via extra={...}
        for key in ("method", "path", "status_code", "duration", "request_id"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(app: Flask) -> None:
    """Configura logging estruturado em JSON."""
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    handler.setLevel(log_level)

    app.logger.handlers = []  # remove handlers padrão do Flask
    app.logger.addHandler(handler)
    app.logger.setLevel(log_level)

    # Propagar também para root logger (captura logs de bibliotecas)
    logging.basicConfig(level=log_level, handlers=[handler])


# ── Registro de componentes ──────────────────────────────────────────────────


def register_middlewares(app: Flask) -> None:
    """Registra middlewares customizados."""
    from backend.app.middleware.request_logger import RequestLoggerMiddleware

    app.wsgi_app = RequestLoggerMiddleware(app.wsgi_app, app.logger)  # type: ignore[method-assign]


def register_blueprints(app: Flask) -> None:
    """Registra blueprints da API."""
    from backend.app.api.legacy import legacy_bp
    from backend.app.api.v1 import api_v1_bp

    # API v1 (estrutura enterprise)
    app.register_blueprint(api_v1_bp, url_prefix="/api/v1")

    # Rotas legacy (compatibilidade com frontend HTML/JS existente)
    app.register_blueprint(legacy_bp)

    # Health check raiz (fora da API versionada — para load balancers)
    @app.route("/health")
    def health():
        return jsonify({"status": "healthy", "version": "1.0.0"}), 200


def register_error_handlers(app: Flask) -> None:
    """Registra handlers globais de erro com respostas JSON padronizadas."""
    from backend.app.utils.jwt_blocklist import is_token_in_blocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload.get("jti")
        return is_token_in_blocklist(jti) if jti else False

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"error": "token_revoked", "message": "This token has been revoked / logged out"}
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "token_expired", "message": "The token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "invalid_token", "message": "Signature verification failed"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "error": "authorization_required",
                    "message": "Request does not contain an access token",
                }
            ),
            401,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not Found", "message": "Resource not found"}), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return (
            jsonify(
                {
                    "error": "Rate Limit Exceeded",
                    "message": "Too many requests. Please try again later.",
                }
            ),
            429,
        )

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(json.dumps({"event": "internal_error", "detail": str(error)}))
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )

    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.exception(json.dumps({"event": "unhandled_exception", "detail": str(error)}))
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                }
            ),
            500,
        )
