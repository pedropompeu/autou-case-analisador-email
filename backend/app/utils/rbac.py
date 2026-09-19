"""
Controle de Acesso Baseado em Papéis (RBAC - Role-Based Access Control).
Papéis suportados: admin, operator, viewer, auditor.
"""
from functools import wraps
from typing import List, Tuple, Optional
from flask import jsonify, g
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.app.models.user import User

# Hierarquia e definições de papéis
ROLE_ADMIN = "admin"
ROLE_OPERATOR = "operator"
ROLE_VIEWER = "viewer"
ROLE_AUDITOR = "auditor"

ALL_ROLES = [ROLE_ADMIN, ROLE_OPERATOR, ROLE_VIEWER, ROLE_AUDITOR]


def get_current_user() -> Optional[User]:
    """Retorna o usuário autenticado na requisição atual."""
    if hasattr(g, "current_user") and g.current_user is not None:
        return g.current_user

    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user = User.query.filter_by(username=identity, is_active=True, is_deleted=False).first()
            g.current_user = user
            return user
    except Exception:
        pass
    return None


def get_current_user_role() -> str:
    """Recupera a role do usuário a partir das claims do JWT ou do banco."""
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims and "role" in claims and claims["role"]:
            return str(claims["role"])
    except Exception:
        pass

    user = get_current_user()
    if user:
        return user.role
    return ROLE_VIEWER


def roles_required(*allowed_roles: str):
    """
    Decorator que restringe o endpoint apenas para usuários com as roles informadas.
    
    Exemplo:
        @api_v1_bp.route("/admin/settings", methods=["POST"])
        @jwt_required()
        @roles_required("admin")
        def update_settings():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Garante que o JWT é verificado
            verify_jwt_in_request()
            
            user_role = get_current_user_role()
            if user_role not in allowed_roles:
                return jsonify({
                    "error": "insufficient_permissions",
                    "message": f"User role '{user_role}' is not authorized to access this resource. Required: {list(allowed_roles)}"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
