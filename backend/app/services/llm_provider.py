"""
Interface abstrata para provedores de LLM (agnóstico).
Permite trocar facilmente entre Gemini, OpenAI, Claude, etc.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Resposta padronizada de um LLM."""

    content: str
    model_used: str
    processing_time_ms: int
    success: bool
    error_message: Optional[str] = None


class LLMProvider(ABC):
    """Interface abstrata para provedores de LLM."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Gera conteúdo baseado no prompt.

        Args:
            prompt: Texto do prompt
            **kwargs: Parâmetros específicos do provedor

        Returns:
            LLMResponse com o resultado
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível."""
        pass
