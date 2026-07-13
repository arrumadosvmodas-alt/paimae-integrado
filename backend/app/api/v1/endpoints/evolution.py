from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.evolution import EvolutionEvent
from app.models.user import User
from app.schemas.evolution import EvolutionEventCreate, EvolutionEventRead
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_school_staff

router = APIRouter()


@router.post("", response_model=EvolutionEventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EvolutionEventCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    ensure_school_staff(current_user)
    child = ensure_child_access(db, current_user, payload.child_id)
    event = EvolutionEvent(**payload.model_dump())
    db.add(event)
    db.flush()
    record_audit(db, actor=current_user, action="evolution_event.create", entity_type="evolution_event", entity_id=event.id, school_id=child.school_id)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EvolutionEventRead])
def list_events(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], child_id: UUID):
    ensure_child_access(db, current_user, child_id)
    query = select(EvolutionEvent).where(EvolutionEvent.child_id == child_id).order_by(EvolutionEvent.occurred_at.desc()).limit(100)
    return list(db.scalars(query))
