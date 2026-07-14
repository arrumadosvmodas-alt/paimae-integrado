import logging
from datetime import datetime, date as date_type
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.pedagogy import StudyPlan, Interaction, InteractionResponse, DailyStudyPlanItem
from app.models.user import User
from app.schemas.study_plan import InteractionRead, InteractionResponseRead
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_school_access
from app.services.scheduler import manually_dispatch_interaction
from app.services.llm import get_llm_service
from app.core.config import settings
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()
llm_service = get_llm_service(settings.google_gemini_api_key)


class DispatchInteractionRequest(BaseModel):
    interaction_id: UUID


class DispatchInteractionResponse(BaseModel):
    status: str
    message: str
    interaction_id: UUID | None = None


class StudyPlanActivationRequest(BaseModel):
    study_plan_id: UUID
    activate: bool = True


class StudyPlanActivationResponse(BaseModel):
    status: str
    message: str
    study_plan_id: UUID | None = None


class EvaluateResponseRequest(BaseModel):
    response_id: UUID
    auto_evaluate: bool = True


class EvaluateResponseResponse(BaseModel):
    status: str
    message: str
    response_id: UUID | None = None
    ai_evaluation: str | None = None
    score: int | None = None


# --- ATIVAÇÃO DE PLANOS ---

@router.post("/study-plans/{study_plan_id}/activate", response_model=StudyPlanActivationResponse)
def activate_study_plan(
    study_plan_id: UUID,
    activate: bool = True,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Ativa ou desativa um plano de estudos.

    Quando ativado:
    - Status muda para "active"
    - Interações começam a ser agendadas automaticamente
    - Items de estudo são gerados diariamente

    Quando desativado:
    - Status muda para "paused"
    - Nenhuma nova interação é agendada
    """
    study_plan = db.scalar(select(StudyPlan).where(StudyPlan.id == study_plan_id))
    if not study_plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano não encontrado")

    ensure_child_access(db, current_user, study_plan.child_id)

    try:
        if activate:
            study_plan.status = "active"
            message = "Plano de estudos ativado. Interações serão agendadas automaticamente."
            logger.info(f"✅ Plano {study_plan_id} ativado")
        else:
            study_plan.status = "paused"
            message = "Plano de estudos pausado. Nenhuma interação será agendada."
            logger.info(f"⏸️ Plano {study_plan_id} pausado")

        record_audit(
            db,
            actor=current_user,
            action=f"study_plan.{'activate' if activate else 'pause'}",
            entity_type="study_plan",
            entity_id=study_plan.id,
            school_id=study_plan.child.school_id,
        )
        db.commit()

        return StudyPlanActivationResponse(
            status="success",
            message=message,
            study_plan_id=study_plan_id,
        )
    except Exception as e:
        logger.error(f"❌ Erro ao {'' if activate else 'des'}ativar plano: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# --- DISPARO MANUAL DE INTERAÇÕES ---

@router.post("/interactions/{interaction_id}/dispatch", response_model=DispatchInteractionResponse)
def dispatch_interaction_now(
    interaction_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Dispara uma interação imediatamente (sem aguardar agendamento).

    Útil para:
    - Teste de notificações
    - Disparo manual quando necessário urgente
    - Reaenvio se falhar na primeira vez
    """
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    result = manually_dispatch_interaction(db, interaction_id)

    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])

    record_audit(
        db,
        actor=current_user,
        action="interaction.dispatch_manual",
        entity_type="interaction",
        entity_id=interaction.id,
        school_id=interaction.child.school_id,
    )

    return DispatchInteractionResponse(
        status=result["status"],
        message=result["message"],
        interaction_id=interaction_id,
    )


# --- AVALIAÇÃO DE RESPOSTAS COM IA ---

