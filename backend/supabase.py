"""
Configuração Supabase para banco de dados e autenticação.
"""
import os
from supabase import create_client, Client
from typing import Optional

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

supabase: Optional[Client] = None


def init_supabase() -> Client:
    """Inicializa cliente Supabase."""
    global supabase
    if not supabase:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase


def get_supabase() -> Client:
    """Retorna cliente Supabase inicializado."""
    global supabase
    if not supabase:
        init_supabase()
    return supabase
