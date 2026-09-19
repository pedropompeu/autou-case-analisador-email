"""
Factory centralizada para criação do LLM Provider.

Elimina duplicação entre email_routes.py e legacy/routes.py e
serve como único ponto de decisão sobre qual provider usar.
"""
import logging
from typing import List

from flask import current_app

from backend.app.services.fallback_llm_provider import FallbackLLMProvider
from backend.app.services.gemini_provider import GeminiProvider, MockLLMProvider
from backend.app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


def create_llm_provider() -> LLMProvider:
    """
    Cria e retorna o LLM Provider adequado para o ambiente atual com suporte a fallback.
    """
    if current_app.config.get("TESTING") or current_app.config.get("USE_MOCK_LLM"):
        logger.info("Using MockLLMProvider (TESTING or USE_MOCK_LLM is set)")
        return MockLLMProvider()

    api_key = current_app.config.get("GEMINI_API_KEY", "")
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-3.6-flash")

    providers: List[LLMProvider] = []
    if api_key:
        providers.append(GeminiProvider(api_key=api_key, model_name=model_name))

    # No ambiente de desenvolvimento ou se habilitado fallback, incluir MockLLMProvider no final da cadeia
    is_dev = current_app.config.get("ENV") == "development" or current_app.config.get("DEBUG", False)
    if current_app.config.get("ENABLE_MOCK_FALLBACK", is_dev) or not providers:
        providers.append(MockLLMProvider())

    if len(providers) == 1:
        return providers[0]

    return FallbackLLMProvider(providers)