@router.post("/interactions/{interaction_id}/responses/{response_id}/evaluate", response_model=EvaluateResponseResponse)
def evaluate_response_with_ai(
    interaction_id: UUID,
    response_id: UUID,
    auto_evaluate: bool = True,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Avalia uma resposta de criança/pai usando IA (Gemini).

    Quando auto_evaluate=True:
    - Gemini analisa a resposta
    - Gera score (1-5)
    - Fornece feedback personalizado
    - Atualiza próximas interações baseado na resposta
    """
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    response = db.scalar(
        select(InteractionResponse).where(
            InteractionResponse.id == response_id,
            InteractionResponse.interaction_id == interaction_id,
        )
    )
    if not response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resposta não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    if not auto_evaluate:
        return EvaluateResponseResponse(
            status="success",
            message="Avaliação automática desativada",
            response_id=response_id,
        )

    try:
        # Gerar avaliação com Gemini
        prompt = f"""
Avalie a seguinte resposta de uma criança em uma atividade de aprendizagem:

**Contexto:**
- Tema: {interaction.context_json.get('theme', 'Desconhecido') if interaction.context_json else 'Desconhecido'}
- Interação Original: {interaction.message[:200]}

**Resposta da Criança:**
{response.response_text}

Por favor, forneça:
1. Score de 1-5 (1=precisa melhorar, 5=excelente)
2. Feedback positivo
3. Áreas para melhoria
4. Sugestão de próxima atividade

Retorne em formato JSON simples.
"""

        evaluation_response = llm_service.model.generate_content(prompt)
        evaluation_text = evaluation_response.text

        # Extrair score (simplificado - em produção seria parsing JSON)
        score = 3
        if "5" in evaluation_text[:50]:
            score = 5
        elif "4" in evaluation_text[:50]:
            score = 4
        elif "2" in evaluation_text[:50]:
            score = 2
        elif "1" in evaluation_text[:50]:
            score = 1

        response.ai_evaluation = evaluation_text
        response.response_score = score

        record_audit(
            db,
            actor=current_user,
            action="interaction_response.evaluate_ai",
            entity_type="interaction_response",
            entity_id=response.id,
            school_id=interaction.child.school_id,
        )
        db.commit()

        logger.info(f"✅ Resposta {response_id} avaliada com score {score}")

        return EvaluateResponseResponse(
            status="success",
            message=f"Resposta avaliada com sucesso (score: {score}/5)",
            response_id=response_id,
            ai_evaluation=evaluation_text[:200],
            score=score,
        )

    except Exception as e:
        logger.error(f"❌ Erro ao avaliar resposta: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# --- LISTAR INTERAÇÕES PENDENTES ---

@router.get("/interactions/pending", response_model=list[InteractionRead])
def list_pending_interactions(
    child_id: UUID | None = None,
    limit: int = Query(10, ge=1, le=100),
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Lista interações pendentes (não enviadas) para uma criança ou todas as crianças acessíveis.
    """
    query = select(Interaction).where(Interaction.status == "scheduled").order_by(Interaction.scheduled_at)

    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(Interaction.child_id == child_id)
    elif current_user.role != "admin":
        if current_user.school_id:
            query = query.join(Child).where(Child.school_id == current_user.school_id)

    interactions = db.scalars(query.limit(limit)).all()
    return interactions


# --- LISTAR RESPOSTAS NÃO AVALIADAS ---

@router.get("/interactions/{interaction_id}/responses/unevaluated", response_model=list[InteractionResponseRead])
def list_unevaluated_responses(
    interaction_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Lista respostas que ainda não foram avaliadas pela IA.
    """
    interaction = db.scalar(select(Interaction).where(Interaction.id == interaction_id))
    if not interaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    ensure_child_access(db, current_user, interaction.child_id)

    responses = db.scalars(
        select(InteractionResponse)
        .where(
            InteractionResponse.interaction_id == interaction_id,
            InteractionResponse.ai_evaluation.is_(None),
        )
        .order_by(InteractionResponse.responded_at.desc())
    ).all()

    return responses


# --- STATUS DO SCHEDULER ---

@router.get("/scheduler/status")
def get_scheduler_status(
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Retorna status do scheduler de background.
    Apenas admins/coordenadores podem acessar.
    """
    if current_user.role not in ("admin", "school_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    from app.services.scheduler import scheduler

    if scheduler is None:
        return {
            "status": "stopped",
            "message": "Scheduler não foi iniciado",
            "jobs": [],
        }

    try:
        jobs_info = []
        for job in scheduler.get_jobs():
            jobs_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": str(job.next_run_time),
                "trigger": str(job.trigger),
            })

        return {
            "status": "running",
            "message": "Scheduler ativo e processando interações",
            "jobs_count": len(jobs_info),
            "jobs": jobs_info,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "jobs": [],
        }
