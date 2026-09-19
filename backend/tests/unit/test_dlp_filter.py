"""
Testes unitários para o Outbound DLP Filter (Data Loss Prevention).
"""

from backend.app.utils.dlp_filter import check_dlp_violations, sanitize_outbound_response


def test_dlp_filter_api_key_detection():
    text = "Use sua chave ak_live_12345678901234567890 para testar a integração."
    violations = check_dlp_violations(text)
    assert len(violations) > 0
    assert any(v["rule"] == "api_key" for v in violations)

    sanitized = sanitize_outbound_response(text)
    assert "ak_live_" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized


def test_dlp_filter_internal_ip():
    text = "O servidor interno responde no endereço 192.168.1.100 ou 10.0.0.50 com segurança."
    sanitized = sanitize_outbound_response(text)
    assert "192.168.1.100" not in sanitized
    assert "10.0.0.50" not in sanitized
    assert "[REDACTED_INTERNAL_IP]" in sanitized


def test_dlp_filter_database_url():
    text = "Conecte-se em postgresql://admin:secret123@db-internal:5432/production_db para ver os dados."
    sanitized = sanitize_outbound_response(text)
    assert "postgresql://" not in sanitized
    assert "secret123" not in sanitized
    assert "[REDACTED_DATABASE_URI]" in sanitized


def test_dlp_filter_clean_text():
    text = "Prezado cliente, seu comprovante de pagamento referente ao contrato 45892 foi recebido com sucesso."
    violations = check_dlp_violations(text)
    assert len(violations) == 0

    sanitized = sanitize_outbound_response(text)
    assert sanitized == text
