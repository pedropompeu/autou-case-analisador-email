"""
Testes unitários para o RoutingEngineService (#11, #17).
"""
import pytest
from backend.app import db
from backend.app.models.tenant import Tenant
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.routing_rule import RoutingRule
from backend.app.services.routing_engine_service import RoutingEngineService


def test_routing_engine_triggers_quarantine_on_fraud_risk(app, db_session):
    with app.app_context():
        tenant = Tenant(name="Rule Tenant 1", slug="rule-tenant-1")
        db.session.add(tenant)
        db.session.commit()

        rule = RoutingRule(
            tenant_id=tenant.id,
            name="Risco Alto de Fraude",
            condition_field="fraud_risk_score",
            condition_operator="gte",
            condition_value="0.5",
            action_type="set_quarantine",
            priority=10
        )
        db.session.add(rule)
        db.session.commit()

        analysis = EmailAnalysis(
            email_content="Clique neste link e informe sua senha imediatamente.",
            summary="Tentativa suspeita",
            content_hash="hash_rule_1",
            category="Improdutivo",
            suggested_response="Nenhuma ação",
            fraud_risk_score=0.85,
            in_quarantine=False,
            tenant_id=tenant.id
        )
        db.session.add(analysis)
        db.session.commit()

        triggered = RoutingEngineService.evaluate_and_apply(analysis)

        assert len(triggered) == 1
        assert triggered[0]["rule_name"] == "Risco Alto de Fraude"
        assert analysis.in_quarantine is True


def test_routing_engine_triggers_urgency_escalation(app, db_session):
    with app.app_context():
        tenant = Tenant(name="Rule Tenant 2", slug="rule-tenant-2")
        db.session.add(tenant)
        db.session.commit()

        rule = RoutingRule(
            tenant_id=tenant.id,
            name="Cliente Irritado -> Urgência Crítica",
            condition_field="sentiment",
            condition_operator="equals",
            condition_value="Irritado",
            action_type="set_urgency",
            action_payload={"urgency": "Critica"},
            priority=5
        )
        db.session.add(rule)
        db.session.commit()

        analysis = EmailAnalysis(
            email_content="Estou extremamente revoltado com o atraso no estorno!",
            summary="Reclamação de estorno",
            content_hash="hash_rule_2",
            category="Produtivo",
            suggested_response="Pedimos desculpas",
            sentiment="Irritado",
            urgency="Media",
            tenant_id=tenant.id
        )
        db.session.add(analysis)
        db.session.commit()

        triggered = RoutingEngineService.evaluate_and_apply(analysis)

        assert len(triggered) == 1
        assert analysis.urgency == "Critica"
