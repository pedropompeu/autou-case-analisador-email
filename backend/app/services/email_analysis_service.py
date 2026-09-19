"""
Serviço de negócio para análise de emails.
Orquestra LLM Provider, Cache e Repository.
"""
import hashlib
import json
import logging
from typing import Dict, Optional

from backend.app.services.llm_provider import LLMProvider
from backend.app.repositories.email_analysis_repository import EmailAnalysisRepository
from backend.app.utils.cache import cache_get, cache_set

logger = logging.getLogger(__name__)

# Número máximo de caracteres do e-mail original a persistir no banco.
# Armazenar o email completo pode ser desnecessário e oneroso; este limite
# garante espaço suficiente para auditoria sem desperdiçar storage.
_EMAIL_CONTENT_MAX_STORE: int = 1000


class EmailAnalysisService:
    """Serviço para análise de emails com IA."""

    def __init__(
        self,
        llm_provider: LLMProvider,
        repository: Optional[EmailAnalysisRepository] = None,
        use_cache: bool = True,
    ):
        """
        Inicializa o serviço.

        Args:
            llm_provider: Provedor de LLM a usar (injetado — facilita testes).
            repository: Repositório de análises (injetado — facilita testes).
                        Se None, cria uma instância padrão.
            use_cache: Se deve usar cache por hash de conteúdo.
        """
        self.llm_provider = llm_provider
        self.repository = repository or EmailAnalysisRepository()
        self.use_cache = use_cache

    def analyze_email(
        self, email_content: str, store_in_db: bool = True
    ) -> Dict[str, object]:
        """
        Analisa um email usando IA.

        Fluxo:
            1. Valida o conteúdo.
            2. Verifica cache no banco de dados (hash SHA-256).
            3. Chama o LLM Provider.
            4. Valida e persiste o resultado.

        Args:
            email_content: Conteúdo completo do email.
            store_in_db: Se deve armazenar a análise no banco de dados.

        Returns:
            Dicionário com resultado da análise ou chave ``error``.
        """
        if not email_content or not email_content.strip():
            return {"error": "Email content is empty"}

        # Gerar hash do conteúdo para cache
        content_hash = self._generate_hash(email_content)

        # Verificar cache no banco de dados
        if self.use_cache:
            cached = self.repository.find_by_hash(content_hash)
            if cached:
                logger.info(f"Cache hit for hash {content_hash[:8]}…")
                return {
                    "categoria": cached.category,
                    "resumo": cached.summary,
                    "sugestao_resposta": cached.suggested_response,
                    "cached": True,
                }

        # Gerar prompt e chamar LLM
        prompt = self._build_prompt(email_content)
        llm_response = self.llm_provider.generate(prompt)

        if not llm_response.success:
            logger.error(f"LLM error: {llm_response.error_message}")
            return {"error": llm_response.error_message}

        # Parse da resposta JSON
        try:
            analysis_result = json.loads(llm_response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            return {"error": "Invalid response format from AI"}

        # Validar estrutura da resposta
        required_keys = ["categoria", "resumo", "sugestao_resposta"]
        if not all(key in analysis_result for key in required_keys):
            logger.error(
                f"Missing required keys in LLM response: {list(analysis_result.keys())}"
            )
            return {"error": "Incomplete response from AI"}

        # Armazenar no banco de dados (falha silenciosa para não impactar o usuário)
        if store_in_db:
            try:
                self.repository.create(
                    content_hash=content_hash,
                    # Limita o tamanho armazenado — ver _EMAIL_CONTENT_MAX_STORE
                    email_content=email_content[:_EMAIL_CONTENT_MAX_STORE],
                    category=analysis_result["categoria"],
                    summary=analysis_result["resumo"],
                    suggested_response=analysis_result["sugestao_resposta"],
                    processing_time_ms=llm_response.processing_time_ms,
                    model_used=llm_response.model_used,
                )
            except Exception as e:
                logger.error(f"Failed to store analysis in database: {e}")
                # Não falha a requisição se o DB falhar

        analysis_result["cached"] = False
        return analysis_result

    # ── Métodos auxiliares ────────────────────────────────────────────────────

    def _generate_hash(self, content: str) -> str:
        """Gera hash SHA-256 do conteúdo do email."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _build_prompt(self, email_content: str) -> str:
        """Constrói o prompt enviado ao LLM."""
        return f"""
Analise o conteúdo do email a seguir e retorne uma análise estruturada em formato JSON.

O JSON de saída deve ter exatamente três chaves:
1. "categoria": Classifique o email como "Produtivo" ou "Improdutivo".
   - "Produtivo": Emails que exigem uma ação (solicitações, dúvidas, relatórios, documentações, etc.).
   - "Improdutivo": Emails que não necessitam de ação (felicitações, spam, confirmações automáticas, etc.).
2. "resumo": Crie um resumo conciso de uma frase sobre o que se trata o email.
3. "sugestao_resposta":
   - Se "Produtivo": elabore uma resposta curta e profissional como ponto de partida.
   - Se "Improdutivo": o valor deve ser exatamente "Nenhuma ação necessária."

Email para analisar:
---
{email_content}
---

Retorne apenas o objeto JSON, sem texto adicional.
"""
