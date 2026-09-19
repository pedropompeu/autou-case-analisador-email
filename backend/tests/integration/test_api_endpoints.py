"""
Testes de integração para endpoints da API.
"""
import pytest
import json


def test_health_endpoint(client):
    """Testa endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["status"] in ["healthy", "unhealthy"]
    assert "version" in data


def test_api_v1_health(client):
    """Testa health check da API v1."""
    response = client.get("/api/v1/health")
    assert response.status_code in [200, 503]

    data = json.loads(response.data)
    assert "status" in data
    assert "checks" in data


def test_analyze_endpoint_valid_input(client, auth_headers):
    """Testa análise com input válido."""
    payload = {"text": "Olá, preciso de ajuda com meu projeto de software."}

    response = client.post(
        "/api/v1/analyze",
        data=json.dumps(payload),
        content_type="application/json",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = json.loads(response.data)
    assert "categoria" in data
    assert "resumo" in data
    assert "sugestao_resposta" in data


def test_analyze_endpoint_invalid_input(client, auth_headers):
    """Testa análise com input inválido."""
    payload = {"text": "abc"}  # Muito curto (min 10 chars)

    response = client.post(
        "/api/v1/analyze",
        data=json.dumps(payload),
        content_type="application/json",
        headers=auth_headers,
    )

    assert response.status_code == 400

    data = json.loads(response.data)
    assert "error" in data


def test_analyze_endpoint_missing_text(client, auth_headers):
    """Testa análise sem campo text."""
    payload = {}

    response = client.post(
        "/api/v1/analyze",
        data=json.dumps(payload),
        content_type="application/json",
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_api_status_endpoint(client):
    """Testa endpoint de status da API."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert data["api_version"] == "v1"
    assert "endpoints" in data
