from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class ChildGuardianCreate(BaseModel):
    child_id: UUID
    guardian_id: UUID
    relationship_type: str = Field(min_length=2, max_length=40)
    can_view: bool = True
    can_manage_routine: bool = False
    can_mark_notifications: bool = True


class ChildGuardianRead(Timestamped):
    child_id: UUID
    guardian_id: UUID
    relationship_type: str
    can_view: bool
    can_manage_routine: bool
    can_mark_notifications: bool



class GuardianProfileUpsert(BaseModel):
    phone: str | None = Field(default=None, max_length=20)
    preferred_channel: str = Field(default="app", pattern="^(app|email|whatsapp)$")
    daily_summary_time: str | None = Field(default=None, pattern="^([01][0-9]|2[0-3]):[0-5][0-9]$")
    evening_activity_time: str | None = Field(default=None, pattern="^([01][0-9]|2[0-3]):[0-5][0-9]$")
    notification_preferences: dict | None = None
    onboarding_completed: bool = False


class GuardianProfileRead(Timestamped):
    guardian_id: UUID
    phone: str | None
    preferred_channel: str
    daily_summary_time: str | None
    evening_activity_time: str | None
    notification_preferences: dict | None
    onboarding_completed: bool