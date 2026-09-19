from datetime import datetime
import bcrypt
from backend.app import db
from backend.app.models.base import BaseModel

class User(BaseModel):
    """Modelo de usuário para autenticação na API."""
    __tablename__ = "users"

    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password: str):
        """Gera um hash seguro da senha."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verifica se a senha fornecida coincide com o hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"), 
            self.password_hash.encode("utf-8")
        )

    def __repr__(self):
        return f"<User {self.username}>"
