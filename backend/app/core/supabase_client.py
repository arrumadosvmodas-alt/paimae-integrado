"""
Configuração Supabase para armazenamento (Supabase Storage).
"""
from typing import Optional

from supabase import create_client, Client

from app.core.config import settings

_client: Optional[Client] = None


def init_supabase() -> Client:
    """Inicializa cliente Supabase."""
    global _client
    if not _client:
        _client = create_client(settings.supabase_url, settings.supabase_key)
    return _client


def get_supabase() -> Client:
    """Retorna cliente Supabase inicializado."""
    global _client
    if not _client:
        return init_supabase()
    return _client
