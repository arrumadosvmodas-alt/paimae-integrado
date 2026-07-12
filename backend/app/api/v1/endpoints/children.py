from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.child_guardian import ChildGuardian
from app.models.user import User
from app.schemas.child import ChildCreate, ChildRead
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_school_access

router = APIRouter()


@router.post("", response_model=ChildRead, status_code=status.HTTP_201_CREATED)
def create_child(payload: ChildCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    ensure_school_access(current_user, payload.school_id)
    child = Child(**payload.model_dump())
    db.add(child)
    db.flush()
    record_audit(db, actor=current_user, action="child.create", entity_type="child", entity_id=child.id, school_id=child.school_id)
    db.commit()
    db.refresh(child)
    return child


@router.get("", response_model=list[ChildRead])
def list_children(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    query = select(Child).where(Child.is_active.is_(True)).order_by(Child.full_name)
    if current_user.role == "admin":
        return list(db.scalars(query))
    if current_user.school_id:
        return list(db.scalars(query.where(Child.school_id == current_user.school_id)))
    linked_ids = select(ChildGuardian.child_id).where(ChildGuardian.guardian_id == current_user.id, ChildGuardian.can_view.is_(True))
    return list(db.scalars(query.where(Child.id.in_(linked_ids))))


@router.get("/{child_id}", response_model=ChildRead)
def get_child(child_id: UUID, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    return ensure_child_access(db, current_user, child_id)
