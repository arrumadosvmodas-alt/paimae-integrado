"""Schemas para a integração pessoal com o ClipEscola."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ClipEscolaPairingResponse(BaseModel):
    account_id: UUID
    qr_image_base64: str


class ClipEscolaStatusResponse(BaseModel):
    account_id: Optional[UUID] = None
    status: str  # not_configured, pending_pairing, active, needs_reauth
    last_synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClipEscolaSyncResponse(BaseModel):
    status: str
    schedules_created: int = 0
    messages_read: int = 0
    message: Optional[str] = None
