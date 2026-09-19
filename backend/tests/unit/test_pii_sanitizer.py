"""
Testes unitários para o módulo de mascaramento de PII.
"""
from backend.app.utils.pii_sanitizer import sanitize_pii


def test_sanitize_cpf():
    text = "Meu CPF é 123.456.789-00 para emitir o boleto."
    sanitized, meta = sanitize_pii(text)
    assert "[CPF_MASCARADO_1]" in sanitized
    assert "123.456.789-00" not in sanitized
    assert meta["masked"] is True
    assert meta["counts"]["cpf"] == 1


def test_sanitize_cnpj():
    text = "Faturamento para a empresa com CNPJ 12.345.678/0001-90."
    sanitized, meta = sanitize_pii(text)
    assert "[CNPJ_MASCARADO_1]" in sanitized
    assert "12.345.678/0001-90" not in sanitized
    assert meta["masked"] is True
    assert meta["counts"]["cnpj"] == 1


def test_sanitize_credit_card():
    text = "Cobrança no cartão 4532 1234 5678 9010 urgente."
    sanitized, meta = sanitize_pii(text)
    assert "[CARTAO_CREDITO_MASCARADO_1]" in sanitized
    assert "4532 1234 5678 9010" not in sanitized
    assert meta["masked"] is True
    assert meta["counts"]["credit_card"] == 1


def test_sanitize_pix_key_and_bank():
    text = "Segue chave PIX: 123e4567-e89b-12d3-a456-426614174000 e Agência: 1234 Conta: 56789-0."
    sanitized, meta = sanitize_pii(text)
    assert "[CHAVE_PIX_MASCARADA_1]" in sanitized
    assert "[DADOS_BANCARIOS_MASCARADOS_1]" in sanitized
    assert meta["masked"] is True


def test_no_pii_present():
    text = "Bom dia, gostaria de solicitar uma proposta comercial para 50 usuários."
    sanitized, meta = sanitize_pii(text)
    assert sanitized == text
    assert meta["masked"] is False
    assert meta["total_items_masked"] == 0
