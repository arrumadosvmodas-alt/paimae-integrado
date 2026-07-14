"""Schemas para integrações."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class IntegrationBase(BaseModel):
    """Base para integração."""

    provider: str
    name: str
    credentials: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    sync_enabled: bool = False
    sync_interval_minutes: int = 60


class IntegrationCreate(IntegrationBase):
    """Criar integração."""

    pass


class IntegrationUpdate(BaseModel):
    """Atualizar integração."""

    name: Optional[str] = None
    credentials: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    sync_enabled: Optional[bool] = None
    sync_interval_minutes: Optional[int] = None


class IntegrationResponse(IntegrationBase):
    """Resposta de integração."""

    id: UUID
    school_id: UUID
    is_active: bool
    webhook_url: Optional[str] = None
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebhookSubscriptionBase(BaseModel):
    """Base para inscrição de webhook."""

    name: str
    url: str
    secret: str
    events: List[str]  # ["assignment.created", "grade.updated"]
    filters: Optional[Dict[str, Any]] = None


class WebhookSubscriptionCreate(WebhookSubscriptionBase):
    """Criar inscrição de webhook."""

    pass


class WebhookSubscriptionUpdate(BaseModel):
    """Atualizar inscrição."""

    name: Optional[str] = None
    url: Optional[str] = None
    secret: Optional[str] = None
    events: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class WebhookSubscriptionResponse(WebhookSubscriptionBase):
    """Resposta de inscrição."""

    id: UUID
    school_id: UUID
    active: bool
    total_delivered: int
    total_failed: int
    last_delivery: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class GoogleClassroomSyncCreate(BaseModel):
    """Sincronizar Google Classroom."""

    classroom_id: str
    classroom_name: str
    teacher_email: str
    sync_assignments: bool = True
    sync_grades: bool = True
    sync_announcements: bool = False


class MicrosoftTeamsSyncCreate(BaseModel):
    """Sincronizar Microsoft Teams."""

    team_id: str
    team_name: str
    channel_id: str
    channel_name: str
    sync_assignments: bool = True
    sync_messages: bool = False
    post_to_channel: bool = True


class WhatsAppBusinessSyncCreate(BaseModel):
    """Sincronizar WhatsApp Business."""

    phone_number: str
    guardian_id: Optional[UUID] = None
    send_notifications: bool = True
    send_grades: bool = False
    send_assignments: bool = True


class WebhookEventBase(BaseModel):
    """Base para evento de webhook."""

    event_type: str
    payload: Dict[str, Any]


class WebhookEventResponse(WebhookEventBase):
    """Resposta de evento."""

    id: UUID
    integration_id: Optional[UUID] = None
    processed: bool
    error: Optional[str] = None
    received_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class IntegrationSyncLogResponse(BaseModel):
    """Resposta de log de sincronização."""

    id: UUID
    integration_id: UUID
    status: str  # success, error, partial
    records_synced: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
