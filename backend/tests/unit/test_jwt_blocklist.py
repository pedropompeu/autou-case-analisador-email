"""
Testes unitários para o módulo de JWT blocklist.
"""
from backend.app.utils.jwt_blocklist import add_token_to_blocklist, is_token_in_blocklist


def test_jwt_blocklist_addition_and_check():
    jti = "test-token-uuid-12345"
    assert is_token_in_blocklist(jti) is False

    add_token_to_blocklist(jti)
    assert is_token_in_blocklist(jti) is True
