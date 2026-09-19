"""
Modelo para armazenar histórico de análises de email.
"""
from backend.app import db
from backend.app.models.base import BaseModel


class EmailAnalysis(BaseModel):
    """Registro de análise de email processada pela IA."""

    __tablename__ = "email_analyses"

    # Contexto multi-tenant e autoria
    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Memória de Thread (#7)
    thread_id = db.Column(db.String(100), nullable=True, index=True)

    # Hash do conteúdo do email (para cache)
    content_hash = db.Column(db.String(64), nullable=False, index=True)

    # Conteúdo original (criptografado at-rest)
    email_content = db.Column(db.Text, nullable=True)

    # Resultado da análise e categorização
    category = db.Column(db.String(80), nullable=False)  # Categoria primária ou dinâmica
    sub_category = db.Column(db.String(80), nullable=True)
    summary = db.Column(db.Text, nullable=False)
    suggested_response = db.Column(db.Text, nullable=False)

    # Inteligência Avançada (Fase 1)
    sentiment = db.Column(db.String(30), nullable=True)  # Positivo, Neutro, Negativo, Irritado
    urgency = db.Column(db.String(20), nullable=True)  # Baixa, Media, Alta, Critica
    confidence_score = db.Column(db.Float, nullable=True)  # 0.0 a 1.0
    in_quarantine = db.Column(db.Boolean, nullable=False, default=False)  # Quarentena humana

    # Detecção de Fraude e Phishing (#6)
    fraud_risk_score = db.Column(db.Float, nullable=True)  # 0.0 a 1.0
    fraud_flags = db.Column(db.JSON, nullable=True)  # Lista de indícios semânticos

    # Extração de Entidades Nomeadas - NER (#3)
    extracted_entities = db.Column(db.JSON, nullable=True)  # Valores, datas, CNPJs, protocolos

    # Tom de resposta utilizado (#8)
    tone_used = db.Column(db.String(30), nullable=True, default="formal")

    # Metadados de segurança e performance
    pii_masked = db.Column(db.Boolean, nullable=False, default=False)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    model_used = db.Column(db.String(100), nullable=True)

    # Workflow e Atribuição de Equipe (#41, #44)
    status = db.Column(
        db.String(30), nullable=False, default="pending"
    )  # pending, in_progress, resolved, escalated
    assigned_to_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relacionamentos
    user = db.relationship("User", foreign_keys=[user_id], backref="created_analyses")
    assigned_user = db.relationship(
        "User", foreign_keys=[assigned_to_user_id], backref="assigned_analyses"
    )

    def __repr__(self):
        return f"<EmailAnalysis {self.id} - {self.category} ({self.status})>"
