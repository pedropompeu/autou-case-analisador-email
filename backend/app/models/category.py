"""
Modelo para Categorias Dinâmicas Customizadas por Tenant.
Permite aos clientes corporativos criarem suas próprias taxonomias de triagem além do Produtivo/Improdutivo.
"""
from backend.app import db
from backend.app.models.base import BaseModel


class CustomCategory(BaseModel):
    """Categoria customizada definida por um tenant."""

    __tablename__ = "custom_categories"

    tenant_id = db.Column(
        db.Integer,
        db.ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    action_required = db.Column(db.Boolean, nullable=False, default=True)  # True = Produtivo / False = Improdutivo
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # Relacionamento
    tenant = db.relationship("Tenant", backref=db.backref("categories", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("tenant_id", "name", name="uq_tenant_category_name"),
    )

    def __repr__(self):
        return f"<CustomCategory {self.id} - {self.name} (Tenant {self.tenant_id})>"
