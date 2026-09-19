"""
API v1 Blueprint.
"""
from flask import Blueprint

api_v1_bp: Blueprint = Blueprint("api_v1", __name__)

from backend.app.api.v1.admin_routes import admin_bp
from backend.app.api.v1.auth_routes import auth_bp
from backend.app.api.v1.compliance_routes import compliance_bp
from backend.app.api.v1.docs_routes import docs_bp

# Importar rotas (deve vir depois da criação do blueprint)
from backend.app.api.v1.email_routes import *
from backend.app.api.v1.feedback_routes import *
from backend.app.api.v1.health_routes import *
from backend.app.api.v1.ingest_routes import ingest_bp
from backend.app.api.v1.stats_routes import *
from backend.app.api.v1.webhook_routes import webhook_bp
from backend.app.api.v1.workflow_routes import workflow_bp

api_v1_bp.register_blueprint(auth_bp, url_prefix="/auth")
api_v1_bp.register_blueprint(admin_bp, url_prefix="/admin")
api_v1_bp.register_blueprint(webhook_bp, url_prefix="/webhooks")
api_v1_bp.register_blueprint(ingest_bp, url_prefix="/ingest")
api_v1_bp.register_blueprint(compliance_bp, url_prefix="/compliance")
api_v1_bp.register_blueprint(docs_bp)
api_v1_bp.register_blueprint(workflow_bp)

__all__ = ["api_v1_bp"]
