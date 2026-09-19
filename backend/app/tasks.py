import logging
from celery import shared_task
from flask import current_app

from backend.app.services.email_analysis_service import EmailAnalysisService
from backend.app.services.llm_provider_factory import create_llm_provider
from backend.app.repositories.email_analysis_repository import EmailAnalysisRepository

logger = logging.getLogger(__name__)

@shared_task(bind=True, name="analyze_email_background")
def analyze_email_background(self, email_text: str, store_in_db: bool = True):
    """
    Task assíncrona para analisar e-mail usando IA em background.
    """
    logger.info(f"Starting background analysis for task {self.request.id}")
    
    # Em tasks Celery com shared_task + factory, temos acesso ao current_app
    # O service será instanciado aqui com as dependências corretas
    service = EmailAnalysisService(
        llm_provider=create_llm_provider(),
        repository=EmailAnalysisRepository(),
    )
    
    try:
        # Executa a análise (pode levar vários segundos)
        result = service.analyze_email(email_text, store_in_db=store_in_db)
        
        if "error" in result:
            logger.error(f"Analysis failed for task {self.request.id}: {result['error']}")
            # Podemos usar retries aqui se for erro de rate limit (429)
            if "rate limit" in str(result["error"]).lower():
                 raise self.retry(exc=Exception(result["error"]), countdown=60)
            return result

        logger.info(f"Analysis completed successfully for task {self.request.id}")
        return result
        
    except Exception as exc:
        logger.exception(f"Unexpected error in task {self.request.id}")
        # Retentativas automáticas para erros inesperados (até 3 vezes)
        raise self.retry(exc=exc, countdown=30, max_retries=3)
