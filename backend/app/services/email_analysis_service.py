"""
Serviço de inteligência artificial avançada para triagem e análise corporativa de emails.
Incorpora:
- #1 Mascaramento automático de PII pré-LLM
- #3 Extração de Entidades Nomeadas (NER)
- #4 Análise de Sentimento e Urgência
- #6 Detecção de Fraude e Phishing
- #7 Memória de Thread (Contexto histórico de conversas)
- #8 Múltiplos Tons de Resposta
- #14 Quarentena automática de baixa confiança / alto risco
- #16 Categorias dinâmicas por tenant
"""
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from backend.app.models.category import CustomCategory
from backend.app.repositories.email_analysis_repository import EmailAnalysisRepository
from backend.app.services.audit_service import AuditService
from backend.app.services.llm_provider import LLMProvider
from backend.app.utils.dlp_filter import inspect_and_filter_dlp
from backend.app.utils.pii_sanitizer import sanitize_pii

logger = logging.getLogger(__name__)

_EMAIL_CONTENT_MAX_STORE: int = 1500

VALID_TONES = ["formal", "empatico", "negociacao", "juridico", "direto"]


class EmailAnalysisService:
    """Serviço corporativo de análise e inteligência de emails."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        repository: Optional[EmailAnalysisRepository] = None,
        use_cache: bool = True,
        enable_pii_masking: bool = True,
    ):
        self.llm_provider = llm_provider
        self.repository = repository or EmailAnalysisRepository()
        self.use_cache = use_cache
        self.enable_pii_masking = enable_pii_masking

    def analyze_email(
        self,
        email_content: str,
        store_in_db: bool = True,
        tenant_id: Optional[int] = None,
        user_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        tone: str = "formal",
    ) -> Dict[str, Any]:
        """
        Executa a análise semântica estruturada com IA.
        """
        if not email_content or not email_content.strip():
            return {"error": "Email content is empty"}

        if tone not in VALID_TONES:
            tone = "formal"

        # 1. Mascaramento automático de PII (Proteção local pré-LLM)
        pii_metadata = {"masked": False}
        llm_payload = email_content
        if self.enable_pii_masking:
            llm_payload, pii_metadata = sanitize_pii(email_content)
            if pii_metadata.get("masked"):
                logger.info(
                    f"PII masked before LLM: {pii_metadata['total_items_masked']} items redacted."
                )

        # 2. Recuperar histórico da conversa (Thread Context) se fornecido
        thread_history = []
        if thread_id:
            thread_history = self.repository.find_by_thread_id(
                thread_id=thread_id, tenant_id=tenant_id, limit=4
            )

        # 3. Categorias disponíveis para o tenant
        custom_categories = []
        if tenant_id is not None:
            try:
                cats = CustomCategory.query.filter_by(tenant_id=tenant_id, is_active=True).all()
                custom_categories = [c.name for c in cats]
            except Exception:
                pass

        # 4. Verificar cache no banco de dados (se não for parte de thread com histórico)
        content_hash = self._generate_hash(f"{email_content}::{tone}")
        if self.use_cache and not thread_history:
            cached = self.repository.find_by_hash(content_hash, tenant_id=tenant_id)
            if cached:
                logger.info(f"Cache hit for hash {content_hash[:8]}… (Tenant: {tenant_id})")
                return {
                    "id": cached.id,
                    "categoria": cached.category,
                    "subcategoria": cached.sub_category,
                    "resumo": cached.summary,
                    "sugestao_resposta": cached.suggested_response,
                    "sentimento": cached.sentiment or "Neutro",
                    "urgencia": cached.urgency or "Media",
                    "score_confianca": cached.confidence_score or 1.0,
                    "in_quarantine": cached.in_quarantine,
                    "risco_fraude": cached.fraud_risk_score or 0.0,
                    "indicios_fraude": cached.fraud_flags or [],
                    "entidades": cached.extracted_entities or {},
                    "tone": cached.tone_used or "formal",
                    "cached": True,
                    "pii_masked": cached.pii_masked,
                }

        # 5. Construir prompt avançado com todas as diretrizes corporativas
        prompt = self._build_prompt(
            email_content=llm_payload,
            thread_history=thread_history,
            custom_categories=custom_categories,
            tone=tone,
        )

        llm_response = self.llm_provider.generate(prompt)
        if not llm_response.success:
            logger.error(f"LLM error: {llm_response.error_message}")
            return {"error": llm_response.error_message}

        # 6. Parse robusto do JSON
        raw_content = llm_response.content.strip()
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_content = "\n".join(lines).strip()

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e} | Raw: {raw_content[:200]}")
            # Fallback defensivo estruturado
            parsed = {
                "categoria": "Produtivo",
                "subcategoria": "Geral",
                "resumo": raw_content[:200],
                "sentimento": "Neutro",
                "urgencia": "Media",
                "score_confianca": 0.5,
                "risco_fraude": 0.0,
                "indicios_fraude": [],
                "entidades": {},
                "sugestao_resposta": "Recebido. Estamos analisando sua mensagem e retornaremos em breve.",
            }

        # 7. Regras de negócio, cálculo de Quarentena e Filtro DLP de Saída (#38)
        confidence = float(parsed.get("score_confianca", 0.9))
        fraud_risk = float(parsed.get("risco_fraude", 0.0))
        in_quarantine = bool(confidence < 0.70 or fraud_risk >= 0.60)

        raw_suggestion = parsed.get("sugestao_resposta", "")
        clean_suggestion, dlp_meta = inspect_and_filter_dlp(raw_suggestion)
        if dlp_meta.get("dlp_triggered"):
            logger.warning(f"DLP Filter triggered on outbound response: {dlp_meta['violations']}")

        # 8. Persistir no banco de dados com isolamento por Tenant
        created_analysis = None
        if store_in_db:
            try:
                created_analysis = self.repository.create(
                    content_hash=content_hash,
                    email_content=email_content[:_EMAIL_CONTENT_MAX_STORE],
                    category=parsed.get("categoria", "Produtivo"),
                    sub_category=parsed.get("subcategoria"),
                    summary=parsed.get("resumo", ""),
                    suggested_response=clean_suggestion,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    thread_id=thread_id,
                    sentiment=parsed.get("sentimento", "Neutro"),
                    urgency=parsed.get("urgencia", "Media"),
                    confidence_score=confidence,
                    in_quarantine=in_quarantine,
                    fraud_risk_score=fraud_risk,
                    fraud_flags=parsed.get("indicios_fraude", []),
                    extracted_entities=parsed.get("entidades", {}),
                    tone_used=tone,
                    pii_masked=bool(pii_metadata.get("masked", False)),
                    processing_time_ms=llm_response.processing_time_ms,
                    model_used=llm_response.model_used,
                )
            except Exception as e:
                logger.error(f"Failed to persist analysis: {e}")

        # 8.5. Avaliar e aplicar regras de roteamento / SLA automáticas (#11, #17)
        if created_analysis:
            try:
                from backend.app.services.routing_engine_service import RoutingEngineService

                RoutingEngineService.evaluate_and_apply(created_analysis)
            except Exception as e:
                logger.error(f"Failed to evaluate routing rules: {e}")

        # 9. Trilha de auditoria
        AuditService.log(
            action="email.analyze",
            resource_type="EmailAnalysis",
            resource_id=str(created_analysis.id) if created_analysis else None,
            details={
                "category": parsed.get("categoria"),
                "urgency": parsed.get("urgencia"),
                "in_quarantine": in_quarantine,
                "fraud_risk": fraud_risk,
                "tone": tone,
                "pii_masked": bool(pii_metadata.get("masked", False)),
                "thread_id": thread_id,
            },
            user_id=user_id,
            tenant_id=tenant_id,
        )

        return {
            "id": created_analysis.id if created_analysis else None,
            "categoria": parsed.get("categoria", "Produtivo"),
            "subcategoria": parsed.get("subcategoria", "Geral"),
            "resumo": parsed.get("resumo", ""),
            "sugestao_resposta": parsed.get("sugestao_resposta", ""),
            "sentimento": parsed.get("sentimento", "Neutro"),
            "urgencia": parsed.get("urgencia", "Media"),
            "score_confianca": confidence,
            "in_quarantine": in_quarantine,
            "risco_fraude": fraud_risk,
            "indicios_fraude": parsed.get("indicios_fraude", []),
            "entidades": parsed.get("entidades", {}),
            "tone": tone,
            "cached": False,
            "pii_masked": bool(pii_metadata.get("masked", False)),
        }

    def regenerate_response(
        self, analysis_id: int, new_tone: str, tenant_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Regenera a sugestão de resposta para um email já analisado com um novo tom comunicativo (#8).
        """
        if new_tone not in VALID_TONES:
            new_tone = "formal"

        analysis = self.repository.find_by_id(analysis_id, tenant_id=tenant_id)
        if not analysis:
            return {"error": "Analysis not found"}

        prompt = f"""
Você é um assistente executivo de triagem de emails.
Com base no resumo e conteúdo abaixo, gere uma nova sugestão de resposta estritamente no TOM '{new_tone.upper()}'.

Diretrizes de Tom:
- formal: Profissional, corporativo e polido.
- empatico: Caloroso, acolhedor e atencioso com o cliente.
- negociacao: Firme, focado em acordos e proposição de valor.
- juridico: Cauteloso, institucional e em conformidade regulatória.
- direto: Sucinto, objetivo e sem rodeios.

Resumo do email: {analysis.summary}
Conteúdo: {analysis.email_content or ''}

Retorne exclusivamente um objeto JSON no formato:
{{"sugestao_resposta": "texto da resposta no tom solicitado"}}
"""
        llm_response = self.llm_provider.generate(prompt)
        if not llm_response.success:
            return {"error": llm_response.error_message}

        raw_content = llm_response.content.strip()
        if raw_content.startswith("```"):
            lines = raw_content.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            raw_content = "\n".join(lines).strip()

        try:
            parsed = json.loads(raw_content)
            new_text = parsed.get("sugestao_resposta", raw_content)
        except Exception:
            new_text = raw_content

        analysis.suggested_response = new_text
        analysis.tone_used = new_tone
        from backend.app import db

        db.session.commit()

        AuditService.log(
            action="email.regenerate_tone",
            resource_type="EmailAnalysis",
            resource_id=str(analysis.id),
            details={"new_tone": new_tone},
            tenant_id=tenant_id,
        )

        return {
            "analysis_id": analysis.id,
            "tone": new_tone,
            "sugestao_resposta": new_text,
        }

    # ── Métodos auxiliares ────────────────────────────────────────────────────

    def _generate_hash(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _build_prompt(
        self,
        email_content: str,
        thread_history: List[Any],
        custom_categories: List[str],
        tone: str,
    ) -> str:
        cats_str = ", ".join(custom_categories) if custom_categories else "Produtivo, Improdutivo"

        history_context = ""
        if thread_history:
            history_context = "\nHistórico anterior desta mesma conversa (para contexto):\n"
            for prev in thread_history:
                history_context += f"- [{prev.category}] Resumo: {prev.summary}\n"

        return f"""
Você é o motor de inteligência artificial de triagem corporativa para o setor financeiro e B2B.
Analise com rigor o email a seguir e extraia todas as entidades e métricas semânticas estruturadas.

{history_context}
Email atual para análise:
---
{email_content}
---

Instruções de Saída:
Gere estritamente um único objeto JSON válido (sem texto livre fora do JSON) com a seguinte estrutura:
{{
  "categoria": "Classifique entre as opções permitidas: {cats_str}. Use 'Produtivo' se exigir ação e 'Improdutivo' se for aviso/spam/agradecimento.",
  "subcategoria": "Ex: Dúvida Faturamento, Solicitação de Cancelamento, Disputa de PIX, Cobrança, Elogio, Spam, etc.",
  "resumo": "Resumo executivo claro em exatamente 1 frase.",
  "sentimento": "Positivo | Neutro | Negativo | Irritado",
  "urgencia": "Baixa | Media | Alta | Critica",
  "score_confianca": 0.95 (float entre 0.0 e 1.0 indicando sua certeza na classificação),
  "risco_fraude": 0.05 (float entre 0.0 e 1.0 indicando suspeita de engenharia social, phishing, spoofing ou golpe financeiro),
  "indicios_fraude": ["lista de indícios identificados ou vazio se legítimo"],
  "entidades": {{
    "valores_monetarios": ["R$ 1.500,00"],
    "datas_vencimento": ["10/10/2026"],
    "documentos": ["CPFs ou CNPJs citados"],
    "protocolos": ["números de chamado ou boletos"],
    "solicitante": "Nome ou cargo identificado"
  }},
  "sugestao_resposta": "Rascunho de resposta profissional elaborado no tom '{tone.upper()}'. Se a categoria for improdutiva, coloque 'Nenhuma ação necessária.'"
}}
"""
