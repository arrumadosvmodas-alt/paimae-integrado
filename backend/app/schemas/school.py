from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class SchoolCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    document: str | None = Field(default=None, max_length=32)


class SchoolRead(Timestamped):
    name: str
    document: str | None
    is_active: bool

