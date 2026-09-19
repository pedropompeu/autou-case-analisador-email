"""
Modelo de Tenant para isolamento lógico multi-tenant no SaaS B2B.
"""
import secrets
from backend.app import db
from backend.app.models.base import BaseModel


class Tenant(BaseModel):
    """Representa uma organização / empresa assinante da plataforma."""

    __tablename__ = "tenants"

    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    plan = db.Column(db.String(50), nullable=False, default="starter")  # starter, pro, enterprise
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    
    # API Key para integrações B2B diretas (Microsoft Graph, Gmail, ERP)
    api_key = db.Column(db.String(128), unique=True, nullable=True, index=True)

    # Configurações do tenant (retenção de dados, regras de mascaramento, etc.)
    settings = db.Column(db.JSON, nullable=False, default=dict)

    # Relacionamentos
    users = db.relationship("User", backref="tenant_rel", lazy="dynamic")
    analyses = db.relationship("EmailAnalysis", backref="tenant_rel", lazy="dynamic")
    feedbacks = db.relationship("AnalysisFeedback", backref="tenant_rel", lazy="dynamic")

    @classmethod
    def generate_api_key(cls) -> str:
        """Gera uma chave de API segura no padrão `ak_live_...`"""
        return f"ak_live_{secrets.token_urlsafe(32)}"

    def __repr__(self):
        return f"<Tenant {self.id} - {self.slug} ({self.plan})>"
