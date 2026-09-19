"""
Repository Pattern para EmailAnalysis.
Isola a lógica de acesso a dados do resto da aplicação.
"""
from typing import Optional, List
from backend.app import db
from backend.app.models.email_analysis import EmailAnalysis


class EmailAnalysisRepository:
    """Repository para operações de banco de dados com EmailAnalysis."""

    @staticmethod
    def create(
        content_hash: str,
        email_content: str,
        category: str,
        summary: str,
        suggested_response: str,
        processing_time_ms: int = None,
        model_used: str = None,
    ) -> EmailAnalysis:
        """Cria um novo registro de análise."""
        analysis = EmailAnalysis(
            content_hash=content_hash,
            email_content=email_content,
            category=category,
            summary=summary,
            suggested_response=suggested_response,
            processing_time_ms=processing_time_ms,
            model_used=model_used,
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis

    @staticmethod
    def find_by_hash(content_hash: str) -> Optional[EmailAnalysis]:
        """Busca análise pelo hash do conteúdo (para cache)."""
        return EmailAnalysis.query.filter_by(
            content_hash=content_hash, is_deleted=False
        ).first()

    @staticmethod
    def find_by_id(analysis_id: int) -> Optional[EmailAnalysis]:
        """Busca análise por ID."""
        return EmailAnalysis.query.filter_by(
            id=analysis_id, is_deleted=False
        ).first()

    @staticmethod
    def get_recent(limit: int = 10) -> List[EmailAnalysis]:
        """Retorna as análises mais recentes."""
        return (
            EmailAnalysis.query.filter_by(is_deleted=False)
            .order_by(EmailAnalysis.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def delete(analysis_id: int) -> bool:
        """Soft delete de uma análise."""
        analysis = EmailAnalysisRepository.find_by_id(analysis_id)
        if analysis:
            analysis.soft_delete()
            return True
        return False
