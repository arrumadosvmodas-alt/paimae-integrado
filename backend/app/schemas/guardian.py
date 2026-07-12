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

