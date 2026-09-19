"""
Testes de integração para as funcionalidades da Fase 4 (Workflows, Notas Internas, Status e Regras).
"""
import uuid
import pytest
from flask_jwt_extended import create_access_token

from backend.app import db
from backend.app.models.tenant import Tenant
from backend.app.models.user import User
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.routing_rule import RoutingRule


@pytest.fixture
def phase4_setup(app):
    with app.app_context():
        uid = uuid.uuid4().hex[:8]
        tenant = Tenant(name=f"Phase 4 Corp {uid}", slug=f"p4-corp-{uid}", plan="enterprise")
        db.session.add(tenant)
        db.session.commit()

        admin_user = User(username=f"admin_p4_{uid}", email=f"admin_{uid}@test.com", role="admin", tenant_id=tenant.id)
        admin_user.set_password("pass123")
        operator_user = User(username=f"op_p4_{uid}", email=f"op_{uid}@test.com", role="operator", tenant_id=tenant.id)
        operator_user.set_password("pass123")
        db.session.add_all([admin_user, operator_user])
        db.session.commit()

        admin_token = create_access_token(
            identity=admin_user.username,
            additional_claims={"user_id": admin_user.id, "tenant_id": tenant.id, "role": admin_user.role}
        )
        op_token = create_access_token(
            identity=operator_user.username,
            additional_claims={"user_id": operator_user.id, "tenant_id": tenant.id, "role": operator_user.role}
        )

        return {
            "tenant": tenant,
            "admin_user": admin_user,
            "operator_user": operator_user,
            "admin_headers": {"Authorization": f"Bearer {admin_token}"},
            "op_headers": {"Authorization": f"Bearer {op_token}"}
        }


def test_internal_notes_workflow(client, phase4_setup):
    headers = phase4_setup["op_headers"]
    tenant_id = phase4_setup["tenant"].id

    analysis = EmailAnalysis(
        email_content="Solicitação de renegociação de dívida",
        summary="Renegociação",
        suggested_response="Resposta",
        content_hash=f"hash_note_{uuid.uuid4().hex[:6]}",
        category="Produtivo",
        tenant_id=tenant_id
    )
    db.session.add(analysis)
    db.session.commit()

    # 1. Adicionar nota interna
    add_resp = client.post(
        f"/api/v1/analyze/{analysis.id}/notes",
        json={"content": "Cliente já possui proposta pré-aprovada de 15% de desconto no CRM."},
        headers=headers
    )
    assert add_resp.status_code == 201
    add_data = add_resp.get_json()
    assert add_data["note"]["content"] == "Cliente já possui proposta pré-aprovada de 15% de desconto no CRM."

    # 2. Listar notas internas
    list_resp = client.get(f"/api/v1/analyze/{analysis.id}/notes", headers=headers)
    assert list_resp.status_code == 200
    list_data = list_resp.get_json()
    assert len(list_data["notes"]) == 1
    assert list_data["notes"][0]["content"] == "Cliente já possui proposta pré-aprovada de 15% de desconto no CRM."


def test_status_and_assignment_workflow(client, phase4_setup):
    headers = phase4_setup["admin_headers"]
    tenant_id = phase4_setup["tenant"].id
    operator_user = phase4_setup["operator_user"]

    analysis = EmailAnalysis(
        email_content="Email para triagem e atribuição",
        summary="Triagem",
        suggested_response="Resposta",
        content_hash=f"hash_assign_{uuid.uuid4().hex[:6]}",
        category="Produtivo",
        status="pending",
        tenant_id=tenant_id
    )
    db.session.add(analysis)
    db.session.commit()

    # 1. Atualizar status para in_progress
    status_resp = client.patch(
        f"/api/v1/analyze/{analysis.id}/status",
        json={"status": "in_progress"},
        headers=headers
    )
    assert status_resp.status_code == 200
    assert status_resp.get_json()["status"] == "in_progress"

    # 2. Atribuir ao operador
    assign_resp = client.patch(
        f"/api/v1/analyze/{analysis.id}/assign",
        json={"user_id": operator_user.id},
        headers=headers
    )
    assert assign_resp.status_code == 200
    assert assign_resp.get_json()["assigned_to_user_id"] == operator_user.id


def test_routing_rules_crud(client, phase4_setup):
    admin_headers = phase4_setup["admin_headers"]
    op_headers = phase4_setup["op_headers"]

    # 1. Criar regra de automação (Admin)
    rule_data = {
        "name": "Auto Quarentena para Baixa Confiança",
        "description": "Retém análises com score < 0.7",
        "condition_field": "confidence_score",
        "condition_operator": "lte",
        "condition_value": "0.7",
        "action_type": "set_quarantine",
        "priority": 10
    }
    create_resp = client.post("/api/v1/routing-rules", json=rule_data, headers=admin_headers)
    assert create_resp.status_code == 201
    rule_id = create_resp.get_json()["rule"]["id"]

    # 2. Operador não pode criar regra (RBAC 403)
    forbidden_resp = client.post("/api/v1/routing-rules", json=rule_data, headers=op_headers)
    assert forbidden_resp.status_code == 403

    # 3. Listar regras
    list_resp = client.get("/api/v1/routing-rules", headers=admin_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.get_json()["rules"]) >= 1

    # 4. Deletar regra
    del_resp = client.delete(f"/api/v1/routing-rules/{rule_id}", headers=admin_headers)
    assert del_resp.status_code == 200
