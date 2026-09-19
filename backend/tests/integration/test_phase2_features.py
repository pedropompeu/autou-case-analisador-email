"""
Testes de integração para as funcionalidades da Fase 2:
- Webhooks de Saída Assíncronos (#26)
- Ingestão de emails RFC822 / .eml (#23)
- API pública B2B com API Keys (#27)
"""
import io


def test_webhook_crud_and_listing(client, auth_headers):
    """Testa cadastro, listagem e exclusão de webhooks (#26)."""
    # 1. Cadastrar
    payload = {
        "url": "https://webhook.site/fake-endpoint",
        "events": ["email.analyzed", "quarantine.flagged"],
        "description": "Integração ERP Financeiro",
    }
    create_resp = client.post("/api/v1/webhooks", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    wh_data = create_resp.get_json()["webhook"]
    assert "secret" in wh_data
    assert wh_data["secret"].startswith("whsec_")
    webhook_id = wh_data["id"]

    # 2. Listar
    list_resp = client.get("/api/v1/webhooks", headers=auth_headers)
    assert list_resp.status_code == 200
    webhooks = list_resp.get_json()["webhooks"]
    assert any(w["id"] == webhook_id for w in webhooks)

    # 3. Deletar
    del_resp = client.delete(f"/api/v1/webhooks/{webhook_id}", headers=auth_headers)
    assert del_resp.status_code == 200


def test_ingest_eml_endpoint(client, auth_headers):
    """Testa ingestão e análise de arquivo .eml (#23)."""
    eml_content = b"""From: tesouraria@cliente.com
To: atendimento@saas.com
Subject: Comprovante de Pagamento Anual
Date: Sat, 19 Sep 2026 14:00:00 -0300
Content-Type: text/plain; charset="utf-8"

Prezados, segue comprovante de pagamento no valor de R$ 12.000,00 referente ao contrato anual com vencimento em 19/09/2026.
"""
    data = {
        "file": (io.BytesIO(eml_content), "comprovante.eml"),
    }
    response = client.post(
        "/api/v1/ingest/eml",
        data=data,
        content_type="multipart/form-data",
        headers=auth_headers,
    )
    assert response.status_code == 200
    res_json = response.get_json()
    assert res_json["email_metadata"]["subject"] == "Comprovante de Pagamento Anual"
    assert "analysis" in res_json
    assert res_json["analysis"]["categoria"] is not None
