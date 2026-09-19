"""
Modelo para Notas Internas em análises de email (#45).
Permite colaboração entre operadores e auditores dentro de uma thread.
"""
from backend.app import db
from backend.app.models.base import BaseModel


class InternalNote(BaseModel):
    """Nota interna privada anexada a uma análise de email."""

    __tablename__ = "internal_notes"

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("email_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    content = db.Column(db.Text, nullable=False)

    # Relacionamentos
    user = db.relationship("User", backref="internal_notes")
    analysis = db.relationship("EmailAnalysis", backref="internal_notes")

    def __repr__(self):
        return f"<InternalNote {self.id} on Analysis {self.analysis_id}>"
