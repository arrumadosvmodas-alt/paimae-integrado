import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.learning import LearningProfile, LearningHistory, AdaptiveRecommendation
from app.models.pedagogy import Interaction, InteractionResponse
from app.models.user import User
from app.schemas.learning import (
    LearningProfileRead,
    LearningProfileUpdate,
    LearningHistoryCreate,
    LearningHistoryRead,
    LearningMetrics,
    AdaptiveRecommendationRead,
    ProgressAnalysis,
    AdaptationReport,
)
from app.services.adaptive_learning import adaptive_learning_service
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_school_access

logger = logging.getLogger(__name__)
router = APIRouter()


# --- PERFIL DE APRENDIZAGEM ---

@router.get("/children/{child_id}/learning-profile", response_model=LearningProfileRead)
def get_learning_profile(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Obtém perfil de aprendizagem de uma criança."""
    ensure_child_access(db, current_user, child_id)

    profile = adaptive_learning_service.create_or_get_learning_profile(db, child_id)
    return profile


@router.put("/children/{child_id}/learning-profile", response_model=LearningProfileRead)
def update_learning_profile(
    child_id: UUID,
    payload: LearningProfileUpdate,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Atualiza perfil de aprendizagem (uso manual/admin)."""
    child = ensure_child_access(db, current_user, child_id)

    profile = adaptive_learning_service.create_or_get_learning_profile(db, child_id)

    # Atualizar campos permitidos
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    record_audit(
        db,
        actor=current_user,
        action="learning_profile.update",
        entity_type="learning_profile",
        entity_id=profile.id,
        school_id=child.school_id,
    )
    db.commit()
    db.refresh(profile)

    return profile


# --- HISTÓRICO DE APRENDIZAGEM ---

@router.post("/children/{child_id}/learning-history", response_model=LearningHistoryRead, status_code=status.HTTP_201_CREATED)
def record_learning_attempt(
    child_id: UUID,
    payload: LearningHistoryCreate,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Registra uma tentativa de atividade no histórico."""
    child = ensure_child_access(db, current_user, child_id)

    history = adaptive_learning_service.record_interaction_attempt(
        db=db,
        child_id=child_id,
        interaction_id=None,
        response_id=None,
        theme=payload.theme,
        activity_type=payload.activity_type,
        difficulty_presented=payload.difficulty_presented,
        was_successful=payload.was_successful,
        score=payload.score,
        time_spent_seconds=payload.time_spent_seconds,
        ai_evaluation=payload.feedback,
        effective_styles=payload.effective_styles,
    )

    # Atualizar perfil dinamicamente
    adaptive_learning_service.update_learning_profile(
        db=db,
        child_id=child_id,
        theme=payload.theme,
        success_rate_update=1.0 if payload.was_successful else 0.0,
        engagement_delta=1 if payload.was_successful else -1,
    )

    record_audit(
        db,
        actor=current_user,
        action="learning_history.create",
        entity_type="learning_history",
        entity_id=history.id,
        school_id=child.school_id,
    )

    return history


@router.get("/children/{child_id}/learning-history", response_model=list[LearningHistoryRead])
def list_learning_history(
    child_id: UUID,
    limit: int = 50,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Lista histórico de aprendizagem."""
    ensure_child_access(db, current_user, child_id)

    histories = db.scalars(
        select(LearningHistory)
        .where(LearningHistory.child_id == child_id, LearningHistory.is_active.is_(True))
        .order_by(LearningHistory.activity_date.desc())
        .limit(limit)
    ).all()

    return histories


# --- MÉTRICAS DE PROGRESSO ---

@router.get("/children/{child_id}/metrics", response_model=LearningMetrics)
def get_learning_metrics(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Obtém métricas completas de aprendizagem."""
    child = ensure_child_access(db, current_user, child_id)

    profile = adaptive_learning_service.create_or_get_learning_profile(db, child_id)
    metrics = adaptive_learning_service.calculate_progress_metrics(db, child_id)
    dropout_risk, risk_level = adaptive_learning_service.predict_dropout_risk(db, child_id)

    recommendations = []
    if metrics["struggling_themes"]:
        recommendations.append(f"Reforçar: {', '.join(metrics['struggling_themes'][:2])}")
    if dropout_risk > 0.6:
        recommendations.append("Ofereça mais atividades fáceis para recuperar confiança")
    if profile.engagement_level < 3:
        recommendations.append("Aumentar gamificação e feedback positivo")

    if metrics["overall_success_rate"] > 0.8:
        next_success, _ = adaptive_learning_service.predict_success_rate(db, child_id, metrics["mastered_themes"][0] if metrics["mastered_themes"] else "novo_tema", "hard")
        recommendations.append(f"Pronto para desafios: sucesso previsto {next_success*100:.0f}%")

    return LearningMetrics(
        child_id=child_id,
        profile=profile,
        total_activities=metrics["total_attempts"],
        successful_activities=metrics["successful_attempts"],
        overall_success_rate=metrics["overall_success_rate"],
        average_engagement=profile.engagement_level,
        themes_mastered=metrics["mastered_themes"],
        themes_in_progress=[t for t, s in metrics["themes"].items() if s["status"] == "in_progress"],
        themes_struggling=metrics["struggling_themes"],
        predicted_next_success_rate=adaptive_learning_service.predict_success_rate(db, child_id, metrics["mastered_themes"][0] if metrics["mastered_themes"] else "novo", "medium")[0],
        dropout_risk=risk_level,
        recommendations=recommendations,
    )


# --- RECOMENDAÇÕES ADAPTATIVAS ---

@router.post("/children/{child_id}/adaptive-recommendation", response_model=AdaptiveRecommendationRead, status_code=status.HTTP_201_CREATED)
def generate_recommendation(
    child_id: UUID,
    available_themes: list[str] = None,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Gera recomendação adaptativa para próxima atividade."""
    child = ensure_child_access(db, current_user, child_id)

    if not available_themes:
        available_themes = ["Português", "Matemática", "Ciências", "Artes", "Educação Física"]

    recommendation = adaptive_learning_service.generate_adaptive_recommendation(
        db=db,
        child_id=child_id,
        available_themes=available_themes,
    )

    if not recommendation:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao gerar recomendação")

    record_audit(
        db,
        actor=current_user,
        action="adaptive_recommendation.create",
        entity_type="adaptive_recommendation",
        entity_id=recommendation.id,
        school_id=child.school_id,
    )

    return recommendation


@router.get("/children/{child_id}/adaptive-recommendations", response_model=list[AdaptiveRecommendationRead])
def list_recommendations(
    child_id: UUID,
    status: str = "pending",
    limit: int = 10,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Lista recomendações geradas."""
    ensure_child_access(db, current_user, child_id)

    recommendations = db.scalars(
        select(AdaptiveRecommendation)
        .where(
            AdaptiveRecommendation.child_id == child_id,
            AdaptiveRecommendation.status == status,
            AdaptiveRecommendation.is_active.is_(True),
        )
        .order_by(AdaptiveRecommendation.created_at.desc())
        .limit(limit)
    ).all()

    return recommendations


# --- PROGNÓSTICO ---

@router.get("/children/{child_id}/success-prediction")
def predict_success(
    child_id: UUID,
    theme: str,
    difficulty: str = "medium",
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Prediz taxa de sucesso para próxima atividade."""
    ensure_child_access(db, current_user, child_id)

    if difficulty not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dificuldade inválida")

    success_rate, confidence = adaptive_learning_service.predict_success_rate(
        db=db,
        child_id=child_id,
        theme=theme,
        difficulty=difficulty,
    )

    return {
        "child_id": str(child_id),
        "theme": theme,
        "difficulty": difficulty,
        "predicted_success_rate": success_rate,
        "confidence": confidence,
        "recommendation": "Atividade recomendada" if success_rate > 0.6 else "Considere reduzir dificuldade",
    }


@router.get("/children/{child_id}/dropout-risk")
def predict_dropout(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Prediz risco de desistência."""
    ensure_child_access(db, current_user, child_id)

    risk_score, risk_level = adaptive_learning_service.predict_dropout_risk(db=db, child_id=child_id)

    interventions = {
        "high": [
            "Ofereça atividades muito fáceis para recuperar confiança",
            "Aumente feedback positivo e recompensas",
            "Revise material anterior que a criança dominava",
            "Converse com pais sobre apoio em casa",
        ],
        "medium": [
            "Intercale atividades fáceis e médias",
            "Ofereça mais pausas e variação",
            "Reconheça pequenos progressos",
        ],
        "low": [
            "Mantenha o ritmo atual",
            "Gradualmente aumente dificuldade",
            "Explore novos temas",
        ],
    }

    return {
        "child_id": str(child_id),
        "dropout_risk_score": risk_score,
        "risk_level": risk_level,
        "interventions": interventions.get(risk_level, []),
    }


# --- FEEDBACK PERSONALIZADO ---

@router.get("/children/{child_id}/personalized-feedback")
def get_personalized_feedback(
    child_id: UUID,
    response_score: int,
    theme: str,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """Gera feedback personalizado baseado no histórico."""
    ensure_child_access(db, current_user, child_id)

    if response_score < 1 or response_score > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Score deve estar entre 1 e 5")

    feedback = adaptive_learning_service.generate_personalized_feedback(
        db=db,
        child_id=child_id,
        response_score=response_score,
        theme=theme,
    )

    return {
        "child_id": str(child_id),
        "theme": theme,
        "score": response_score,
        "feedback": feedback,
    }
