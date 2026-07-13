from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.child_guardian import ChildGuardian
from app.models.user import User
from app.schemas.common import ActiveStatusUpdate
from app.schemas.child import ChildCreate, ChildRead, ChildUpdate
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
    query = select(Child).order_by(Child.full_name)
    if current_user.role == "admin":
        return list(db.scalars(query))
    if current_user.school_id:
        return list(db.scalars(query.where(Child.school_id == current_user.school_id)))
    linked_ids = select(ChildGuardian.child_id).where(ChildGuardian.guardian_id == current_user.id, ChildGuardian.can_view.is_(True))
    return list(db.scalars(query.where(Child.id.in_(linked_ids), Child.is_active.is_(True))))


@router.get("/{child_id}", response_model=ChildRead)
def get_child(child_id: UUID, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    return ensure_child_access(db, current_user, child_id)


@router.put("/{child_id}", response_model=ChildRead)
def update_child(
    child_id: UUID,
    payload: ChildUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = db.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Criança não encontrada.")
    ensure_school_access(current_user, child.school_id)
    ensure_school_access(current_user, payload.school_id)
    
    child.full_name = payload.full_name
    child.birth_date = payload.birth_date
    child.school_id = payload.school_id
    child.class_name = payload.class_name
    
    record_audit(db, actor=current_user, action="child.update", entity_type="child", entity_id=child.id, school_id=child.school_id)
    db.commit()
    db.refresh(child)
    return child


@router.patch("/{child_id}/status", response_model=ChildRead)
def update_child_status(
    child_id: UUID,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = db.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Criança não encontrada.")
    ensure_school_access(current_user, child.school_id)
    
    previous_status = child.is_active
    child.is_active = payload.is_active
    record_audit(
        db,
        actor=current_user,
        action="child.status_update",
        entity_type="child",
        entity_id=child.id,
        school_id=child.school_id,
        payload={"previous_is_active": previous_status, "is_active": child.is_active},
    )
    db.commit()
    db.refresh(child)
    return child
