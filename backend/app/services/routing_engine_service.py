"""
Motor de Regras de Roteamento e SLA Automático (#11, #17).
Avalia regras ativas após a análise de IA para disparar ações automáticas.
"""
import logging
from typing import Any, Dict, List

from backend.app import db
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.models.routing_rule import RoutingRule
from backend.app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)


class RoutingEngineService:
    """Aplica regras de roteamento e ações baseadas em atributos da análise."""

    @classmethod
    def evaluate_and_apply(cls, analysis: EmailAnalysis) -> List[Dict[str, Any]]:
        """
        Avalia todas as regras ativas do tenant ordenadas por prioridade.
        Executa as ações correspondentes e retorna o log de regras disparadas.
        """
        if not analysis.tenant_id:
            return []

        rules = (
            RoutingRule.query.filter_by(
                tenant_id=analysis.tenant_id, is_active=True, is_deleted=False
            )
            .order_by(RoutingRule.priority.asc())
            .all()
        )

        triggered_rules = []
        for rule in rules:
            if cls._matches_condition(analysis, rule):
                cls._execute_action(analysis, rule)
                triggered_rules.append(
                    {
                        "rule_id": rule.id,
                        "rule_name": rule.name,
                        "action_type": rule.action_type,
                        "payload": rule.action_payload,
                    }
                )

        if triggered_rules:
            db.session.commit()

        return triggered_rules

    @classmethod
    def _matches_condition(cls, analysis: EmailAnalysis, rule: RoutingRule) -> bool:
        """Verifica se a análise satisfaz a condição da regra."""
        field = rule.condition_field
        op = rule.condition_operator.lower()
        target_val = str(rule.condition_value).strip().lower()

        # Extração do valor real do campo da análise
        actual_val = None
        if field == "sentiment":
            actual_val = analysis.sentiment
        elif field == "urgency":
            actual_val = analysis.urgency
        elif field == "category":
            actual_val = analysis.category
        elif field == "fraud_risk_score":
            actual_val = analysis.fraud_risk_score
        elif field == "confidence_score":
            actual_val = analysis.confidence_score
        elif field == "status":
            actual_val = analysis.status

        if actual_val is None:
            return False

        # Operações numéricas
        if field in ("fraud_risk_score", "confidence_score"):
            try:
                num_actual = float(actual_val)
                num_target = float(target_val)
                if op == "gte" or op == ">=":
                    return num_actual >= num_target
                elif op == "lte" or op == "<=":
                    return num_actual <= num_target
                elif op == "equals" or op == "==":
                    return num_actual == num_target
            except (ValueError, TypeError):
                return False

        # Operações de texto
        str_actual = str(actual_val).strip().lower()
        if op == "equals" or op == "==":
            return str_actual == target_val
        elif op == "contains":
            return target_val in str_actual
        elif op == "in":
            items = [item.strip().lower() for item in target_val.split(",")]
            return str_actual in items

        return False

    @classmethod
    def _execute_action(cls, analysis: EmailAnalysis, rule: RoutingRule) -> None:
        """Executa a ação configurada na regra."""
        action = rule.action_type.lower()
        payload = rule.action_payload or {}

        logger.info(f"Executing rule action '{action}' (rule {rule.id}) on analysis {analysis.id}")

        if action == "set_quarantine":
            analysis.in_quarantine = True

        elif action == "set_urgency":
            new_urgency = payload.get("urgency", "Alta")
            analysis.urgency = new_urgency

        elif action == "set_status":
            new_status = payload.get("status", "in_progress")
            analysis.status = new_status

        elif action == "assign_user":
            user_id = payload.get("user_id")
            if user_id:
                analysis.assigned_to_user_id = int(user_id)

        elif action == "alert_webhook":
            event_name = payload.get("event", "analysis.sla_alert")
            WebhookService.dispatch_event(
                tenant_id=analysis.tenant_id,
                event=event_name,
                payload={
                    "analysis_id": analysis.id,
                    "rule_id": rule.id,
                    "rule_name": rule.name,
                    "urgency": analysis.urgency,
                    "sentiment": analysis.sentiment,
                    "category": analysis.category,
                },
            )
