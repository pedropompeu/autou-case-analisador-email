"""
Legacy routes - Compatibilidade com frontend existente.
Mantém as rotas originais funcionando enquanto migra para a nova API.
"""
from flask import Blueprint

legacy_bp = Blueprint(
    "legacy", __name__, template_folder="../../../templates", static_folder="../../../static"
)

# Importar rotas
from backend.app.api.legacy import routes

__all__ = ["legacy_bp"]
