"""
Módulo de Criptografia At-Rest para proteção de dados sensíveis em repouso.
Criptografa payloads de emails no banco de dados usando Fernet (AES-128-CBC + HMAC SHA-256).
"""
import base64
import hashlib
import os
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

_fernet_instance: Optional[Fernet] = None


def _get_fernet() -> Optional[Fernet]:
    """Obtém ou inicializa a instância Fernet a partir da chave configurada."""
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    key = os.getenv("DATA_ENCRYPTION_KEY")
    if not key:
        # Chave padrão derivada do SECRET_KEY para ambientes de dev/testes
        secret = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        # Gera uma chave Fernet válida de 32 bytes em base64 urlsafe
        key_bytes = hashlib.sha256(secret.encode()).digest()
        key = base64.urlsafe_b64encode(key_bytes).decode()

    try:
        _fernet_instance = Fernet(key.encode() if isinstance(key, str) else key)
        return _fernet_instance
    except Exception as e:
        logger.error(f"Failed to initialize Fernet encryption: {e}")
        return None


def encrypt_text(plaintext: Optional[str]) -> Optional[str]:
    """
    Criptografa texto para armazenamento seguro no banco de dados.
    Prefixa o resultado com 'enc::' para identificação unívoca de campos cifrados.
    """
    if plaintext is None or plaintext == "":
        return plaintext

    # Se já estiver criptografado
    if plaintext.startswith("enc::"):
        return plaintext

    fernet = _get_fernet()
    if not fernet:
        return plaintext

    try:
        encrypted_bytes = fernet.encrypt(plaintext.encode("utf-8"))
        return f"enc::{encrypted_bytes.decode('utf-8')}"
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return plaintext


def decrypt_text(ciphertext: Optional[str]) -> Optional[str]:
    """
    Decifra texto armazenado no banco de dados se possuir o prefixo 'enc::'.
    Se não estiver cifrado, retorna o texto original de forma transparente.
    """
    if ciphertext is None or ciphertext == "":
        return ciphertext

    if not ciphertext.startswith("enc::"):
        return ciphertext

    fernet = _get_fernet()
    if not fernet:
        return ciphertext

    try:
        raw_token = ciphertext[5:].encode("utf-8")
        decrypted_bytes = fernet.decrypt(raw_token)
        return decrypted_bytes.decode("utf-8")
    except InvalidToken:
        logger.warning("Failed to decrypt data: Invalid encryption token or key mismatch.")
        return ciphertext
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        return ciphertext
