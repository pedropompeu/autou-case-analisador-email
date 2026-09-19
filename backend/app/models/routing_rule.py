"""
Modelo para Motor de Regras de Roteamento e SLA (#11, #17).
"""
from backend.app import db
from backend.app.models.base import BaseModel


class RoutingRule(BaseModel):
    """Regra condicional para roteamento e triagem automatizada."""

    __tablename__ = "routing_rules"

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Condição
    condition_field = db.Column(db.String(50), nullable=False)  # sentiment, urgency, category, fraud_risk_score
    condition_operator = db.Column(db.String(30), nullable=False, default="equals")  # equals, contains, gte, in
    condition_value = db.Column(db.String(255), nullable=False)

    # Ação
    action_type = db.Column(db.String(50), nullable=False)  # set_quarantine, set_urgency, alert_webhook, assign_role
    action_payload = db.Column(db.JSON, nullable=True, default=dict)

    priority = db.Column(db.Integer, nullable=False, default=100)  # menor valor = maior prioridade
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<RoutingRule {self.id} - {self.name} ({self.condition_field} {self.condition_operator} {self.condition_value})>"
