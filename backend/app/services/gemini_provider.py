"""
Implementação concreta do LLM Provider para Google Gemini.
Usa o SDK oficial `google-genai` (substituto do deprecated `google-generativeai`).
Inclui retries exponenciais com jitter e circuit breaker básico.
"""
import json
import logging
import random
import time

from google import genai
from google.genai import types

from backend.app.services.llm_provider import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Provedor de IA usando Google Gemini (SDK google-genai)."""

    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-3.6-flash",
        max_retries: int = 3,
        initial_delay: float = 1.0,
    ):
        """
        Inicializa o provedor Gemini com o novo SDK google-genai.

        Args:
            api_key: Chave da API do Google.
            model_name: Nome do modelo a usar (ex: gemini-2.0-flash).
            max_retries: Número máximo de tentativas em caso de rate limit.
            initial_delay: Delay inicial (segundos) para retry exponencial.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.max_retries = max_retries
        self.initial_delay = initial_delay

        # Novo SDK: cliente é instanciado com chave — não mais uma configuração global
        self._client = genai.Client(api_key=api_key)

        self._generation_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.3,
            max_output_tokens=2048,
            top_p=0.8,
            top_k=40,
        )

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Gera conteúdo usando Gemini com retry exponencial e jitter.

        O jitter randomizado (±25%) previne o "thundering herd problem":
        quando múltiplos workers atingem o rate limit simultaneamente,
        o jitter distribui as tentativas no tempo evitando uma nova rajada.

        Args:
            prompt: Texto do prompt.
            **kwargs: Parâmetros adicionais de geração (sobrescrevem os padrões).

        Returns:
            LLMResponse com resultado ou erro.
        """
        start_time = time.time()

        # Merge de configuração se kwargs fornecidos
        if kwargs:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=kwargs.get("temperature", 0.5),
                max_output_tokens=kwargs.get("max_output_tokens", 500),
                top_p=kwargs.get("top_p", 0.8),
                top_k=kwargs.get("top_k", 40),
            )
        else:
            config = self._generation_config

        delay = self.initial_delay

        for attempt in range(self.max_retries):
            try:
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                processing_time = int((time.time() - start_time) * 1000)

                logger.info(
                    f"Gemini request ok (attempt {attempt + 1}/{self.max_retries}, "
                    f"{processing_time}ms)"
                )

                return LLMResponse(
                    content=response.text or "",
                    model_used=self.model_name,
                    processing_time_ms=processing_time,
                    success=True,
                )

            except Exception as e:
                err_str = str(e).lower()
                is_retryable = (
                    "429" in err_str
                    or "resource_exhausted" in err_str
                    or "rate limit" in err_str
                    or "quota" in err_str
                    or "503" in err_str
                    or "unavailable" in err_str
                    or "high demand" in err_str
                )

                if is_retryable and attempt < self.max_retries - 1:
                    # Jitter: ±25% do delay calculado — evita thundering herd
                    jitter = delay * random.uniform(-0.25, 0.25)
                    sleep_for = delay + jitter
                    logger.warning(
                        f"Transient Gemini error (rate limit / 503) — retrying in {sleep_for:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries}): {e}"
                    )
                    time.sleep(sleep_for)
                    delay *= 2.5  # Exponential backoff
                else:
                    if is_retryable:
                        logger.error(f"Max retries reached after transient API errors: {e}")
                        error_msg = "API is currently experiencing high demand. Please try again in a few moments."
                    else:
                        logger.exception(f"Unexpected error calling Gemini API: {e}")
                        error_msg = f"Error communicating with AI service: {str(e)}"

                    processing_time = int((time.time() - start_time) * 1000)
                    return LLMResponse(
                        content="",
                        model_used=self.model_name,
                        processing_time_ms=processing_time,
                        success=False,
                        error_message=error_msg,
                    )

        # Fallback defensivo (não deve ser atingido normalmente)
        processing_time = int((time.time() - start_time) * 1000)
        return LLMResponse(
            content="",
            model_used=self.model_name,
            processing_time_ms=processing_time,
            success=False,
            error_message="Unexpected error in retry logic.",
        )

    def is_available(self) -> bool:
        """Verifica se o Gemini está disponível com uma chamada mínima."""
        try:
            self._client.models.generate_content(
                model=self.model_name,
                contents="ping",
            )
            return True
        except Exception as e:
            logger.error(f"Gemini availability check failed: {e}")
            return False


class MockLLMProvider(LLMProvider):
    """Provedor mock para testes e desenvolvimento local (Sandbox Mode)."""

    def __init__(self):
        self.model_name = "mock-llm"

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        """Retorna resposta determinística para testes."""
        mock_response = {
            "categoria": "Produtivo",
            "resumo": "Email de teste mockado para desenvolvimento local.",
            "sugestao_resposta": (
                "Obrigado pelo seu email. Estamos analisando e retornaremos em breve."
            ),
        }

        return LLMResponse(
            content=json.dumps(mock_response, ensure_ascii=False),
            model_used=self.model_name,
            processing_time_ms=50,
            success=True,
        )

    def is_available(self) -> bool:
        """Mock sempre disponível."""
        return True
