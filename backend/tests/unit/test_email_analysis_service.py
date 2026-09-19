"""
Testes unitários para EmailAnalysisService.
"""
import pytest
from backend.app.services.email_analysis_service import EmailAnalysisService


def test_analyze_email_with_mock_provider(mock_llm_provider):
    """Testa análise de email com provider mockado."""
    service = EmailAnalysisService(llm_provider=mock_llm_provider, use_cache=False)

    result = service.analyze_email(
        "Olá, preciso de ajuda com meu projeto.", store_in_db=False
    )

    assert "error" not in result
    assert "categoria" in result
    assert "resumo" in result
    assert "sugestao_resposta" in result
    assert result["categoria"] in ["Produtivo", "Improdutivo"]


def test_analyze_empty_email(mock_llm_provider):
    """Testa análise de email vazio."""
    service = EmailAnalysisService(llm_provider=mock_llm_provider)

    result = service.analyze_email("", store_in_db=False)

    assert "error" in result
    assert result["error"] == "Email content is empty"


def test_hash_generation(mock_llm_provider):
    """Testa geração de hash consistente."""
    service = EmailAnalysisService(llm_provider=mock_llm_provider)

    hash1 = service._generate_hash("test content")
    hash2 = service._generate_hash("test content")
    hash3 = service._generate_hash("different content")

    assert hash1 == hash2
    assert hash1 != hash3
    assert len(hash1) == 64  # SHA256 hex length
