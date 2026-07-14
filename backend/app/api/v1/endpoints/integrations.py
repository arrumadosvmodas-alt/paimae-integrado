"""Endpoints para gerenciar integrações externas."""
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.integration import (
    Integration,
    IntegrationSyncLog,
    WebhookEvent,
    WebhookSubscription,
)
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)
from app.services.google_classroom import GoogleClassroomService
from app.services.microsoft_teams import MicrosoftTeamsService
from app.services.whatsapp import WhatsAppBusinessService
from app.services.webhook import WebhookService

router = APIRouter(prefix="/integrations", tags=["integrations"])

google_classroom = GoogleClassroomService()
microsoft_teams = MicrosoftTeamsService()
whatsapp = WhatsAppBusinessService()
webhook_service = WebhookService()


@router.get("", response_model=List[IntegrationResponse])
async def list_integrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as integrações da escola."""
    integrations = (
        db.query(Integration)
        .filter_by(school_id=current_user.school_id)
        .all()
    )
    return integrations


@router.post("", response_model=IntegrationResponse)
async def create_integration(
    data: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria uma nova integração."""
    integration = Integration(
        school_id=current_user.school_id,
        provider=data.provider,
        name=data.name,
        credentials=data.credentials,
        config=data.config,
        sync_enabled=data.sync_enabled,
    )
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: UUID,
    data: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Atualiza uma integração."""
    integration = (
        db.query(Integration)
        .filter_by(id=integration_id, school_id=current_user.school_id)
        .first()
    )

    if not integration:
        raise HTTPException(status_code=404, detail="Integração não encontrada")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(integration, field, value)

    db.commit()
    db.refresh(integration)
    return integration


@router.delete("/{integration_id}")
async def delete_integration(
    integration_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Deleta uma integração."""
    integration = (
        db.query(Integration)
        .filter_by(id=integration_id, school_id=current_user.school_id)
        .first()
    )

    if not integration:
        raise HTTPException(status_code=404, detail="Integração não encontrada")

    db.delete(integration)
    db.commit()
    return {"message": "Integração deletada"}


@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sincroniza dados de uma integração."""
    integration = (
        db.query(Integration)
        .filter_by(id=integration_id, school_id=current_user.school_id)
        .first()
    )

    if not integration:
        raise HTTPException(status_code=404, detail="Integração não encontrada")

    # Adicionar tarefa em background
    background_tasks.add_task(_sync_integration_task, integration, db)

    return {"message": "Sincronização iniciada", "integration_id": integration_id}


async def _sync_integration_task(integration: Integration, db: Session):
    """Tarefa de sincronização em background."""
    try:
        sync_log = IntegrationSyncLog(
            integration_id=integration.id,
            status="started",
        )
        db.add(sync_log)
        db.commit()

        # Chamar serviço apropriado
        if integration.provider == "google_classroom":
            result = await google_classroom.sync_classroom_data(
                integration.config.get("course_id"),
                integration.school_id,
            )
        elif integration.provider == "microsoft_teams":
            result = await microsoft_teams.sync_team_data(
                integration.config.get("team_id"),
                integration.config.get("channel_id"),
                integration.school_id,
            )
        else:
            result = {"status": "error", "error": "Provider não implementado"}

        # Atualizar log
        sync_log.status = result.get("status", "error")
        sync_log.records_synced = str(result.get("records_synced", 0))
        sync_log.error_message = result.get("error")
        sync_log.completed_at = datetime.utcnow()
        integration.last_sync = datetime.utcnow()

        db.commit()
    except Exception as e:
        sync_log.status = "error"
        sync_log.error_message = str(e)
        sync_log.completed_at = datetime.utcnow()
        db.commit()


# Webhooks
@router.get("/webhooks/subscriptions", response_model=List[WebhookSubscriptionResponse])
async def list_webhook_subscriptions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista todas as inscrições de webhook."""
    subscriptions = (
        db.query(WebhookSubscription)
        .filter_by(school_id=current_user.school_id)
        .all()
    )
    return subscriptions


@router.post("/webhooks/subscriptions", response_model=WebhookSubscriptionResponse)
async def create_webhook_subscription(
    data: WebhookSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria uma nova inscrição de webhook."""
    subscription = WebhookSubscription(
        school_id=current_user.school_id,
        name=data.name,
        url=data.url,
        secret=data.secret,
        events=data.events,
        filters=data.filters,
        active=True,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.post("/webhooks/subscriptions/{subscription_id}/test")
async def test_webhook(
    subscription_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Testa um webhook."""
    subscription = (
        db.query(WebhookSubscription)
        .filter_by(id=subscription_id, school_id=current_user.school_id)
        .first()
    )

    if not subscription:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    result = await webhook_service.test_webhook(subscription.url, subscription.secret)
    return result


@router.post("/webhooks/events")
async def receive_webhook_event(
    request: Request,
    db: Session = Depends(get_db),
):
    """Recebe eventos de webhook (sem autenticação)."""
    # Verificar assinatura
    signature = request.headers.get("X-Webhook-Signature")
    if not signature:
        raise HTTPException(status_code=401, detail="Assinatura não fornecida")

    body = await request.body()

    # Nota: a assinatura identifica a integração de origem; sem um lookup por
    # integração conhecida, o evento é armazenado sem vínculo para processamento manual.
    event = WebhookEvent(
        integration_id=None,
        event_type=request.headers.get("X-Webhook-Event", "unknown"),
        payload=await request.json(),
        processed=False,
    )
    db.add(event)
    db.commit()

    return {"status": "received", "event_id": event.id}
