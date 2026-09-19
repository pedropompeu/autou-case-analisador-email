"""
Gerenciamento de contexto do Tenant ativo na requisição.
Garante isolamento lógico multi-tenant em toda a camada de aplicação.
"""
from typing import Optional
from flask import g, request
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from backend.app.models.tenant import Tenant
from backend.app.models.user import User


def get_current_tenant_id() -> Optional[int]:
    """
    Recupera o tenant_id ativo na requisição atual.
    
    Ordem de resolução:
    1. Header X-API-Key (para integrações de máquina/API)
    2. Claims do JWT (para usuários web autenticados)
    3. flask.g.current_tenant_id (se explicitamente definido)
    """
    # 1. Resolução via API Key corporativa (B2B)
    try:
        api_key = request.headers.get("X-API-Key")
        if api_key:
            tenant = Tenant.query.filter_by(api_key=api_key, is_active=True, is_deleted=False).first()
            if tenant:
                g.current_tenant_id = tenant.id
                g.current_tenant = tenant
                return tenant.id
    except Exception:
        pass

    # 2. Resolução via JWT
    try:
        claims = get_jwt()
        if claims and "tenant_id" in claims and claims["tenant_id"] is not None:
            return int(claims["tenant_id"])
    except Exception:
        pass

    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims and "tenant_id" in claims and claims["tenant_id"] is not None:
            return int(claims["tenant_id"])
        
        # Fallback: consultar usuário do JWT se tenant_id não estiver no payload
        if claims and "sub" in claims:
            username = claims["sub"]
            user = User.query.filter_by(username=username, is_deleted=False).first()
            if user and user.tenant_id:
                return user.tenant_id
    except Exception:
        pass

    if hasattr(g, "current_tenant_id") and g.current_tenant_id is not None:
        return g.current_tenant_id

    return None


def get_current_tenant() -> Optional[Tenant]:
    """Retorna o objeto Tenant ativo na requisição."""
    if hasattr(g, "current_tenant") and g.current_tenant is not None:
        return g.current_tenant

    tenant_id = get_current_tenant_id()
    if tenant_id:
        tenant = Tenant.query.filter_by(id=tenant_id, is_active=True, is_deleted=False).first()
        g.current_tenant = tenant
        return tenant
    return None


def set_current_tenant_id(tenant_id: Optional[int]) -> None:
    """Define explicitamente o tenant_id para o ciclo da requisição."""
    g.current_tenant_id = tenant_id
