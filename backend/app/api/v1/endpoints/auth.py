from datetime import datetime, timedelta
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserRead, UserUpdate, UserFirstAccess
from app.schemas.common import ActiveStatusUpdate
from app.services.audit import record_audit
from app.services.permissions import ensure_admin

router = APIRouter()

# Dicionário em memória para Rate Limiting
login_attempts: dict[str, list[datetime]] = {}


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
        password_hash=hash_password(payload.password) if payload.password else "",
        role="admin",
        school_id=None,
        document=payload.document,
        first_access_completed=True,
    )
    db.add(user)
    db.flush()
    record_audit(db, actor=user, action="auth.bootstrap_admin", entity_type="user", entity_id=user.id)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{form.username.lower()}:{client_ip}"
    now = datetime.now()

    # Limpeza e checagem de Rate Limit
    if rate_key in login_attempts:
        login_attempts[rate_key] = [t for t in login_attempts[rate_key] if now - t < timedelta(minutes=15)]
        if len(login_attempts[rate_key]) >= 5:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas de login de forma consecutiva. Por favor, tente novamente em 15 minutos."
            )

    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if not user or not verify_password(form.password, user.password_hash):
        # Registra falha de tentativa
        if rate_key not in login_attempts:
            login_attempts[rate_key] = []
        login_attempts[rate_key].append(now)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    # Limpa tentativas em caso de sucesso
    if rate_key in login_attempts:
        del login_attempts[rate_key]

    token = create_access_token(str(user.id), {"role": user.role, "school_id": str(user.school_id) if user.school_id else None})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/lgpd-accept", response_model=UserRead)
def lgpd_accept(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    current_user.lgpd_accepted = True
    current_user.lgpd_accepted_at = datetime.now()
    db.commit()
    db.refresh(current_user)
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
    
    # Generate temporary random password if none is provided
    temp_pass = payload.password or secrets.token_urlsafe(12)
    user = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(temp_pass),
        role=payload.role,
        school_id=payload.school_id,
        document=payload.document,
        first_access_completed=True if payload.role == "admin" else False,
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
    user.document = payload.document
    
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


@router.post("/first-access", status_code=status.HTTP_200_OK)
def first_access(payload: UserFirstAccess, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
    
    # Compare names ignoring case and duplicate spaces
    registered_name = " ".join(user.name.lower().split())
    provided_name = " ".join(payload.name.lower().split())
    if registered_name != provided_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome fornecido não confere com o cadastrado pelo administrador."
        )
    
    if user.first_access_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O primeiro acesso já foi realizado para esta conta."
        )
    
    user.password_hash = hash_password(payload.password)
    user.first_access_completed = True
    db.commit()
    return {"message": "Senha cadastrada com sucesso! Faça login."}

