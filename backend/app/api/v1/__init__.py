"""
API v1 Blueprint.
"""
from flask import Blueprint

api_v1_bp = Blueprint("api_v1", __name__)

# Importar rotas (deve vir depois da criação do blueprint)
from backend.app.api.v1.email_routes import *
from backend.app.api.v1.health_routes import *
from backend.app.api.v1.stats_routes import *
from backend.app.api.v1.feedback_routes import *
from backend.app.api.v1.auth_routes import auth_bp

api_v1_bp.register_blueprint(auth_bp, url_prefix="/auth")

__all__ = ["api_v1_bp"]

