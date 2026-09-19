"""
Rotas para Gerenciamento de Webhooks de Saída (Outbound Webhooks) (#26).
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from backend.app import db
from backend.app.models.webhook import WebhookSubscription, WebhookDelivery
from backend.app.utils.tenant_context import get_current_tenant_id
from backend.app.services.webhook_service import WebhookService
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

webhook_bp = Blueprint("webhooks", __name__)


@webhook_bp.route("", methods=["GET"])
@jwt_required()
def list_webhooks():
    """Lista todas as assinaturas de webhook do tenant atual."""
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return jsonify({"error": "No tenant associated"}), 400

    subscriptions = WebhookSubscription.query.filter_by(
        tenant_id=tenant_id, is_deleted=False
    ).all()

    return jsonify({
        "webhooks": [
            {
                "id": s.id,
                "url": s.url,
                "events": s.events,
                "is_active": s.is_active,
                "description": s.description,
                "created_at": s.created_at.isoformat(),
            }
            for s in subscriptions
        ]
    }), 200


@webhook_bp.route("", methods=["POST"])
@jwt_required()
def create_webhook():
    """Cadastra um novo endpoint de webhook com geração de segredo HMAC."""
    tenant_id = get_current_tenant_id()
    if tenant_id is None:
        return jsonify({"error": "No tenant associated"}), 400

    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return jsonify({"error": "Valid HTTP/HTTPS URL is required"}), 400

    events = data.get("events") or ["email.analyzed"]
    secret = WebhookSubscription.generate_secret()

    subscription = WebhookSubscription(
        tenant_id=tenant_id,
        url=url,
        secret=secret,
        events=events,
        description=data.get("description"),
    )
    db.session.add(subscription)
    db.session.commit()

    AuditService.log(
        action="webhook.create",
        resource_type="WebhookSubscription",
        resource_id=str(subscription.id),
        details={"url": url, "events": events},
        tenant_id=tenant_id,
    )

    return jsonify({
        "message": "Webhook created successfully",
        "webhook": {
            "id": subscription.id,
            "url": subscription.url,
            "secret": subscription.secret,  # Exibido apenas na criação para segurança
            "events": subscription.events,
        }
    }), 201


@webhook_bp.route("/<int:webhook_id>", methods=["DELETE"])
@jwt_required()
def delete_webhook(webhook_id):
    """Remove uma assinatura de webhook."""
    tenant_id = get_current_tenant_id()
    subscription = WebhookSubscription.query.filter_by(
        id=webhook_id, tenant_id=tenant_id, is_deleted=False
    ).first()

    if not subscription:
        return jsonify({"error": "Webhook not found"}), 404

    subscription.soft_delete()

    AuditService.log(
        action="webhook.delete",
        resource_type="WebhookSubscription",
        resource_id=str(webhook_id),
        tenant_id=tenant_id,
    )

    return jsonify({"message": "Webhook deleted successfully"}), 200


@webhook_bp.route("/<int:webhook_id>/test", methods=["POST"])
@jwt_required()
def test_webhook(webhook_id):
    """Dispara um evento de teste ('webhook.test') para o endpoint cadastrado."""
    tenant_id = get_current_tenant_id()
    subscription = WebhookSubscription.query.filter_by(
        id=webhook_id, tenant_id=tenant_id, is_deleted=False
    ).first()

    if not subscription:
        return jsonify({"error": "Webhook not found"}), 404

    test_payload = {
        "message": "This is a test notification from AutoU Email Analyzer",
        "sample_data": {"category": "Produtivo", "urgency": "Alta"},
    }

    delivery = WebhookService.deliver_webhook(
        subscription_id=subscription.id,
        event="webhook.test",
        payload=test_payload,
    )

    return jsonify({
        "message": "Test webhook dispatched",
        "status_code": delivery.status_code,
        "success": delivery.success,
        "response_body": delivery.response_body,
    }), 200


@webhook_bp.route("/<int:webhook_id>/deliveries", methods=["GET"])
@jwt_required()
def list_deliveries(webhook_id):
    """Lista as últimas tentativas de entrega de um webhook para diagnóstico."""
    tenant_id = get_current_tenant_id()
    deliveries = (
        WebhookDelivery.query.filter_by(subscription_id=webhook_id, tenant_id=tenant_id)
        .order_by(WebhookDelivery.created_at.desc())
        .limit(20)
        .all()
    )

    return jsonify({
        "deliveries": [
            {
                "id": d.id,
                "event": d.event,
                "status_code": d.status_code,
                "success": d.success,
                "created_at": d.created_at.isoformat(),
            }
            for d in deliveries
        ]
    }), 200
