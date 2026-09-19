"""
Módulo de Mascaramento Automático de PII (Personally Identifiable Information).
Sanitiza dados sensíveis (CPFs, CNPJs, Cartões, Chaves PIX, Contas bancárias)
localmente ANTES do payload ser transmitido para qualquer provedor LLM externo.
Conformidade rigorosa com LGPD e GDPR.
"""
import re
from typing import Tuple, Dict, Any, List


# Regexes compilados para performance
_CPF_REGEX = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}[-.]?\d{2}\b")
_CNPJ_REGEX = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}[-.]?\d{2}\b")
_CREDIT_CARD_REGEX = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{13,19}\b")
_EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_REGEX = re.compile(r"(?:\+?55\s?)?(?:\(?0?[1-9]{2}\)?\s?)?(?:9[.\s]?\d{4}|\d{4})[-.\s]?\d{4}\b")
_BANK_ACCOUNT_REGEX = re.compile(r"(?i)\b(?:ag[eê]ncia|ag|conta|cc|c/c|cta)[:\s]+(\d{3,6}(?:-\d)?)\b")
_PIX_UUID_REGEX = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")


def sanitize_pii(text: str, mask_emails: bool = False) -> Tuple[str, Dict[str, Any]]:
    """
    Sanitiza PII no texto substituindo dados sensíveis por placeholders seguros.
    
    Args:
        text: Texto original com possíveis dados confidenciais.
        mask_emails: Se True, mascara também emails no corpo do texto.
        
    Returns:
        Tuple contendo:
        1. Texto sanitizado seguro para envio a LLM externo.
        2. Dicionário de estatísticas e metadados de mascaramento.
    """
    if not text:
        return text, {"masked": False, "counts": {}}

    sanitized = text
    counts = {
        "cpf": 0,
        "cnpj": 0,
        "credit_card": 0,
        "phone": 0,
        "bank_data": 0,
        "pix_key": 0,
        "email": 0,
    }

    # 1. Cartão de crédito (executado antes de CPF para não sobrepor padrões)
    def _mask_cc(match):
        val = match.group(0)
        # Ignora números curtos ou anos
        digits_only = re.sub(r"\D", "", val)
        if len(digits_only) in [13, 15, 16, 19]:
            counts["credit_card"] += 1
            return f"[CARTAO_CREDITO_MASCARADO_{counts['credit_card']}]"
        return val

    sanitized = _CREDIT_CARD_REGEX.sub(_mask_cc, sanitized)

    # 2. CNPJ
    def _mask_cnpj(match):
        counts["cnpj"] += 1
        return f"[CNPJ_MASCARADO_{counts['cnpj']}]"

    sanitized = _CNPJ_REGEX.sub(_mask_cnpj, sanitized)

    # 3. CPF
    def _mask_cpf(match):
        counts["cpf"] += 1
        return f"[CPF_MASCARADO_{counts['cpf']}]"

    sanitized = _CPF_REGEX.sub(_mask_cpf, sanitized)

    # 4. Chave PIX Aleatória (UUID)
    def _mask_pix(match):
        counts["pix_key"] += 1
        return f"[CHAVE_PIX_MASCARADA_{counts['pix_key']}]"

    sanitized = _PIX_UUID_REGEX.sub(_mask_pix, sanitized)

    # 5. Dados bancários explícitos (Agência / Conta)
    def _mask_bank(match):
        counts["bank_data"] += 1
        return f"[DADOS_BANCARIOS_MASCARADOS_{counts['bank_data']}]"

    sanitized = _BANK_ACCOUNT_REGEX.sub(_mask_bank, sanitized)

    # 6. Telefones
    def _mask_phone(match):
        val = match.group(0)
        digits = re.sub(r"\D", "", val)
        if 8 <= len(digits) <= 13:
            counts["phone"] += 1
            return f"[TELEFONE_MASCARADO_{counts['phone']}]"
        return val

    sanitized = _PHONE_REGEX.sub(_mask_phone, sanitized)

    # 7. Emails (opcional no corpo)
    if mask_emails:
        def _mask_email(match):
            counts["email"] += 1
            return f"[EMAIL_MASCARADO_{counts['email']}]"

        sanitized = _EMAIL_REGEX.sub(_mask_email, sanitized)

    total_masked = sum(counts.values())
    metadata = {
        "masked": total_masked > 0,
        "total_items_masked": total_masked,
        "counts": counts,
    }

    return sanitized, metadata
