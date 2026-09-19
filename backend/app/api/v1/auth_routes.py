import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate, ValidationError

from backend.app.models.user import User
from backend.app import db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# --- Schemas ---

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6))

login_schema = LoginSchema()
register_schema = RegisterSchema()

# --- Routes ---

@auth_bp.route("/register", methods=["POST"])
def register():
    """Registra um novo usuário."""
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    new_user = User(username=data["username"])
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()

    logger.info(f"New user registered: {new_user.username}")
    return jsonify({"message": "User created successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Autentica um usuário e retorna um token JWT."""
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    user = User.query.filter_by(username=data["username"], is_active=True).first()

    if not user or not user.check_password(data["password"]):
        logger.warning(f"Failed login attempt for user: {data['username']}")
        return jsonify({"error": "Invalid username or password"}), 401

    # Atualizar last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Criar token de acesso
    access_token = create_access_token(identity=user.username)
    
    logger.info(f"User logged in: {user.username}")
    return jsonify({
        "access_token": access_token,
        "username": user.username
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Retorna dados do usuário autenticado."""
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    return jsonify({
        "id": user.id,
        "username": user.username,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat()
    }), 200
