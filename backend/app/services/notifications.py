from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import Notification
from app.models.routine import RoutineItem


def _scheduled_at(target_date: date, routine: RoutineItem) -> datetime:
    tz = ZoneInfo(settings.app_timezone)
    local_dt = datetime.combine(target_date, routine.scheduled_time, tzinfo=tz)
    return local_dt.astimezone(UTC)


def generate_notifications_for_date(
    db: Session,
    target_date: date,
    child_id: UUID | None = None,
    child_ids_query=None,
) -> list[Notification]:
    weekday = target_date.weekday()
    query = select(RoutineItem).where(
        RoutineItem.is_active.is_(True),
        RoutineItem.weekdays.any(weekday),
    )
    if child_id:
        query = query.where(RoutineItem.child_id == child_id)
    elif child_ids_query is not None:
        query = query.where(RoutineItem.child_id.in_(child_ids_query))
    created: list[Notification] = []
    for routine in db.scalars(query):
        scheduled_at = _scheduled_at(target_date, routine)
        exists = db.scalar(
            select(Notification).where(
                Notification.routine_item_id == routine.id,
                Notification.scheduled_at == scheduled_at,
            )
        )
        if exists:
            continue
        notification = Notification(
            child_id=routine.child_id,
            routine_item_id=routine.id,
            title=routine.title,
            message=routine.description,
            scheduled_at=scheduled_at,
            target_audience=routine.target_audience,
        )
        db.add(notification)
        created.append(notification)
    db.flush()
    return created
