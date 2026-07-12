from datetime import datetime
from uuid import UUID

from app.schemas.common import ORMModel


class AuditLogRead(ORMModel):
    id: UUID
    actor_user_id: UUID | None
    action: str
    entity_type: str
    entity_id: UUID | None
    school_id: UUID | None
    payload: dict | None
    created_at: datetime

