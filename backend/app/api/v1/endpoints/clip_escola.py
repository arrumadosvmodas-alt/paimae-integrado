"""Endpoints para o responsavel parear e sincronizar sua conta ClipEscola.

Diferente de /integrations (nivel escola, ensure_school_staff), aqui quem
gerencia e o proprio responsavel, sobre a crianca que ele acompanha - por
isso usamos ensure_child_access(manage_routine=True) em vez de
ensure_school_staff.
"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.integration import ClipEscolaAccount
from app.models.user import User
from app.schemas.clip_escola import (
    ClipEscolaDateLookupRequest,
    ClipEscolaDateLookupResponse,
    ClipEscolaPairingResponse,
    ClipEscolaStatusResponse,
    ClipEscolaSyncResponse,
)
from app.services import clip_escola as clip_escola_service
from app.services.permissions import ensure_child_access

router = APIRouter()


def _get_account_or_404(db: Session, guardian_id: UUID, child_id: UUID) -> ClipEscolaAccount:
    account = db.scalar(
        select(ClipEscolaAccount).where(
            ClipEscolaAccount.guardian_id == guardian_id,
            ClipEscolaAccount.child_id == child_id,
        )
    )
    if not account:
        raise HTTPException(status_code=404, detail="Conta ClipEscola nao configurada para esta crianca.")
    return account


@router.get("/{child_id}", response_model=ClipEscolaStatusResponse)
def get_status(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id, manage_routine=True)
    account = db.scalar(
        select(ClipEscolaAccount).where(
            ClipEscolaAccount.guardian_id == current_user.id,
            ClipEscolaAccount.child_id == child_id,
        )
    )
    if not account:
        return ClipEscolaStatusResponse(status="not_configured")
    return ClipEscolaStatusResponse(
        account_id=account.id,
        status=account.status,
        last_synced_at=account.last_synced_at,
    )


@router.post("/{child_id}/pair/start", response_model=ClipEscolaPairingResponse)
async def start_pairing(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id, manage_routine=True)
    result = await clip_escola_service.start_pairing(db, current_user.id, child_id)
    db.commit()
    return result


@router.get("/{child_id}/pair/status", response_model=ClipEscolaStatusResponse)
async def get_pairing_status(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id, manage_routine=True)
    account = _get_account_or_404(db, current_user.id, child_id)
    result = await clip_escola_service.check_pairing_status(db, account)
    db.commit()
    return ClipEscolaStatusResponse(
        account_id=account.id,
        status=result["status"],
        last_synced_at=account.last_synced_at,
        qr_image_base64=result["qr_image_base64"],
    )


@router.post("/{child_id}/sync", response_model=ClipEscolaSyncResponse)
def sync_now(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id, manage_routine=True)
    account = _get_account_or_404(db, current_user.id, child_id)
    result = clip_escola_service.sync_agenda(db, account)
    db.commit()
    return result


@router.post("/{child_id}/lookup-date", response_model=ClipEscolaDateLookupResponse)
def lookup_date(
    child_id: UUID,
    payload: ClipEscolaDateLookupRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Busca o conteudo de um dia especifico na aba Clips - usado quando a
    sincronizacao automatica nao trouxe nenhum recado para aquele dia."""
    ensure_child_access(db, current_user, child_id, manage_routine=True)
    account = _get_account_or_404(db, current_user.id, child_id)
    result = clip_escola_service.find_agenda_for_date(db, account, payload.date)
    db.commit()
    return result


@router.delete("/{child_id}")
def disconnect(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id, manage_routine=True)
    account = _get_account_or_404(db, current_user.id, child_id)
    db.delete(account)
    db.commit()
    return {"message": "Conta ClipEscola desconectada."}
