"""
Testes unitários para o ComplianceService (LGPD Export, Erasure e Retention).
"""
import pytest
from datetime import datetime, timedelta, timezone

from backend.app import db
from backend.app.models.tenant import Tenant
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.services.compliance_service import ComplianceService


def test_compliance_export_subject_data(app, db_session):
    with app.app_context():
        tenant = Tenant(name="LGPD Tenant", slug="lgpd-export-tenant")
        db.session.add(tenant)
        db.session.commit()

        analysis1 = EmailAnalysis(
            email_content="Olá, meu email é titular@exemplo.com e gostaria de extrato.",
            summary="Pedido de extrato",
            content_hash="hash_export_1",
            category="Produtivo",
            suggested_response="Resposta enviada para titular@exemplo.com com sucesso.",
            tenant_id=tenant.id
        )
        analysis2 = EmailAnalysis(
            email_content="Outro email qualquer sem menção ao titular.",
            summary="Outro email",
            content_hash="hash_export_2",
            category="Improdutivo",
            suggested_response="Obrigado pelo contato.",
            tenant_id=tenant.id
        )
        db.session.add_all([analysis1, analysis2])
        db.session.commit()

        export_data = ComplianceService.export_subject_data(
            tenant_id=tenant.id,
            subject_identifier="titular@exemplo.com"
        )

        assert export_data["subject_identifier"] == "titular@exemplo.com"
        assert export_data["total_records_found"] == 1
        assert len(export_data["records"]) == 1
        assert export_data["records"][0]["id"] == analysis1.id


def test_compliance_erase_subject_data(app, db_session):
    with app.app_context():
        tenant = Tenant(name="LGPD Erasure Tenant", slug="lgpd-erasure-tenant")
        db.session.add(tenant)
        db.session.commit()

        analysis = EmailAnalysis(
            email_content="Favor cancelar conta do cliente joao.silva@empresa.com imediatamente.",
            summary="Cancelamento de conta",
            content_hash="hash_erase_1",
            category="Produtivo",
            suggested_response="Prezado joao.silva@empresa.com, seu pedido foi processado.",
            extracted_entities={"client_email": "joao.silva@empresa.com", "protocol": "12345"},
            tenant_id=tenant.id
        )
        db.session.add(analysis)
        db.session.commit()

        result = ComplianceService.erase_subject_data(
            tenant_id=tenant.id,
            subject_identifier="joao.silva@empresa.com"
        )

        assert result["records_anonymized"] == 1

        db.session.refresh(analysis)
        assert "joao.silva@empresa.com" not in analysis.email_content
        assert "[LGPD_ANONYMIZED]" in analysis.email_content
        assert "[LGPD_ANONYMIZED]" in analysis.suggested_response
        assert analysis.extracted_entities["client_email"] == "[LGPD_ANONYMIZED]"


def test_compliance_retention_cleanup(app, db_session):
    with app.app_context():
        tenant = Tenant(
            name="Retention Tenant",
            slug="retention-tenant",
            settings={"retention_days": 30}
        )
        db.session.add(tenant)
        db.session.commit()

        old_date = datetime.now(timezone.utc) - timedelta(days=45)
        recent_date = datetime.now(timezone.utc) - timedelta(days=10)

        old_analysis = EmailAnalysis(
            email_content="Mensagem antiga que deve expirar.",
            summary="Email antigo",
            content_hash="hash_old_1",
            suggested_response="Resposta antiga",
            category="Produtivo",
            tenant_id=tenant.id,
            created_at=old_date
        )
        recent_analysis = EmailAnalysis(
            email_content="Mensagem recente que deve ser preservada.",
            summary="Email recente",
            content_hash="hash_recent_1",
            suggested_response="Resposta recente",
            category="Produtivo",
            tenant_id=tenant.id,
            created_at=recent_date
        )
        db.session.add_all([old_analysis, recent_analysis])
        db.session.commit()

        result = ComplianceService.run_retention_cleanup(tenant_id=tenant.id)
        assert result["records_purged"] == 1

        db.session.refresh(old_analysis)
        db.session.refresh(recent_analysis)

        assert old_analysis.is_deleted is True
        assert old_analysis.email_content == "[RETENTION_EXPIRED_PURGED]"
        assert recent_analysis.is_deleted is False
        assert recent_analysis.email_content == "Mensagem recente que deve ser preservada."
