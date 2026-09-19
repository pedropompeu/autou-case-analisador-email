"""
Provedor de IA com Suporte a Fallback Multi-LLM e Circuit Breaker.
Garante alta disponibilidade alternando automaticamente entre provedores (ex: Gemini -> Mock/Secondary)
em caso de sobrecarga, rate limits rígidos ou quedas transitórias de rede.
"""
import logging
from typing import List

from backend.app.services.llm_provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class FallbackLLMProvider(LLMProvider):
    """Encapsula múltiplos provedores de LLM com política de failover sequencial."""

    def __init__(self, providers: List[LLMProvider]):
        """
        Args:
            providers: Lista ordenada de provedores por prioridade (primário, secundário, etc.).
        """
        if not providers:
            raise ValueError("FallbackLLMProvider requires at least one LLMProvider.")
        self.providers = providers
        self.model_name = f"fallback({','.join(p.model_name for p in providers)})"

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Executa a geração de conteúdo tentando os provedores em ordem de prioridade.
        """
        last_error = None

        for idx, provider in enumerate(self.providers):
            try:
                logger.info(
                    f"Attempting generation with provider #{idx + 1}: {provider.model_name}"
                )
                response = provider.generate(prompt, **kwargs)
                if response.success:
                    if idx > 0:
                        logger.warning(
                            f"Failover successful! Primary provider failed, fulfilled by #{idx + 1} ({provider.model_name})."
                        )
                    return response

                last_error = response.error_message
                logger.warning(
                    f"Provider {provider.model_name} failed: {response.error_message}. Trying next..."
                )

            except Exception as e:
                last_error = str(e)
                logger.exception(f"Unexpected exception with provider {provider.model_name}: {e}")

        logger.error("All configured LLM providers failed in fallback chain.")
        return LLMResponse(
            content="",
            model_used=self.model_name,
            processing_time_ms=0,
            success=False,
            error_message=f"All AI providers failed. Last error: {last_error}",
        )

    def is_available(self) -> bool:
        """Retorna True se pelo menos um provedor estiver operacional."""
        return any(p.is_available() for p in self.providers)
