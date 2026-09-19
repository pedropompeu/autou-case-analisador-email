"""
Testes de integração para as funcionalidades de IA da Fase 1:
- Sentimento e Urgência (#4)
- Extração de Entidades / NER (#3)
- Detecção de Fraude e Quarentena de Baixa Confiança (#6, #14)
- Múltiplos Tons de Resposta (#8)
- Categorias Dinâmicas por Tenant (#16)
- Memória de Thread (#7)
"""


def test_advanced_email_analysis_fields(client, auth_headers):
    """Testa se a análise retorna campos avançados da Fase 1."""
    payload = {
        "text": "Solicito com urgência máxima a liberação do pagamento da fatura no valor de R$ 45.000,00 com vencimento em 15/10/2026.",
        "tone": "empatico",
    }
    response = client.post("/api/v1/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()

    assert "categoria" in data
    assert "sentimento" in data
    assert "urgencia" in data
    assert "score_confianca" in data
    assert "risco_fraude" in data
    assert "entidades" in data
    assert data["tone"] == "empatico"
    assert "in_quarantine" in data


def test_regenerate_response_tone(client, auth_headers):
    """Testa regeneração de tom de resposta (#8)."""
    # 1. Cria análise inicial
    init_payload = {"text": "Gostaria de solicitar o cancelamento da minha conta."}
    init_resp = client.post("/api/v1/analyze", json=init_payload, headers=auth_headers)
    assert init_resp.status_code == 200
    analysis_id = init_resp.get_json()["id"]

    # 2. Regenera no tom Jurídico
    regen_resp = client.post(
        f"/api/v1/analyze/{analysis_id}/regenerate-response",
        json={"tone": "juridico"},
        headers=auth_headers,
    )
    assert regen_resp.status_code == 200
    regen_data = regen_resp.get_json()
    assert regen_data["tone"] == "juridico"
    assert "sugestao_resposta" in regen_data


def test_dynamic_categories_crud(client, auth_headers):
    """Testa criação e listagem de categorias dinâmicas por tenant (#16)."""
    # 1. Listar inicialmente
    list_resp = client.get("/api/v1/categories", headers=auth_headers)
    assert list_resp.status_code == 200
    initial_count = len(list_resp.get_json()["categories"])

    # 2. Criar nova categoria
    create_payload = {
        "name": "Disputa de Pagamento",
        "description": "Contestações de cobrança e chargebacks",
        "action_required": True,
    }
    create_resp = client.post("/api/v1/categories", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    created_cat = create_resp.get_json()["category"]
    assert created_cat["name"] == "Disputa de Pagamento"

    # 3. Listar novamente e confirmar inclusão
    after_resp = client.get("/api/v1/categories", headers=auth_headers)
    assert after_resp.status_code == 200
    assert len(after_resp.get_json()["categories"]) == initial_count + 1


def test_thread_context_analysis(client, auth_headers):
    """Testa análise de mensagens consecutivas com thread_id (#7)."""
    thread_id = "thread-b2b-invoice-9988"

    # Mensagem 1
    resp1 = client.post(
        "/api/v1/analyze",
        json={"text": "Enviamos o contrato para revisão jurídica.", "thread_id": thread_id},
        headers=auth_headers,
    )
    assert resp1.status_code == 200

    # Mensagem 2 (continuação da mesma thread)
    resp2 = client.post(
        "/api/v1/analyze",
        json={"text": "Ok, recebido. Encaminhamos para assinatura.", "thread_id": thread_id},
        headers=auth_headers,
    )
    assert resp2.status_code == 200
    assert resp2.get_json()["categoria"] is not None
