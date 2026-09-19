"""
Factory centralizada para criação do LLM Provider.

Elimina duplicação entre email_routes.py e legacy/routes.py e
serve como único ponto de decisão sobre qual provider usar.
"""
import logging
from flask import current_app

from backend.app.services.llm_provider import LLMProvider
from backend.app.services.gemini_provider import GeminiProvider, MockLLMProvider

logger = logging.getLogger(__name__)


def create_llm_provider() -> LLMProvider:
    """
    Cria e retorna o LLM Provider adequado para o ambiente atual.

    - Em testes (TESTING=True) ou quando USE_MOCK_LLM=True: retorna MockLLMProvider
    - Em desenvolvimento/produção: retorna GeminiProvider

    Returns:
        Instância de LLMProvider configurada.
    """
    if current_app.config.get("TESTING") or current_app.config.get("USE_MOCK_LLM"):
        logger.info("Using MockLLMProvider (TESTING or USE_MOCK_LLM is set)")
        return MockLLMProvider()

    api_key = current_app.config["GEMINI_API_KEY"]
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-1.5-flash-latest")

    logger.debug(f"Creating GeminiProvider with model={model_name}")
    return GeminiProvider(api_key=api_key, model_name=model_name)
