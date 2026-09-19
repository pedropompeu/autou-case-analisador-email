"""
Testes de integração para as funcionalidades da Fase 3 (LGPD, Retenção, DLP e ROI Stats).
"""
import pytest
from backend.app import db
from backend.app.models.tenant import Tenant
from backend.app.models.user import User
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.feedback import AnalysisFeedback
from flask_jwt_extended import create_access_token


import uuid


@pytest.fixture
def phase3_setup(app):
    with app.app_context():
        uid = uuid.uuid4().hex[:8]
        tenant = Tenant(name=f"Phase 3 Corp {uid}", slug=f"p3-corp-{uid}", plan="enterprise", settings={"retention_days": 60})
        db.session.add(tenant)
        db.session.commit()

        admin_user = User(username=f"admin_{uid}", email=f"admin_{uid}@test.com", role="admin", tenant_id=tenant.id)
        admin_user.set_password("pass123")
        operator_user = User(username=f"op_{uid}", email=f"op_{uid}@test.com", role="operator", tenant_id=tenant.id)
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
            "admin_headers": {"Authorization": f"Bearer {admin_token}"},
            "op_headers": {"Authorization": f"Bearer {op_token}"}
        }


def test_compliance_export_endpoint(client, phase3_setup):
    headers = phase3_setup["admin_headers"]
    tenant_id = phase3_setup["tenant"].id

    # Criar análise
    analysis = EmailAnalysis(
        email_content="Solicitação de cancelamento de maria.oliveira@banco.com",
        summary="Cancelamento",
        content_hash="hash_p3_export",
        category="Produtivo",
        suggested_response="Prezada Maria, cancelamento efetuado.",
        sentiment="Neutro",
        urgency="Media",
        tenant_id=tenant_id
    )
    db.session.add(analysis)
    db.session.commit()

    response = client.post(
        "/api/v1/compliance/export",
        json={"identifier": "maria.oliveira@banco.com"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["total_records_found"] == 1
    assert data["records"][0]["id"] == analysis.id


def test_compliance_erasure_endpoint(client, phase3_setup):
    headers = phase3_setup["admin_headers"]
    tenant_id = phase3_setup["tenant"].id

    analysis = EmailAnalysis(
        email_content="Dados confidenciais de roberto.souza@fintech.com",
        summary="Dados confidenciais",
        content_hash="hash_p3_erasure",
        category="Produtivo",
        suggested_response="Resposta enviada a roberto.souza@fintech.com",
        tenant_id=tenant_id
    )
    db.session.add(analysis)
    db.session.commit()

    response = client.post(
        "/api/v1/compliance/erasure",
        json={"identifier": "roberto.souza@fintech.com"},
        headers=headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["records_anonymized"] == 1

    db.session.refresh(analysis)
    assert "roberto.souza@fintech.com" not in analysis.email_content
    assert "[LGPD_ANONYMIZED]" in analysis.email_content


def test_compliance_rbac_forbidden_for_operator(client, phase3_setup):
    headers = phase3_setup["op_headers"]

    # Operador comum não tem permissão para expurgar dados
    response = client.post(
        "/api/v1/compliance/erasure",
        json={"identifier": "teste@exemplo.com"},
        headers=headers
    )
    assert response.status_code == 403


def test_stats_with_roi_and_breakdowns(client, phase3_setup):
    headers = phase3_setup["admin_headers"]
    tenant_id = phase3_setup["tenant"].id

    analysis1 = EmailAnalysis(
        email_content="Email urgente sobre boleto vencido",
        summary="Boleto vencido",
        suggested_response="Resposta ao boleto vencido",
        content_hash="hash_p3_stats1",
        category="Produtivo",
        sentiment="Irritado",
        urgency="Alta",
        in_quarantine=False,
        processing_time_ms=450,
        tenant_id=tenant_id
    )
    analysis2 = EmailAnalysis(
        email_content="Parabéns pelo excelente atendimento",
        summary="Elogio",
        suggested_response="Obrigado pelo elogio",
        content_hash="hash_p3_stats2",
        category="Produtivo",
        sentiment="Positivo",
        urgency="Baixa",
        in_quarantine=False,
        processing_time_ms=320,
        tenant_id=tenant_id
    )
    analysis3 = EmailAnalysis(
        email_content="Email com baixa confiança e suspeita de fraude",
        summary="Suspeita",
        suggested_response="Mensagem retida para análise de fraude",
        content_hash="hash_p3_stats3",
        category="Improdutivo",
        sentiment="Negativo",
        urgency="Critica",
        in_quarantine=True,
        processing_time_ms=500,
        tenant_id=tenant_id
    )
    db.session.add_all([analysis1, analysis2, analysis3])
    db.session.commit()

    # Feedback
    fb1 = AnalysisFeedback(analysis_id=analysis1.id, approved=True, tenant_id=tenant_id)
    fb2 = AnalysisFeedback(analysis_id=analysis2.id, approved=False, notes="Corrigido", tenant_id=tenant_id)
    db.session.add_all([fb1, fb2])
    db.session.commit()

    response = client.get("/api/v1/stats?hourly_rate=50.0&minutes_saved=3.0", headers=headers)
    assert response.status_code == 200
    data = response.get_json()

    assert data["total_analyses"] == 3
    assert data["productive_count"] == 2
    assert data["unproductive_count"] == 1
    assert data["quarantined_count"] == 1
    assert data["total_feedbacks"] == 2
    assert data["approved_count"] == 1
    assert data["accuracy_rate"] == 50.0
    assert "sentiment_breakdown" in data
    assert data["sentiment_breakdown"].get("Irritado") == 1
    assert "urgency_breakdown" in data
    assert data["urgency_breakdown"].get("Alta") == 1
    assert data["time_saved_estimate_hours"] > 0
    assert data["estimated_savings_brl"] > 0
