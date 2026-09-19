"""
Testes unitários para o módulo de criptografia at-rest.
"""
from backend.app.utils.crypto import encrypt_text, decrypt_text


def test_encryption_and_decryption_cycle():
    secret_text = "Texto confidencial de email corporativo bancário."
    encrypted = encrypt_text(secret_text)
    
    assert encrypted != secret_text
    assert encrypted.startswith("enc::")
    
    decrypted = decrypt_text(encrypted)
    assert decrypted == secret_text


def test_decrypt_plaintext_passthrough():
    plaintext = "Texto legado não criptografado."
    assert decrypt_text(plaintext) == plaintext


def test_encrypt_idempotence():
    text = "Meu texto."
    encrypted1 = encrypt_text(text)
    encrypted2 = encrypt_text(encrypted1)
    assert encrypted1 == encrypted2
