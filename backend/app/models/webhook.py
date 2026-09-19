"""
Modelos para Webhooks de Saída (Outbound Webhooks) no SaaS B2B.
Permite aos clientes receberem eventos em tempo real em seus próprios sistemas (ERP, CRM, Slack, etc.).
"""
import secrets

from backend.app import db
from backend.app.models.base import BaseModel


class WebhookSubscription(BaseModel):
    """Assinatura de Webhook cadastrada por um Tenant."""

    __tablename__ = "webhook_subscriptions"

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = db.Column(db.String(500), nullable=False)
    secret = db.Column(db.String(128), nullable=False)  # Usado para assinatura HMAC-SHA256
    events = db.Column(
        db.JSON, nullable=False, default=list
    )  # Ex: ["email.analyzed", "quarantine.flagged"]
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.String(255), nullable=True)

    # Relacionamentos
    tenant = db.relationship("Tenant", backref=db.backref("webhooks", lazy="dynamic"))
    deliveries = db.relationship(
        "WebhookDelivery", backref="subscription", lazy="dynamic", cascade="all, delete-orphan"
    )

    @classmethod
    def generate_secret(cls) -> str:
        """Gera um segredo seguro no padrão `whsec_...` para assinatura de payloads."""
        return f"whsec_{secrets.token_urlsafe(32)}"

    def __repr__(self):
        return f"<WebhookSubscription {self.id} - {self.url} (Tenant {self.tenant_id})>"


class WebhookDelivery(BaseModel):
    """Registro de tentativa de entrega de um Webhook para auditoria e observabilidade."""

    __tablename__ = "webhook_deliveries"

    subscription_id = db.Column(
        db.Integer,
        db.ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event = db.Column(db.String(50), nullable=False, index=True)
    payload = db.Column(db.JSON, nullable=False)
    status_code = db.Column(db.Integer, nullable=True)
    response_body = db.Column(db.Text, nullable=True)
    attempt = db.Column(db.Integer, nullable=False, default=1)
    success = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"<WebhookDelivery {self.id} - Event {self.event} (Status {self.status_code})>"
