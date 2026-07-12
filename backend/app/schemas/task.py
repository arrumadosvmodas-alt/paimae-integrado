from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class TaskCreate(BaseModel):
    child_id: UUID
    title: str = Field(min_length=2, max_length=180)
    description: str | None = None
    due_date: date | None = None


class TaskStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|in_progress|completed|cancelled)$")


class TaskRead(Timestamped):
    child_id: UUID
    title: str
    description: str | None
    due_date: date | None
    status: str

