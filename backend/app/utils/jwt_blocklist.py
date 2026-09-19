"""
Módulo de Gerenciamento de JWT Blocklist com Redis.
Permite revogação instantânea de tokens de acesso (logout, detecção de anomalia, troca de senha).
"""
import logging
from typing import Optional

import redis
from flask import current_app

logger = logging.getLogger(__name__)

_in_memory_blocklist = set()
_redis_client: Optional[redis.Redis] = None


def _get_redis() -> Optional[redis.Redis]:
    """Obtém cliente Redis a partir da configuração da aplicação."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        redis_url = current_app.config.get("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(redis_url, decode_responses=True)
        _redis_client.ping()
        return _redis_client
    except Exception as e:
        logger.debug(f"Redis not available for JWT blocklist, falling back to memory: {e}")
        return None


def add_token_to_blocklist(jti: str, expires_in_seconds: int = 86400) -> None:
    """
    Adiciona o JTI (JWT Unique Identifier) na blocklist de revogação.

    Args:
        jti: Identificador único do token JWT.
        expires_in_seconds: Tempo de expiração no Redis (TTL) para autolimpeza.
    """
    r = _get_redis()
    if r:
        try:
            r.setex(f"jwt_blocklist:{jti}", expires_in_seconds, "revoked")
            return
        except Exception as e:
            logger.error(f"Failed to set JWT in Redis blocklist: {e}")

    # Fallback in-memory
    _in_memory_blocklist.add(jti)


def is_token_in_blocklist(jti: str) -> bool:
    """Verifica se o JTI está marcado como revogado."""
    r = _get_redis()
    if r:
        try:
            val = r.get(f"jwt_blocklist:{jti}")
            return val is not None
        except Exception as e:
            logger.error(f"Failed to check JWT in Redis blocklist: {e}")

    return jti in _in_memory_blocklist
