from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.school import School
from app.models.user import User
from app.schemas.school import SchoolCreate, SchoolRead
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

