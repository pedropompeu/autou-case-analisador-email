"""
Rotas de health check e status da API.
"""
from flask import current_app, jsonify

from backend.app import db
from backend.app.api.v1 import api_v1_bp


@api_v1_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check detalhado da API.

    ---
    tags:
      - Health
    responses:
      200:
        description: Serviço saudável
      503:
        description: Serviço com problemas
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "environment": current_app.config.get("ENV", "unknown"),
        "checks": {},
    }

    # Verificar banco de dados
    try:
        db.session.execute(db.text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"

    # Verificar Redis (cache)
    try:
        from backend.app.utils.cache import get_redis_client

        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            health_status["checks"]["redis"] = "ok"
        else:
            health_status["checks"]["redis"] = "not configured"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"

    # Status code baseado na saúde geral
    status_code = 200 if health_status["status"] == "healthy" else 503

    return jsonify(health_status), status_code


@api_v1_bp.route("/status", methods=["GET"])
def api_status():
    """
    Informações sobre a API.

    ---
    tags:
      - Health
    responses:
      200:
        description: Informações da API
    """
    return (
        jsonify(
            {
                "api_version": "v1",
                "service": "Email Analyzer",
                "endpoints": {
                    "analyze": "/api/v1/analyze",
                    "analyze_with_file": "/api/v1/analyze-with-file",
                    "health": "/api/v1/health",
                },
            }
        ),
        200,
    )
