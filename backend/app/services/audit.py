from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def record_audit(
    db: Session,
    *,
    actor: User | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    school_id: UUID | None = None,
    payload: dict | None = None,
) -> AuditLog:
    log = AuditLog(
        actor_user_id=actor.id if actor else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        school_id=school_id,
        payload=payload,
    )
    db.add(log)
    return log

