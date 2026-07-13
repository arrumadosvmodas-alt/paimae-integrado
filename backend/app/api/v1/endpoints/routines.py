from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.routine import RoutineItem
from app.models.user import User
from app.schemas.routine import RoutineItemCreate, RoutineItemRead
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, scoped_child_ids_query, ensure_school_staff

router = APIRouter()


@router.post("", response_model=RoutineItemRead, status_code=status.HTTP_201_CREATED)
def create_routine(payload: RoutineItemCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    ensure_school_staff(current_user)
    child = ensure_child_access(db, current_user, payload.child_id, manage_routine=True)
    routine = RoutineItem(**payload.model_dump())
    db.add(routine)
    db.flush()
    record_audit(db, actor=current_user, action="routine.create", entity_type="routine_item", entity_id=routine.id, school_id=child.school_id)
    db.commit()
    db.refresh(routine)
    return routine


@router.get("", response_model=list[RoutineItemRead])
def list_routines(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], child_id: UUID | None = None):
    query = select(RoutineItem).where(RoutineItem.is_active.is_(True)).order_by(RoutineItem.scheduled_time)
    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(RoutineItem.child_id == child_id)
    else:
        query = query.where(RoutineItem.child_id.in_(scoped_child_ids_query(current_user)))
    return list(db.scalars(query))
