from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.child_guardian import ChildGuardian
from app.models.user import User


def ensure_admin(user: User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")


def ensure_school_access(user: User, school_id: UUID) -> None:
    if user.role == "admin":
        return
    if user.school_id == school_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="School access denied")


def get_child_or_404(db: Session, child_id: UUID) -> Child:
    child = db.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")
    return child


def ensure_child_access(
    db: Session,
    user: User,
    child_id: UUID,
    *,
    manage_routine: bool = False,
    mark_notifications: bool = False,
) -> Child:
    child = get_child_or_404(db, child_id)
    if user.role == "admin" or user.school_id == child.school_id:
        return child
    link = db.scalar(
        select(ChildGuardian).where(
            ChildGuardian.child_id == child_id,
            ChildGuardian.guardian_id == user.id,
            ChildGuardian.can_view.is_(True),
        )
    )
    if link and manage_routine and not link.can_manage_routine:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Routine management denied")
    if link and mark_notifications and not link.can_mark_notifications:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Notification update denied")
    if link:
        return child
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child access denied")


def scoped_child_ids_query(user: User):
    if user.role == "admin":
        return select(Child.id).where(Child.is_active.is_(True))
    if user.school_id:
        return select(Child.id).where(Child.school_id == user.school_id, Child.is_active.is_(True))
    return select(ChildGuardian.child_id).where(
        ChildGuardian.guardian_id == user.id,
        ChildGuardian.can_view.is_(True),
    )


def ensure_school_staff(user: User) -> None:
    if user.role in ("admin", "school_admin", "teacher"):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Apenas administradores e funcionarios da escola podem realizar esta acao."
    )

