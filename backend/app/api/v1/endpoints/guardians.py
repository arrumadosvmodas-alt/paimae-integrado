from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child_guardian import ChildGuardian
from app.models.user import User
from app.schemas.guardian import ChildGuardianCreate, ChildGuardianRead
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, scoped_child_ids_query

router = APIRouter()


@router.post("", response_model=ChildGuardianRead, status_code=status.HTTP_201_CREATED)
def create_child_guardian(
    payload: ChildGuardianCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = ensure_child_access(db, current_user, payload.child_id)
    link = ChildGuardian(**payload.model_dump())
    db.add(link)
    db.flush()
    record_audit(
        db,
        actor=current_user,
        action="child_guardian.create",
        entity_type="child_guardian",
        entity_id=link.id,
        school_id=child.school_id,
        payload={"guardian_id": str(payload.guardian_id), "child_id": str(payload.child_id)},
    )
    db.commit()
    db.refresh(link)
    return link


@router.get("", response_model=list[ChildGuardianRead])
def list_child_guardians(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], child_id: UUID | None = None):
    query = select(ChildGuardian)
    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(ChildGuardian.child_id == child_id)
    elif current_user.role != "admin":
        query = query.where(ChildGuardian.child_id.in_(scoped_child_ids_query(current_user)))
    return list(db.scalars(query))
