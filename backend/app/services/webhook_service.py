"""
Serviço para Despacho e Assinatura Criptográfica de Webhooks de Saída (#26).
"""
import hmac
import hashlib
import time
import json
import logging
from typing import Optional, Dict, Any
import urllib.request
import urllib.error

from backend.app import db
from backend.app.models.webhook import WebhookSubscription, WebhookDelivery

logger = logging.getLogger("webhooks")


class WebhookService:
    """Serviço para gerenciamento e disparo seguro de Webhooks corporativos."""

    @staticmethod
    def generate_signature(secret: str, payload_str: str, timestamp: int) -> str:
        """
        Gera assinatura HMAC-SHA256 no padrão Stripe/GitHub para verificação pelo cliente.
        Header: t=<timestamp>,v1=<signature>
        """
        signed_payload = f"{timestamp}.{payload_str}".encode("utf-8")
        signature = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={signature}"

    @classmethod
    def dispatch_event(cls, tenant_id: Optional[int], event: str, payload: Dict[str, Any]) -> int:
        """
        Identifica assinaturas ativas para o evento e tenant e agenda o disparo.
        Retorna o número de webhooks acionados.
        """
        if tenant_id is None:
            return 0

        subscriptions = WebhookSubscription.query.filter_by(
            tenant_id=tenant_id, is_active=True, is_deleted=False
        ).all()

        dispatched_count = 0
        for sub in subscriptions:
            # Verifica se o evento está assinado ou se assina todos com wildcard '*'
            if "*" in sub.events or event in sub.events:
                # Disparo síncrono/assíncrono direto
                cls.deliver_webhook(sub.id, event, payload)
                dispatched_count += 1

        return dispatched_count

    @classmethod
    def deliver_webhook(
        cls, subscription_id: int, event: str, payload: Dict[str, Any], timeout: int = 5
    ) -> WebhookDelivery:
        """
        Executa a requisição HTTP POST ao endpoint do cliente com assinatura HMAC e headers.
        """
        sub = WebhookSubscription.query.filter_by(id=subscription_id, is_deleted=False).first()
        if not sub:
            raise ValueError(f"WebhookSubscription {subscription_id} not found.")

        timestamp = int(time.time())
        payload_data = {
            "event": event,
            "created_at": timestamp,
            "tenant_id": sub.tenant_id,
            "data": payload,
        }
        payload_str = json.dumps(payload_data, ensure_ascii=False)
        signature_header = cls.generate_signature(sub.secret, payload_str, timestamp)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AutoU-EmailAnalyzer-Webhook/1.0",
            "X-Webhook-Signature": signature_header,
            "X-Webhook-Event": event,
        }

        req = urllib.request.Request(
            url=sub.url,
            data=payload_str.encode("utf-8"),
            headers=headers,
            method="POST",
        )

        status_code = None
        response_body = ""
        success = False

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status_code = resp.getcode()
                response_body = resp.read().decode("utf-8", errors="ignore")[:2000]
                success = 200 <= status_code < 300
        except urllib.error.HTTPError as e:
            status_code = e.code
            response_body = e.read().decode("utf-8", errors="ignore")[:2000]
        except Exception as e:
            status_code = 0
            response_body = str(e)[:1000]
            logger.warning(f"Webhook delivery failed for URL {sub.url}: {e}")

        # Gravar log de entrega
        delivery = WebhookDelivery(
            subscription_id=sub.id,
            tenant_id=sub.tenant_id,
            event=event,
            payload=payload_data,
            status_code=status_code,
            response_body=response_body,
            attempt=1,
            success=success,
        )

        try:
            db.session.add(delivery)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to record webhook delivery log: {e}")
            db.session.rollback()

        return delivery
