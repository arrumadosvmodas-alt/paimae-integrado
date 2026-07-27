"""Criptografia simetrica para dados sensiveis armazenados em repouso.

Usado para credenciais/sessoes de integracoes pessoais (ex: cookie de sessao
do ClipEscola), que nao devem ficar em texto plano no banco.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _fernet() -> Fernet:
    key = settings.encryption_key
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY nao configurada. Defina uma chave Fernet valida "
            "(ex: gerada com `Fernet.generate_key()`) na variavel de ambiente ENCRYPTION_KEY."
        )
    # Aceita tanto uma chave Fernet valida (32 bytes urlsafe-base64) quanto
    # uma string arbitraria, derivando uma chave valida via SHA-256.
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except (ValueError, TypeError):
        derived = base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest())
        return Fernet(derived)


def encrypt_str(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_str(token: str) -> str:
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise ValueError("Nao foi possivel descriptografar o valor: token invalido ou chave incorreta.") from exc
