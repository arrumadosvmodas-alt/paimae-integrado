from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.audit import AuditLogRead
from app.services.permissions import ensure_admin

router = APIRouter()


@router.get("", response_model=list[AuditLogRead])
def list_audit_logs(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role == "admin":
        query = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)
    else:
        ensure_admin(current_user)
    return list(db.scalars(query))
