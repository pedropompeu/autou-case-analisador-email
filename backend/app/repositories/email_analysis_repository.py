"""
Repository Pattern para EmailAnalysis.
Isola a lógica de acesso a dados do resto da aplicação com suporte a multi-tenancy e criptografia at-rest.
"""
from typing import Optional, List
from backend.app import db
from backend.app.models.email_analysis import EmailAnalysis
from backend.app.utils.crypto import encrypt_text, decrypt_text


class EmailAnalysisRepository:
    """Repository para operações de banco de dados com EmailAnalysis."""

    @staticmethod
    def create(
        content_hash: str,
        email_content: str,
        category: str,
        summary: str,
        suggested_response: str,
        tenant_id: Optional[int] = None,
        user_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        sub_category: Optional[str] = None,
        sentiment: Optional[str] = None,
        urgency: Optional[str] = None,
        confidence_score: Optional[float] = None,
        in_quarantine: bool = False,
        fraud_risk_score: Optional[float] = None,
        fraud_flags: Optional[dict] = None,
        extracted_entities: Optional[dict] = None,
        tone_used: Optional[str] = "formal",
        pii_masked: bool = False,
        processing_time_ms: Optional[int] = None,
        model_used: Optional[str] = None,
    ) -> EmailAnalysis:
        """Cria um novo registro de análise com criptografia at-rest e inteligência da Fase 1."""
        encrypted_content = encrypt_text(email_content)

        analysis = EmailAnalysis(
            tenant_id=tenant_id,
            user_id=user_id,
            thread_id=thread_id,
            content_hash=content_hash,
            email_content=encrypted_content,
            category=category,
            sub_category=sub_category,
            summary=summary,
            suggested_response=suggested_response,
            sentiment=sentiment,
            urgency=urgency,
            confidence_score=confidence_score,
            in_quarantine=in_quarantine,
            fraud_risk_score=fraud_risk_score,
            fraud_flags=fraud_flags,
            extracted_entities=extracted_entities,
            tone_used=tone_used,
            pii_masked=pii_masked,
            processing_time_ms=processing_time_ms,
            model_used=model_used,
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis

    @staticmethod
    def find_by_thread_id(
        thread_id: str, tenant_id: Optional[int] = None, limit: int = 5
    ) -> List[EmailAnalysis]:
        """Busca histórico de análises de uma mesma thread para contexto conversacional."""
        query = EmailAnalysis.query.filter_by(thread_id=thread_id, is_deleted=False)
        if tenant_id is not None:
            query = query.filter_by(tenant_id=tenant_id)

        items = query.order_by(EmailAnalysis.created_at.asc()).limit(limit).all()
        for item in items:
            if item.email_content:
                item.email_content = decrypt_text(item.email_content)
        return items

    @staticmethod
    def find_by_hash(content_hash: str, tenant_id: Optional[int] = None) -> Optional[EmailAnalysis]:
        """Busca análise pelo hash do conteúdo (isolado por tenant se fornecido)."""
        query = EmailAnalysis.query.filter_by(content_hash=content_hash, is_deleted=False)
        if tenant_id is not None:
            query = query.filter_by(tenant_id=tenant_id)
        
        analysis = query.first()
        if analysis and analysis.email_content:
            analysis.email_content = decrypt_text(analysis.email_content)
        return analysis

    @staticmethod
    def find_by_id(analysis_id: int, tenant_id: Optional[int] = None) -> Optional[EmailAnalysis]:
        """Busca análise por ID."""
        query = EmailAnalysis.query.filter_by(id=analysis_id, is_deleted=False)
        if tenant_id is not None:
            query = query.filter_by(tenant_id=tenant_id)

        analysis = query.first()
        if analysis and analysis.email_content:
            analysis.email_content = decrypt_text(analysis.email_content)
        return analysis

    @staticmethod
    def get_recent(limit: int = 10, tenant_id: Optional[int] = None) -> List[EmailAnalysis]:
        """Retorna as análises mais recentes do tenant."""
        query = EmailAnalysis.query.filter_by(is_deleted=False)
        if tenant_id is not None:
            query = query.filter_by(tenant_id=tenant_id)

        analyses = (
            query.order_by(EmailAnalysis.created_at.desc())
            .limit(limit)
            .all()
        )
        for item in analyses:
            if item.email_content:
                item.email_content = decrypt_text(item.email_content)
        return analyses

    @staticmethod
    def delete(analysis_id: int, tenant_id: Optional[int] = None) -> bool:
        """Soft delete de uma análise."""
        analysis = EmailAnalysisRepository.find_by_id(analysis_id, tenant_id=tenant_id)
        if analysis:
            analysis.soft_delete()
            return True
        return False

