from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserRead
from app.services.audit import record_audit
from app.services.permissions import ensure_admin

router = APIRouter()


@router.post("/bootstrap-admin", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    if payload.role != "admin":
        raise HTTPException(status_code=400, detail="Bootstrap user must be admin")
    users_count = db.scalar(select(func.count(User.id)))
    if users_count:
        raise HTTPException(status_code=409, detail="Bootstrap already completed")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role="admin",
        school_id=None,
    )
    db.add(user)
    db.flush()
    record_audit(db, actor=user, action="auth.bootstrap_admin", entity_type="user", entity_id=user.id)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id), {"role": user.role, "school_id": str(user.school_id) if user.school_id else None})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=payload.role,
        school_id=payload.school_id,
    )
    db.add(user)
    db.flush()
    record_audit(db, actor=current_user, action="user.create", entity_type="user", entity_id=user.id, school_id=user.school_id)
    db.commit()
    db.refresh(user)
    return user

