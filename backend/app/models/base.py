"""
Modelo base com campos comuns e soft delete.
"""
from datetime import datetime

from backend.app import db


class BaseModel(db.Model):  # type: ignore[name-defined, misc]
    """Modelo abstrato com campos comuns a todas as entidades."""

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)

    def soft_delete(self):
        """Marca o registro como deletado sem removê-lo do banco."""
        self.is_deleted = True
        db.session.commit()

    def to_dict(self) -> dict:
        """Converte o modelo para dicionário (útil para serialização)."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
