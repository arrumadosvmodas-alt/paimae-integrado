from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationGenerateRequest, NotificationRead, NotificationStatusUpdate
from app.services.audit import record_audit
from app.services.notifications import generate_notifications_for_date
from app.services.permissions import ensure_child_access, scoped_child_ids_query

router = APIRouter()


@router.post("/generate", response_model=list[NotificationRead])
def generate(payload: NotificationGenerateRequest, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if payload.child_id:
        child = ensure_child_access(db, current_user, payload.child_id, mark_notifications=True)
        school_id = child.school_id
    else:
        school_id = current_user.school_id
    created = generate_notifications_for_date(
        db,
        payload.target_date,
        child_id=payload.child_id,
        child_ids_query=None if payload.child_id else scoped_child_ids_query(current_user),
    )
    record_audit(
        db,
        actor=current_user,
        action="notification.generate",
        entity_type="notification",
        school_id=school_id,
        payload={"target_date": str(payload.target_date), "created": len(created)},
    )
    db.commit()
    for item in created:
        db.refresh(item)
    return created


@router.get("", response_model=list[NotificationRead])
def list_notifications(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], child_id: UUID | None = None):
    query = select(Notification).order_by(Notification.scheduled_at.desc()).limit(100)
    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(Notification.child_id == child_id)
    else:
        query = query.where(Notification.child_id.in_(scoped_child_ids_query(current_user)))
    return list(db.scalars(query))


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_read(notification_id: UUID, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    notification = db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    child = ensure_child_access(db, current_user, notification.child_id, mark_notifications=True)
    notification.status = "read"
    notification.read_at = datetime.now(UTC)
    record_audit(db, actor=current_user, action="notification.read", entity_type="notification", entity_id=notification.id, school_id=child.school_id)
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/{notification_id}/complete", response_model=NotificationRead)
def mark_complete(notification_id: UUID, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    notification = db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    child = ensure_child_access(db, current_user, notification.child_id, mark_notifications=True)
    now = datetime.now(UTC)
    notification.status = "completed"
    notification.read_at = notification.read_at or now
    notification.completed_at = now
    record_audit(db, actor=current_user, action="notification.complete", entity_type="notification", entity_id=notification.id, school_id=child.school_id)
    db.commit()
    db.refresh(notification)
    return notification


@router.patch("/{notification_id}/status", response_model=NotificationRead)
def update_status(
    notification_id: UUID,
    payload: NotificationStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    notification = db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    child = ensure_child_access(db, current_user, notification.child_id, mark_notifications=True)
    notification.status = payload.status
    record_audit(db, actor=current_user, action="notification.status_update", entity_type="notification", entity_id=notification.id, school_id=child.school_id, payload=payload.model_dump())
    db.commit()
    db.refresh(notification)
    return notification
