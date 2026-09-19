import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE

from backend.app.models.user import User
from backend.app.models.tenant import Tenant
from backend.app.services.audit_service import AuditService
from backend.app.utils.jwt_blocklist import add_token_to_blocklist
from backend.app import db

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

# --- Schemas ---


class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=True)
    password = fields.Str(required=True)


class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(load_default=None)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    organization_name = fields.Str(load_default=None, validate=validate.Length(max=120))
    role = fields.Str(
        load_default="operator",
        validate=validate.OneOf(["admin", "operator", "viewer", "auditor"]),
    )


login_schema = LoginSchema()
register_schema = RegisterSchema()

# --- Routes ---


@auth_bp.route("/register", methods=["POST"])
def register():
    """Registra um novo usuário e cria/associa a uma organização (Tenant)."""
    try:
        data = register_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already exists"}), 409

    if data.get("email") and User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already in use"}), 409

    # Criação ou associação de Tenant
    org_name = data.get("organization_name") or f"Org {data['username']}"
    slug = org_name.lower().replace(" ", "-").replace(".", "")[:80]
    
    tenant = Tenant.query.filter_by(slug=slug).first()
    if not tenant:
        tenant = Tenant(
            name=org_name,
            slug=slug,
            plan="starter",
            api_key=Tenant.generate_api_key(),
            settings={"pii_masking_enabled": True, "retention_days": 90},
        )
        db.session.add(tenant)
        db.session.flush()

    # Se for o primeiro usuário da org, ele é Admin
    user_role = data.get("role", "operator")
    if tenant.users.count() == 0:
        user_role = "admin"

    new_user = User(
        username=data["username"],
        email=data.get("email"),
        role=user_role,
        tenant_id=tenant.id,
    )
    new_user.set_password(data["password"])

    db.session.add(new_user)
    db.session.commit()

    # Registrar auditoria
    AuditService.log(
        action="auth.register",
        resource_type="User",
        resource_id=str(new_user.id),
        details={"username": new_user.username, "role": new_user.role, "tenant": tenant.slug},
        user_id=new_user.id,
        tenant_id=tenant.id,
    )

    logger.info(f"New user registered: {new_user.username} (Role: {new_user.role}, Tenant: {tenant.slug})")
    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "role": new_user.role,
            "tenant_id": tenant.id,
            "tenant_slug": tenant.slug,
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Autentica um usuário e retorna um token JWT com claims de role e tenant."""
    try:
        data = login_schema.load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    user = User.query.filter_by(username=data["username"], is_active=True, is_deleted=False).first()

    if not user or not user.check_password(data["password"]):
        logger.warning(f"Failed login attempt for user: {data['username']}")
        AuditService.log(
            action="auth.login_failed",
            resource_type="User",
            details={"username": data["username"]},
        )
        return jsonify({"error": "Invalid username or password"}), 401

    # Atualizar last login
    user.last_login = datetime.utcnow()
    db.session.commit()

    # Criar token de acesso com claims corporativas
    additional_claims = {
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
    }
    access_token = create_access_token(
        identity=user.username,
        additional_claims=additional_claims,
    )

    # Registrar auditoria
    AuditService.log(
        action="auth.login",
        resource_type="User",
        resource_id=str(user.id),
        details={"role": user.role},
        user_id=user.id,
        tenant_id=user.tenant_id,
    )

    logger.info(f"User logged in: {user.username} (Role: {user.role})")
    return jsonify({
        "access_token": access_token,
        "username": user.username,
        "role": user.role,
        "tenant_id": user.tenant_id,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Invalida o token JWT atual adicionando-o à blocklist no Redis."""
    jwt_payload = get_jwt()
    jti = jwt_payload.get("jti")
    current_username = get_jwt_identity()
    user_id = jwt_payload.get("user_id")
    tenant_id = jwt_payload.get("tenant_id")

    if jti:
        add_token_to_blocklist(jti)

    AuditService.log(
        action="auth.logout",
        resource_type="User",
        resource_id=str(user_id) if user_id else None,
        user_id=user_id,
        tenant_id=tenant_id,
    )

    logger.info(f"User logged out: {current_username} (JTI: {jti})")
    return jsonify({"message": "Successfully logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Retorna dados do usuário autenticado e seu Tenant."""
    current_username = get_jwt_identity()
    user = User.query.filter_by(username=current_username, is_deleted=False).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    tenant_data = None
    if user.tenant_rel:
        tenant_data = {
            "id": user.tenant_rel.id,
            "name": user.tenant_rel.name,
            "slug": user.tenant_rel.slug,
            "plan": user.tenant_rel.plan,
            "settings": user.tenant_rel.settings,
        }

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "tenant": tenant_data,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "created_at": user.created_at.isoformat(),
    }), 200

