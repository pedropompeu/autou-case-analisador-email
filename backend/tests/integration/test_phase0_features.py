"""
Testes de integração para as funcionalidades da Fase 0:
- Multi-tenancy isolation
- RBAC (Role-Based Access Control)
- Trilha de Auditoria (Audit Logs)
- Mascaramento de PII
- JWT Logout & Blocklist
"""
from backend.app.models.audit_log import AuditLog


def test_multi_tenant_registration(client):
    """Testa cadastro com criação automática de Tenant."""
    payload = {
        "username": "financial_admin",
        "email": "fin_admin@banco.com",
        "password": "strongpassword123",
        "organization_name": "Banco Alpha Corp",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["role"] == "admin"  # Primeiro usuário da org é Admin
    assert data["user"]["tenant_slug"] == "banco-alpha-corp"


def test_login_returns_tenant_and_role_claims(client):
    """Testa se login retorna claims de Tenant e Role."""
    # 1. Registrar
    reg_payload = {
        "username": "operator_user",
        "email": "op@empresa.com",
        "password": "password123",
        "organization_name": "Empresa Beta",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # 2. Login
    login_payload = {
        "username": "operator_user",
        "password": "password123",
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["tenant_id"] is not None


def test_jwt_logout_and_revocation(client):
    """Testa se logout invalida o token via Redis/Memory blocklist."""
    reg_payload = {
        "username": "logout_test_user",
        "password": "password123",
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = client.post("/api/v1/auth/login", json=reg_payload)
    token = login_resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Acesso inicial OK
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200

    # Logout
    logout_resp = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code == 200

    # Acesso subsequente com o mesmo token deve ser rejeitado (401 revoked)
    me_after_logout = client.get("/api/v1/auth/me", headers=headers)
    assert me_after_logout.status_code == 401
    assert me_after_logout.get_json()["error"] == "token_revoked"


def test_rbac_admin_audit_logs_endpoint(client, auth_headers, admin_auth_headers):
    """Testa restrição de acesso por papel: apenas admin/auditor pode ver audit logs."""
    # Operador comum tentando acessar endpoint de admin -> 403 Forbidden
    op_response = client.get("/api/v1/admin/audit-logs", headers=auth_headers)
    assert op_response.status_code == 403
    assert op_response.get_json()["error"] == "insufficient_permissions"

    # Admin acessando -> 200 OK
    admin_response = client.get("/api/v1/admin/audit-logs", headers=admin_auth_headers)
    assert admin_response.status_code == 200
    assert "items" in admin_response.get_json()


def test_email_analysis_masks_pii_and_creates_audit_log(client, auth_headers):
    """Testa se a análise de email mascara PII e gera registro de auditoria."""
    payload = {
        "text": "Solicito pagamento referente ao CPF 123.456.789-00 e cartão 5555 4444 3333 2222.",
    }
    response = client.post("/api/v1/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["pii_masked"] is True

    # Verificar audit log criado mais recente
    audit = AuditLog.query.filter_by(action="email.analyze").order_by(AuditLog.id.desc()).first()
    assert audit is not None
    assert audit.details["pii_masked"] is True
