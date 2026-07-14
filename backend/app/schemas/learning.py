from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


# --- PERFIL DE APRENDIZAGEM ---
class LearningProfileRead(Timestamped):
    child_id: UUID
    visual_preference: float
    auditory_preference: float
    kinesthetic_preference: float
    learning_speed: float
    confidence_level: int
    retention_rate: float
    competencies: dict
    identified_challenges: dict
    engagement_level: int
    use_adaptive_difficulty: bool
    is_active: bool


class LearningProfileUpdate(BaseModel):
    visual_preference: float | None = None
    auditory_preference: float | None = None
    kinesthetic_preference: float | None = None
    learning_speed: float | None = None
    confidence_level: int | None = None
    retention_rate: float | None = None
    competencies: dict | None = None
    identified_challenges: dict | None = None
    engagement_level: int | None = None
    use_adaptive_difficulty: bool | None = None


# --- HISTÓRICO DE APRENDIZAGEM ---
class LearningHistoryCreate(BaseModel):
    theme: str = Field(min_length=2, max_length=180)
    activity_type: str = Field(pattern="^(pergunta|exercicio|leitura|escrita|discussao|outro)$")
    difficulty_presented: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    was_successful: bool
    score: int | None = Field(default=None, ge=0, le=100)
    time_spent_seconds: int | None = None
    feedback: str | None = None
    effective_styles: list | None = None
    activity_date: datetime


class LearningHistoryRead(Timestamped):
    child_id: UUID
    interaction_id: UUID | None
    response_id: UUID | None
    theme: str
    activity_type: str
    difficulty_presented: str
    was_successful: bool
    score: int | None
    time_spent_seconds: int | None
    feedback: str | None
    effective_styles: list
    activity_date: datetime
    is_active: bool


# --- RECOMENDAÇÃO ADAPTATIVA ---
class AdaptiveRecommendationRead(Timestamped):
    child_id: UUID
    learning_profile_id: UUID
    recommended_theme: str
    recommended_difficulty: str
    recommended_style: str
    confidence: float
    reason: str | None
    predicted_success_rate: float
    risk_of_dropout: float
    status: str
    is_active: bool


# --- ANÁLISE DE PROGRESSO ---
class ProgressAnalysis(BaseModel):
    child_id: UUID
    theme: str
    success_rate: float  # 0-1
    total_attempts: int
    successful_attempts: int
    average_score: float
    average_time_seconds: int | None
    trend: str  # "improving", "stable", "declining"
    recommendation: str


class LearningMetrics(BaseModel):
    child_id: UUID
    profile: LearningProfileRead | None
    total_activities: int
    successful_activities: int
    overall_success_rate: float
    average_engagement: int
    themes_mastered: list[str]
    themes_in_progress: list[str]
    themes_struggling: list[str]
    predicted_next_success_rate: float
    dropout_risk: str  # "low", "medium", "high"
    recommendations: list[str]


class AdaptationReport(BaseModel):
    child_id: UUID
    timestamp: datetime
    changes_made: list[str]  # Mudanças aplicadas ao perfil
    rationale: str  # Por quê as mudanças foram feitas
    impact_expected: str  # Impacto esperado
    next_milestone: str  # Próximo objetivo
