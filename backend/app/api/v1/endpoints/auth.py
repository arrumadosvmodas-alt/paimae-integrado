from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserRead, UserUpdate
from app.schemas.common import ActiveStatusUpdate
from app.services.audit import record_audit
from app.services.permissions import ensure_admin

router = APIRouter()


@router.post("/bootstrap-admin", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    if payload.role != "admin":
        raise HTTPException(status_code=400, detail="Bootstrap user must be admin")
    existing = db.scalar(select(User).where(User.email == payload.email.lower()))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
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
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
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


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    return db.scalars(select(User)).all()


@router.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check email duplicate
    if payload.email.lower() != user.email:
        existing = db.scalar(select(func.count(User.id)).where(User.email == payload.email.lower()))
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
            
    user.name = payload.name
    user.email = payload.email.lower()
    if payload.password:
        user.password_hash = hash_password(payload.password)
    user.role = payload.role
    user.school_id = payload.school_id
    
    record_audit(db, actor=current_user, action="user.update", entity_type="user", entity_id=user.id, school_id=user.school_id)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/status", response_model=UserRead)
def update_user_status(
    user_id: str,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    previous_status = user.is_active
    user.is_active = payload.is_active
    record_audit(
        db,
        actor=current_user,
        action="user.status_update",
        entity_type="user",
        entity_id=user.id,
        school_id=user.school_id,
        payload={"previous_is_active": previous_status, "is_active": user.is_active},
    )
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_admin(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    from sqlalchemy import delete
    from app.models.child_guardian import ChildGuardian
    db.execute(delete(ChildGuardian).where(ChildGuardian.guardian_id == user.id))
    
    db.delete(user)
    db.commit()
    return

