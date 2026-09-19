"""
Testes unitários para o parser de RFC822 / .eml.
"""
from backend.app.utils.email_parser import parse_eml


def test_parse_simple_plain_eml():
    raw_eml = """From: cliente@banco.com
To: suporte@fintech.com
Subject: Solicitação de Extrato
Date: Sat, 19 Sep 2026 10:00:00 -0300
Message-ID: <msg-12345@banco.com>
Content-Type: text/plain; charset="utf-8"

Olá, gostaria de solicitar o extrato consolidado do mês de agosto referente à conta 12345.
"""
    result = parse_eml(raw_eml)
    assert result["subject"] == "Solicitação de Extrato"
    assert "cliente@banco.com" in result["from"]
    assert "suporte@fintech.com" in result["to"]
    assert result["message_id"] == "<msg-12345@banco.com>"
    assert "extrato consolidado" in result["full_text"]


def test_parse_multipart_with_attachment():
    raw_eml = """From: faturamento@fornecedor.com
To: contas@empresa.com
Subject: Fatura 9988 Anexa
Date: Sat, 19 Sep 2026 12:00:00 -0300
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset="utf-8"

Segue em anexo a fatura para pagamento até 30/09/2026 no valor de R$ 5.000,00.

--boundary123
Content-Type: application/pdf; name="fatura_9988.pdf"
Content-Disposition: attachment; filename="fatura_9988.pdf"
Content-Transfer-Encoding: base64

JVBERi0xLjQKJcTl8uXr...
--boundary123--
"""
    result = parse_eml(raw_eml)
    assert result["subject"] == "Fatura 9988 Anexa"
    assert len(result["attachments"]) == 1
    assert result["attachments"][0]["filename"] == "fatura_9988.pdf"
    assert result["attachments"][0]["content_type"] == "application/pdf"
