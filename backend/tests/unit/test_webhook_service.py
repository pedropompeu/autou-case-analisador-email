"""
Testes unitários para o serviço de Webhooks e assinatura HMAC.
"""
from backend.app.services.webhook_service import WebhookService


def test_webhook_hmac_signature_generation():
    secret = "whsec_test_secret_key_12345"
    payload = '{"event": "email.analyzed", "data": {"id": 1}}'
    timestamp = 1789834000

    sig = WebhookService.generate_signature(secret, payload, timestamp)
    assert sig.startswith(f"t={timestamp},v1=")
    assert len(sig.split("v1=")[1]) == 64  # SHA-256 hex digest length
