"""
Serviço de conformidade e governança de dados (LGPD / GDPR).
Suporta Direito ao Esquecimento, Exportação de Dados do Titular e Políticas de Retenção.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy import or_

from backend.app import db
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.feedback import AnalysisFeedback
from backend.app.models.tenant import Tenant
from backend.app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class ComplianceService:
    """Gerencia requisições de privacidade, LGPD e expurgo de dados."""

    @staticmethod
    def export_subject_data(
        tenant_id: int, subject_identifier: str, requester_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Exporta todos os dados vinculados a um titular (email ou documento) dentro do tenant (LGPD Art. 19).
        """
        logger.info(f"Exporting LGPD data for subject '{subject_identifier}' on tenant {tenant_id}")

        # Busca registros onde o identificador aparece no texto, resposta ou entidades
        query = EmailAnalysis.query.filter(
            EmailAnalysis.tenant_id == tenant_id,
            EmailAnalysis.is_deleted.is_(False),
            or_(
                EmailAnalysis.email_content.ilike(f"%{subject_identifier}%"),
                EmailAnalysis.suggested_response.ilike(f"%{subject_identifier}%"),
                EmailAnalysis.category.ilike(f"%{subject_identifier}%"),
            ),
        )
        analyses = query.all()

        analyses_data = []
        for item in analyses:
            feedbacks = AnalysisFeedback.query.filter_by(
                tenant_id=tenant_id, analysis_id=item.id, is_deleted=False
            ).all()

            analyses_data.append(
                {
                    "id": item.id,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "category": item.category,
                    "sentiment": item.sentiment,
                    "urgency": item.urgency,
                    "email_content": item.email_content,
                    "suggested_response": item.suggested_response,
                    "extracted_entities": item.extracted_entities,
                    "confidence_score": item.confidence_score,
                    "feedbacks": [
                        {
                            "id": fb.id,
                            "approved": fb.approved,
                            "notes": fb.notes,
                            "created_at": fb.created_at.isoformat() if fb.created_at else None,
                        }
                        for fb in feedbacks
                    ],
                }
            )

        result = {
            "subject_identifier": subject_identifier,
            "tenant_id": tenant_id,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_records_found": len(analyses_data),
            "records": analyses_data,
        }

        # Auditoria imutável
        AuditService.log(
            action="compliance.lgpd_export",
            resource_type="subject",
            resource_id=subject_identifier,
            details={"records_exported": len(analyses_data)},
            user_id=requester_user_id,
            tenant_id=tenant_id,
        )

        return result

    @staticmethod
    def erase_subject_data(
        tenant_id: int, subject_identifier: str, requester_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Anonimiza irreversivelmente os dados do titular atendendo ao Direito ao Esquecimento (LGPD Art. 18, VI).
        """
        logger.info(
            f"Executing LGPD erasure for subject '{subject_identifier}' on tenant {tenant_id}"
        )

        query = EmailAnalysis.query.filter(
            EmailAnalysis.tenant_id == tenant_id,
            EmailAnalysis.is_deleted.is_(False),
            or_(
                EmailAnalysis.email_content.ilike(f"%{subject_identifier}%"),
                EmailAnalysis.suggested_response.ilike(f"%{subject_identifier}%"),
            ),
        )
        analyses = query.all()

        modified_count = 0
        for item in analyses:
            # Substitui menções ao titular por máscara irreversível
            if item.email_content:
                item.email_content = item.email_content.replace(
                    subject_identifier, "[LGPD_ANONYMIZED]"
                )
            if item.suggested_response:
                item.suggested_response = item.suggested_response.replace(
                    subject_identifier, "[LGPD_ANONYMIZED]"
                )

            # Limpa entidades extraídas que possam conter o titular
            if item.extracted_entities and isinstance(item.extracted_entities, dict):
                cleaned_entities: Dict[str, Any] = {}
                for k, v in item.extracted_entities.items():
                    if isinstance(v, str) and subject_identifier in v:
                        cleaned_entities[k] = "[LGPD_ANONYMIZED]"
                    elif isinstance(v, list):
                        cleaned_entities[k] = [
                            "[LGPD_ANONYMIZED]"
                            if (isinstance(elem, str) and subject_identifier in elem)
                            else elem
                            for elem in v
                        ]
                    else:
                        cleaned_entities[k] = v
                item.extracted_entities = cleaned_entities

            modified_count += 1

        db.session.commit()

        # Auditoria imutável
        AuditService.log(
            action="compliance.lgpd_erasure",
            resource_type="subject",
            resource_id=subject_identifier,
            details={"records_anonymized": modified_count},
            user_id=requester_user_id,
            tenant_id=tenant_id,
        )

        return {
            "status": "success",
            "subject_identifier": subject_identifier,
            "tenant_id": tenant_id,
            "anonymized_at": datetime.now(timezone.utc).isoformat(),
            "records_anonymized": modified_count,
        }

    @staticmethod
    def run_retention_cleanup(
        tenant_id: int,
        retention_days: Optional[int] = None,
        requester_user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Executa expurgo/anonimização de registros de análise anteriores à política de retenção do tenant.
        """
        tenant = db.session.get(Tenant, tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        if retention_days is None:
            settings = tenant.settings or {}
            retention_days = int(settings.get("retention_days", 90))

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        old_records = EmailAnalysis.query.filter(
            EmailAnalysis.tenant_id == tenant_id,
            EmailAnalysis.is_deleted.is_(False),
            EmailAnalysis.created_at < cutoff_date,
        ).all()

        cleaned_count = len(old_records)
        for record in old_records:
            record.is_deleted = True
            record.email_content = "[RETENTION_EXPIRED_PURGED]"
            record.suggested_response = "[RETENTION_EXPIRED_PURGED]"
            record.extracted_entities = {}

        db.session.commit()

        # Auditoria imutável
        AuditService.log(
            action="compliance.retention_cleanup",
            resource_type="tenant",
            resource_id=str(tenant_id),
            details={
                "retention_days": retention_days,
                "cutoff_date": cutoff_date.isoformat(),
                "records_purged": cleaned_count,
            },
            user_id=requester_user_id,
            tenant_id=tenant_id,
        )

        return {
            "status": "success",
            "tenant_id": tenant_id,
            "retention_days": retention_days,
            "cutoff_date": cutoff_date.isoformat(),
            "records_purged": cleaned_count,
        }
