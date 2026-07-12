from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class EvolutionEventCreate(BaseModel):
    child_id: UUID
    event_type: str = Field(min_length=2, max_length=80)
    occurred_at: datetime
    score: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = None
    event_metadata: dict | None = None


class EvolutionEventRead(Timestamped):
    child_id: UUID
    event_type: str
    occurred_at: datetime
    score: int | None
    notes: str | None
    event_metadata: dict | None

