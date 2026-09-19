"""
Modelo para armazenar feedback do usuário sobre análises (Human-in-the-loop).
"""
from backend.app import db
from backend.app.models.base import BaseModel


class AnalysisFeedback(BaseModel):
    """Feedback do usuário sobre uma análise de email."""

    __tablename__ = "analysis_feedbacks"

    # Contexto multi-tenant
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Referência à análise original
    analysis_id = db.Column(
        db.Integer,
        db.ForeignKey("email_analyses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    analysis = db.relationship("EmailAnalysis", backref="feedbacks")

    # Feedback do usuário
    approved = db.Column(db.Boolean, nullable=False)
    corrected_category = db.Column(db.String(50), nullable=True)
    corrected_summary = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Quem deu o feedback (se autenticado)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self):
        action = "approved" if self.approved else "corrected"
        return f"<AnalysisFeedback {self.id} - {action}>"
