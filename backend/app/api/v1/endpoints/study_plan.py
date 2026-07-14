from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.pedagogy import StudyPlan, DailyStudyPlanItem, Interaction, InteractionResponse
from app.models.user import User
from app.schemas.common import ActiveStatusUpdate
from app.schemas.study_plan import (
    StudyPlanCreate,
    StudyPlanRead,
    StudyPlanUpdate,
    DailyStudyPlanItemCreate,
    DailyStudyPlanItemRead,
    DailyStudyPlanItemUpdate,
    InteractionCreate,
    InteractionRead,
    InteractionUpdate,
    InteractionResponseCreate,
    InteractionResponseRead,
    InteractionResponseUpdate,
)
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_school_access

router = APIRouter()


# --- ESTUDO PLANO ---

@router.post("", response_model=StudyPlanRead, status_code=status.HTTP_201_CREATED)
def create_study_plan(
    payload: StudyPlanCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = ensure_child_access(db, current_user, payload.child_id)
    ensure_school_access(current_user, child.school_id)

    study_plan = StudyPlan(
        child_id=payload.child_id,
        material_id=payload.material_id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        ai_generated_plan=payload.ai_generated_plan,
    )
    db.add(study_plan)
    db.flush()

    if payload.daily_items:
        for item_data in payload.daily_items:
            daily_item = DailyStudyPlanItem(
                study_plan_id=study_plan.id,
                **item_data.model_dump(),
            )
            db.add(daily_item)

    record_audit(
        db,
        actor=current_user,
        action="study_plan.create",
        entity_type="study_plan",
        entity_id=study_plan.id,
        school_id=child.school_id,
    )
    db.commit()
    db.refresh(study_plan)
    return study_plan


@router.get("", response_model=list[StudyPlanRead])
def list_study_plans(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    child_id: UUID | None = None,
):
    query = select(StudyPlan).order_by(StudyPlan.created_at.desc())

    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(StudyPlan.child_id == child_id)
    elif current_user.role != "admin":
        if current_user.school_id:
            query = query.join(Child).where(Child.school_id == current_user.school_id)
        else:
            query = query.where(StudyPlan.child_id.in_(
                select(Child.id).join(Child.school)
            ))

    return list(db.scalars(query))


@router.get("/{study_plan_id}", response_model=StudyPlanRead)
def get_study_plan(
    study_plan_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    study_plan = db.scalar(select(StudyPlan).where(StudyPlan.id == study_plan_id))
    if not study_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano de estudos não encontrado")

    ensure_child_access(db, current_user, study_plan.child_id)
    return study_plan


@router.put("/{study_plan_id}", response_model=StudyPlanRead)
def update_study_plan(
    study_plan_id: UUID,
    payload: StudyPlanUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    study_plan = db.scalar(select(StudyPlan).where(StudyPlan.id == study_plan_id))
    if not study_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano de estudos não encontrado")

    ensure_child_access(db, current_user, study_plan.child_id)

    study_plan.start_date = payload.start_date
    study_plan.end_date = payload.end_date
    study_plan.ai_generated_plan = payload.ai_generated_plan
    study_plan.status = payload.status

    record_audit(
        db,
        actor=current_user,
        action="study_plan.update",
        entity_type="study_plan",
        entity_id=study_plan.id,
        school_id=study_plan.child.school_id,
    )
    db.commit()
    db.refresh(study_plan)
    return study_plan


@router.delete("/{study_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_plan(
    study_plan_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    study_plan = db.scalar(select(StudyPlan).where(StudyPlan.id == study_plan_id))
    if not study_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano de estudos não encontrado")

    ensure_child_access(db, current_user, study_plan.child_id)

    record_audit(
        db,
        actor=current_user,
        action="study_plan.delete",
        entity_type="study_plan",
        entity_id=study_plan.id,
        school_id=study_plan.child.school_id,
    )
    db.delete(study_plan)
    db.commit()


# --- ITEM DE ESTUDO DIÁRIO ---

@router.post("/daily-items", response_model=DailyStudyPlanItemRead, status_code=status.HTTP_201_CREATED)
def create_daily_study_plan_item(
    payload: DailyStudyPlanItemCreate,
    study_plan_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    study_plan = db.scalar(select(StudyPlan).where(StudyPlan.id == study_plan_id))
    if not study_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano de estudos não encontrado")

    ensure_child_access(db, current_user, study_plan.child_id)

    daily_item = DailyStudyPlanItem(
        study_plan_id=study_plan_id,
        **payload.model_dump(),
    )
    db.add(daily_item)
    db.flush()

    record_audit(
        db,
        actor=current_user,
        action="daily_study_item.create",
        entity_type="daily_study_item",
        entity_id=daily_item.id,
        school_id=study_plan.child.school_id,
    )
    db.commit()
    db.refresh(daily_item)
    return daily_item


@router.get("/daily-items/{daily_item_id}", response_model=DailyStudyPlanItemRead)
def get_daily_study_plan_item(
    daily_item_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    daily_item = db.scalar(select(DailyStudyPlanItem).where(DailyStudyPlanItem.id == daily_item_id))
    if not daily_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estudo não encontrado")

    ensure_child_access(db, current_user, daily_item.study_plan.child_id)
    return daily_item


@router.put("/daily-items/{daily_item_id}", response_model=DailyStudyPlanItemRead)
def update_daily_study_plan_item(
    daily_item_id: UUID,
    payload: DailyStudyPlanItemUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    daily_item = db.scalar(select(DailyStudyPlanItem).where(DailyStudyPlanItem.id == daily_item_id))
    if not daily_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de estudo não encontrado")

    ensure_child_access(db, current_user, daily_item.study_plan.child_id)

    for key, value in payload.model_dump().items():
        setattr(daily_item, key, value)

    record_audit(
        db,
        actor=current_user,
        action="daily_study_item.update",
        entity_type="daily_study_item",
        entity_id=daily_item.id,
        school_id=daily_item.study_plan.child.school_id,
    )
    db.commit()
    db.refresh(daily_item)
    return daily_item


# --- INTERAÇÕES ---

@router.post("/interactions", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: InteractionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, payload.child_id)

    interaction = Interaction(
        child_id=payload.child_id,
        material_id=payload.material_id,
        scheduled_at=payload.scheduled_at,
        recipient_type=payload.recipient_type,
        message=payload.message,
        context_json=payload.context_json,
    )
    db.add(interaction)
    db.flush()

    child = db.scalar(select(Child).where(Child.id == payload.child_id))
    record_audit(
        db,
        actor=current_user,
        action="interaction.create",
        entity_type="interaction",
        entity_id=interaction.id,
        school_id=child.school_id,
    )
    db.commit()
    db.refresh(interaction)
    return interaction


@router.get("/interactions", response_model=list[InteractionRead])
def list_interactions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    child_id: UUID | None = None,
):
    query = select(Interaction).order_by(Interaction.scheduled_at.desc())

    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(Interaction.child_id == child_id)
    elif current_user.role != "admin":
        if current_user.school_id:
            query = query.join(Child).where(Child.school_id == current_user.school_id)

    return list(db.scalars(query))


@router.get("/interactions/{interaction_id}", response_model=InteractionRead)
def get_interaction(
    interaction_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)
    return interaction


@router.put("/interactions/{interaction_id}", response_model=InteractionRead)
def update_interaction(
    interaction_id: UUID,
    payload: InteractionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    interaction.scheduled_at = payload.scheduled_at
    interaction.recipient_type = payload.recipient_type
    interaction.message = payload.message
    interaction.context_json = payload.context_json
    interaction.status = payload.status

    record_audit(
        db,
        actor=current_user,
        action="interaction.update",
        entity_type="interaction",
        entity_id=interaction.id,
        school_id=interaction.child.school_id,
    )
    db.commit()
    db.refresh(interaction)
    return interaction


@router.delete("/interactions/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(
    interaction_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    record_audit(
        db,
        actor=current_user,
        action="interaction.delete",
        entity_type="interaction",
        entity_id=interaction.id,
        school_id=interaction.child.school_id,
    )
    db.delete(interaction)
    db.commit()


# --- RESPOSTAS DE INTERAÇÃO ---

@router.post("/interactions/{interaction_id}/responses", response_model=InteractionResponseRead, status_code=status.HTTP_201_CREATED)
def create_interaction_response(
    interaction_id: UUID,
    payload: InteractionResponseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    response = InteractionResponse(
        interaction_id=interaction_id,
        **payload.model_dump(),
    )
    db.add(response)
    db.flush()

    record_audit(
        db,
        actor=current_user,
        action="interaction_response.create",
        entity_type="interaction_response",
        entity_id=response.id,
        school_id=interaction.child.school_id,
    )
    db.commit()
    db.refresh(response)
    return response


@router.get("/interactions/{interaction_id}/responses", response_model=list[InteractionResponseRead])
def list_interaction_responses(
    interaction_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    responses = db.scalars(
        select(InteractionResponse)
        .where(InteractionResponse.interaction_id == interaction_id)
        .order_by(InteractionResponse.responded_at.desc())
    )
    return list(responses)


@router.put("/responses/{response_id}", response_model=InteractionResponseRead)
def update_interaction_response(
    response_id: UUID,
    payload: InteractionResponseUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    response = db.scalar(select(InteractionResponse).where(InteractionResponse.id == response_id))
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta não encontrada")

    ensure_child_access(db, current_user, response.interaction.child_id)

    for key, value in payload.model_dump().items():
        setattr(response, key, value)

    record_audit(
        db,
        actor=current_user,
        action="interaction_response.update",
        entity_type="interaction_response",
        entity_id=response.id,
        school_id=response.interaction.child.school_id,
    )
    db.commit()
    db.refresh(response)
    return response
