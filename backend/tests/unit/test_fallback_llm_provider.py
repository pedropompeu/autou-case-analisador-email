"""
Testes unitários para o FallbackLLMProvider.
"""
from backend.app.services.fallback_llm_provider import FallbackLLMProvider
from backend.app.services.llm_provider import LLMProvider, LLMResponse


class FailingLLMProvider(LLMProvider):
    def __init__(self, name="failing-llm"):
        self.model_name = name

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        return LLMResponse(
            content="",
            model_used=self.model_name,
            processing_time_ms=10,
            success=False,
            error_message="503 Service Unavailable",
        )

    def is_available(self) -> bool:
        return False


class WorkingLLMProvider(LLMProvider):
    def __init__(self, name="working-llm", content='{"categoria": "Produtivo"}'):
        self.model_name = name
        self.content = content

    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        return LLMResponse(
            content=self.content,
            model_used=self.model_name,
            processing_time_ms=25,
            success=True,
        )

    def is_available(self) -> bool:
        return True


def test_fallback_switches_to_secondary_on_primary_failure():
    primary = FailingLLMProvider("gemini-failing")
    secondary = WorkingLLMProvider("claude-backup", content='{"status": "ok"}')

    provider = FallbackLLMProvider([primary, secondary])
    response = provider.generate("teste prompt")

    assert response.success is True
    assert response.model_used == "claude-backup"
    assert response.content == '{"status": "ok"}'


def test_fallback_fails_if_all_providers_fail():
    p1 = FailingLLMProvider("p1")
    p2 = FailingLLMProvider("p2")

    provider = FallbackLLMProvider([p1, p2])
    response = provider.generate("teste prompt")

    assert response.success is False
    assert "All AI providers failed" in response.error_message
