"""
Modelo para armazenar histórico de análises de email.
"""
from backend.app import db
from backend.app.models.base import BaseModel


class EmailAnalysis(BaseModel):
    """Registro de análise de email processada pela IA."""

    __tablename__ = "email_analyses"

    # Hash do conteúdo do email (para cache)
    content_hash = db.Column(db.String(64), nullable=False, index=True)

    # Conteúdo original (opcional, para auditoria)
    email_content = db.Column(db.Text, nullable=True)

    # Resultado da análise
    category = db.Column(db.String(50), nullable=False)  # Produtivo/Improdutivo
    summary = db.Column(db.Text, nullable=False)
    suggested_response = db.Column(db.Text, nullable=False)

    # Metadados
    processing_time_ms = db.Column(db.Integer, nullable=True)
    model_used = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<EmailAnalysis {self.id} - {self.category}>"
