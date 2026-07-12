from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class NotificationGenerateRequest(BaseModel):
    target_date: date
    child_id: UUID | None = None


class NotificationStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|read|completed|cancelled)$")


class NotificationRead(Timestamped):
    child_id: UUID
    routine_item_id: UUID | None
    title: str
    message: str | None
    scheduled_at: datetime
    status: str
    target_audience: str
    read_at: datetime | None
    completed_at: datetime | None

