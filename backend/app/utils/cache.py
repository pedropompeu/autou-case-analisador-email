"""
Utilitários para cache usando Redis.

O cliente Redis é armazenado em `app.extensions['redis_client']` em vez de
uma variável global do módulo. Isso evita cross-contamination entre diferentes
instâncias de aplicação criadas durante testes.
"""
import json
import logging
from typing import Optional, Any

import redis
from flask import current_app

logger = logging.getLogger(__name__)

_EXTENSION_KEY = "redis_client"


def get_redis_client() -> Optional[redis.Redis]:
    """
    Retorna o cliente Redis vinculado à instância de aplicação atual.

    O cliente é criado uma única vez por instância Flask e armazenado em
    ``app.extensions``, garantindo isolamento entre instâncias de teste.

    Returns:
        Cliente Redis ou None se não configurado/disponível.
    """
    app = current_app._get_current_object()  # type: ignore[attr-defined]

    # Retorna cliente já inicializado para esta instância
    if _EXTENSION_KEY in app.extensions:
        return app.extensions[_EXTENSION_KEY]

    # Inicializa e armazena na instância
    try:
        redis_url = app.config.get("REDIS_URL")
        if not redis_url:
            logger.warning("REDIS_URL not configured — cache disabled")
            app.extensions[_EXTENSION_KEY] = None
            return None

        client = redis.from_url(redis_url, decode_responses=True, socket_timeout=2)
        client.ping()  # Testa a conexão imediatamente
        logger.info("Redis client initialized successfully")
        app.extensions[_EXTENSION_KEY] = client
        return client

    except Exception as e:
        logger.warning(f"Failed to initialize Redis client: {e} — cache disabled")
        app.extensions[_EXTENSION_KEY] = None
        return None


def cache_get(key: str) -> Optional[Any]:
    """
    Recupera valor do cache.

    Args:
        key: Chave do cache.

    Returns:
        Valor deserializado ou None se não encontrado/erro.
    """
    client = get_redis_client()
    if not client:
        return None

    try:
        value = client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        logger.error(f"Cache get error for key '{key}': {e}")

    return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> bool:
    """
    Armazena valor no cache.

    Args:
        key: Chave do cache.
        value: Valor a armazenar (serializado como JSON).
        ttl: Tempo de vida em segundos (padrão: 1 hora).

    Returns:
        True se armazenado com sucesso, False caso contrário.
    """
    client = get_redis_client()
    if not client:
        return False

    try:
        serialized = json.dumps(value, ensure_ascii=False)
        client.setex(key, ttl, serialized)
        return True
    except Exception as e:
        logger.error(f"Cache set error for key '{key}': {e}")
        return False


def cache_delete(key: str) -> bool:
    """Remove valor do cache."""
    client = get_redis_client()
    if not client:
        return False

    try:
        client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Cache delete error for key '{key}': {e}")
        return False
