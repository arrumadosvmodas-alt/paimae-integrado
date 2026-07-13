from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.school import School
from app.models.user import User
from app.schemas.common import ActiveStatusUpdate
from app.schemas.school import SchoolCreate, SchoolRead, SchoolUpdate
from app.services.audit import record_audit
from app.services.permissions import ensure_admin

router = APIRouter()


@router.post("", response_model=SchoolRead, status_code=status.HTTP_201_CREATED)
def create_school(payload: SchoolCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    ensure_admin(current_user)
    school = School(**payload.model_dump())
    db.add(school)
    db.flush()
    record_audit(db, actor=current_user, action="school.create", entity_type="school", entity_id=school.id, school_id=school.id)
    db.commit()
    db.refresh(school)
    return school


@router.get("", response_model=list[SchoolRead])
def list_schools(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role == "admin":
        return list(db.scalars(select(School).order_by(School.name)))
    if current_user.school_id:
        school = db.get(School, current_user.school_id)
        return [school] if school else []
    return []


@router.put("/{school_id}", response_model=SchoolRead)
def update_school(
    school_id: UUID,
    payload: SchoolUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    school = db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="Escola não encontrada.")
    
    school.name = payload.name
    school.document = payload.document
    record_audit(db, actor=current_user, action="school.update", entity_type="school", entity_id=school.id, school_id=school.id)
    db.commit()
    db.refresh(school)
    return school


@router.patch("/{school_id}/status", response_model=SchoolRead)
def update_school_status(
    school_id: UUID,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    school = db.get(School, school_id)
    if not school:
        raise HTTPException(status_code=404, detail="Escola não encontrada.")
    
    previous_status = school.is_active
    school.is_active = payload.is_active
    record_audit(
        db,
        actor=current_user,
        action="school.status_update",
        entity_type="school",
        entity_id=school.id,
        school_id=school.id,
        payload={"previous_is_active": previous_status, "is_active": school.is_active},
    )
    db.commit()
    db.refresh(school)
    return school
