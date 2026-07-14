from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class ChildCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    birth_date: date | None = None
    school_id: UUID
    class_name: str | None = Field(default=None, max_length=80)
    grade: str | None = Field(default=None, max_length=20)
    shift: str | None = Field(default=None, max_length=20)
    preferences: dict | None = None
    difficulties: dict | None = None
    observations: str | None = None


class ChildRead(Timestamped):
    full_name: str
    birth_date: date | None
    school_id: UUID
    class_name: str | None
    grade: str | None
    shift: str | None
    preferences: dict | None
    difficulties: dict | None
    observations: str | None
    is_active: bool


class ChildUpdate(BaseModel):
    full_name: str = Field(min_length=2, max_length=180)
    birth_date: date | None = None
    school_id: UUID
    class_name: str | None = Field(default=None, max_length=80)
    grade: str | None = Field(default=None, max_length=20)
    shift: str | None = Field(default=None, max_length=20)
    preferences: dict | None = None
    difficulties: dict | None = None
    observations: str | None = None

