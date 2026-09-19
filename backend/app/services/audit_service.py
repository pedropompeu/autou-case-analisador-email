"""
Serviço de Trilha de Auditoria Imutável (Audit Trail).
Registra ações de segurança, compliance e operações de negócio.
"""
import json
import logging
from typing import Any, Dict, Optional

from flask import has_request_context, request

from backend.app import db
from backend.app.models.audit_log import AuditLog
from backend.app.utils.rbac import get_current_user
from backend.app.utils.tenant_context import get_current_tenant_id

logger = logging.getLogger("audit")


class AuditService:
    """Serviço para registro imutável de eventos de auditoria."""

    @staticmethod
    def log(
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
    ) -> Optional[AuditLog]:
        """
        Registra um evento de auditoria no banco e no logger estruturado.

        Args:
            action: Nome da ação (ex: 'auth.login', 'email.analyze', 'user.role_change')
            resource_type: Tipo do recurso envolvido ('EmailAnalysis', 'User', etc.)
            resource_id: Identificador do recurso
            details: Metadados contextuais adicionais
            user_id: ID do usuário (inferido do contexto se None)
            tenant_id: ID do tenant (inferido do contexto se None)
        """
        ip_address = None
        user_agent = None

        if has_request_context():
            ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
            if ip_address and "," in ip_address:
                ip_address = ip_address.split(",")[0].strip()
            user_agent = request.headers.get("User-Agent", "")[:255]

            if user_id is None:
                user = get_current_user()
                if user:
                    user_id = user.id

            if tenant_id is None:
                tenant_id = get_current_tenant_id()

        audit_entry = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )

        try:
            db.session.add(audit_entry)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to persist audit log entry: {e}")
            db.session.rollback()

        # Emitir log estruturado JSON
        logger.info(
            json.dumps(
                {
                    "event": "audit_event",
                    "action": action,
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "ip": ip_address,
                    "details": details or {},
                }
            )
        )

        return audit_entry
