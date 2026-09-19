"""
Módulo de Prevenção de Perda de Dados (DLP - Data Loss Prevention) de Saída (#38).
Inspeciona as respostas geradas antes da exibição ao operador para evitar
o vazamento acidental de chaves de API, credenciais, conexões de banco de dados ou IPs internos.
"""
import re
from typing import Tuple, Dict, Any, List

# Padrões de segredos e credenciais
_API_KEY_PATTERNS = [
    re.compile(r"(?i)(?:api[_-]?key|secret|token|password|senha)[:=\s]+(['\"]?[A-Za-z0-9_\-\.]{16,}['\"]?)"),
    re.compile(r"\b(?:sk_live|ak_live|whsec|ghp_|AIzaSy)[A-Za-z0-9_\-]{16,}\b"),
]

# URLs de conexões internas de bancos de dados
_DB_URL_PATTERN = re.compile(r"(?i)(?:postgresql|postgres|mysql|mongodb|redis):\/\/[^\s]+(?::[^\s]+)?@[^\s]+")

# Endereços IPv4 privados internos (RFC 1918)
_INTERNAL_IP_PATTERN = re.compile(r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3})\b")

# Dados financeiros confidenciais
_INTERNAL_CARD_PATTERN = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
_INTERNAL_PASSWORD_PATTERN = re.compile(r"(?i)\bsenha[:\s]+[^\s]{4,30}\b")


def inspect_and_filter_dlp(text: str) -> Tuple[str, Dict[str, Any]]:
    """
    Inspeciona e filtra dados confidenciais de saída (DLP).
    
    Args:
        text: Texto da resposta sugerida ou mensagem de saída.
        
    Returns:
        Tuple contendo:
        1. Texto filtrado seguro.
        2. Metadados de violações DLP interceptadas.
    """
    if not text:
        return text, {"dlp_triggered": False, "violations": []}

    sanitized = text
    violations: List[str] = []

    # 1. Checagem de Database URIs
    if _DB_URL_PATTERN.search(sanitized):
        violations.append("database_uri")
        sanitized = _DB_URL_PATTERN.sub("[REDACTED_DATABASE_URI]", sanitized)

    # 2. Checagem de API Keys / Segredos
    for pattern in _API_KEY_PATTERNS:
        if pattern.search(sanitized):
            violations.append("api_key")
            sanitized = pattern.sub("[REDACTED_SECRET]", sanitized)

    # 3. Checagem de IPs internos
    if _INTERNAL_IP_PATTERN.search(sanitized):
        violations.append("internal_ip")
        sanitized = _INTERNAL_IP_PATTERN.sub("[REDACTED_INTERNAL_IP]", sanitized)

    # 4. Checagem de Senhas em texto puro
    if _INTERNAL_PASSWORD_PATTERN.search(sanitized):
        violations.append("plaintext_password")
        sanitized = _INTERNAL_PASSWORD_PATTERN.sub("[REDACTED_SECRET]", sanitized)

    # 5. Checagem de Cartões
    if _INTERNAL_CARD_PATTERN.search(sanitized):
        violations.append("credit_card")
        sanitized = _INTERNAL_CARD_PATTERN.sub("[REDACTED_FINANCIAL]", sanitized)

    triggered = len(violations) > 0
    return sanitized, {
        "dlp_triggered": triggered,
        "violations": list(set(violations)),
        "is_safe": not triggered,
    }


def sanitize_outbound_response(text: str) -> str:
    """Retorna apenas o texto sanitizado pelo filtro DLP."""
    sanitized, _ = inspect_and_filter_dlp(text)
    return sanitized


def check_dlp_violations(text: str) -> List[Dict[str, str]]:
    """Retorna lista de violações identificadas sem modificar o texto original."""
    _, meta = inspect_and_filter_dlp(text)
    return [{"rule": v} for v in meta.get("violations", [])]

