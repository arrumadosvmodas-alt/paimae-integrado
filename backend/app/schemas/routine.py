from datetime import time
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class RoutineItemCreate(BaseModel):
    child_id: UUID
    title: str = Field(min_length=2, max_length=180)
    description: str | None = Field(default=None, max_length=500)
    scheduled_time: time
    weekdays: list[int] = Field(min_length=1, max_length=7)
    target_audience: str = Field(default="child", pattern="^(child|guardian|both)$")


class RoutineItemRead(Timestamped):
    child_id: UUID
    title: str
    description: str | None
    scheduled_time: time
    weekdays: list[int]
    target_audience: str
    is_active: bool

