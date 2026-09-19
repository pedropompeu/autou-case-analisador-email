"""
Modelo para trilha de auditoria imutável (Audit Trail).
Essencial para compliance LGPD, GDPR e exigências regulatórias do setor financeiro.
"""
from backend.app import db
from backend.app.models.base import BaseModel


class AuditLog(BaseModel):
    """Registro imutável de eventos de auditoria e segurança."""

    __tablename__ = "audit_logs"

    # Contexto organizacional e usuário
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Ação executada (ex: auth.login, auth.logout, email.analyze, email.view, feedback.submit, settings.update)
    action = db.Column(db.String(100), nullable=False, index=True)

    # Recurso afetado
    resource_type = db.Column(db.String(50), nullable=True)  # EmailAnalysis, User, Tenant, etc.
    resource_id = db.Column(db.String(50), nullable=True)

    # Detalhes contextuais estruturados
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    details = db.Column(db.JSON, nullable=True)

    # Relacionamentos
    tenant = db.relationship("Tenant", backref="audit_logs")
    user = db.relationship("User", backref="audit_logs")

    def __repr__(self):
        return (
            f"<AuditLog {self.id} - {self.action} by User {self.user_id} (Tenant {self.tenant_id})>"
        )
