from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


# --- ITEM DE PLANO DE ESTUDO DIÁRIO ---
class DailyStudyPlanItemCreate(BaseModel):
    date: date
    chapter_or_theme: str = Field(min_length=2, max_length=180)
    activity_description: str | None = None
    difficulty_level: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    estimated_duration_minutes: int | None = Field(default=None, ge=5, le=240)


class DailyStudyPlanItemRead(Timestamped):
    study_plan_id: UUID
    date: date
    chapter_or_theme: str
    activity_description: str | None
    difficulty_level: str
    estimated_duration_minutes: int | None
    status: str
    is_active: bool


class DailyStudyPlanItemUpdate(BaseModel):
    chapter_or_theme: str = Field(min_length=2, max_length=180)
    activity_description: str | None = None
    difficulty_level: str = Field(default="medium", pattern="^(easy|medium|hard)$")
    estimated_duration_minutes: int | None = Field(default=None, ge=5, le=240)
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|skipped)$")


# --- PLANO DE ESTUDO ---
class StudyPlanCreate(BaseModel):
    child_id: UUID
    material_id: UUID
    start_date: date
    end_date: date | None = None
    ai_generated_plan: str | None = None
    daily_items: list[DailyStudyPlanItemCreate] | None = None


class StudyPlanRead(Timestamped):
    child_id: UUID
    material_id: UUID
    start_date: date
    end_date: date | None
    ai_generated_plan: str | None
    status: str
    daily_items: list[DailyStudyPlanItemRead]
    is_active: bool


class StudyPlanUpdate(BaseModel):
    start_date: date
    end_date: date | None = None
    ai_generated_plan: str | None = None
    status: str = Field(default="draft", pattern="^(draft|active|completed|paused)$")
    daily_items: list[DailyStudyPlanItemCreate] | None = None


# --- RESPOSTA DE INTERAÇÃO ---
class InteractionResponseCreate(BaseModel):
    responder_type: str = Field(pattern="^(child|parent)$")
    response_text: str = Field(min_length=2)
    response_score: int | None = Field(default=None, ge=1, le=5)
    attachment_url: str | None = Field(default=None, max_length=500)
    responded_at: date


class InteractionResponseRead(Timestamped):
    interaction_id: UUID
    responder_type: str
    response_text: str
    response_score: int | None
    attachment_url: str | None
    responded_at: date
    ai_evaluation: str | None
    is_active: bool


class InteractionResponseUpdate(BaseModel):
    response_text: str = Field(min_length=2)
    response_score: int | None = Field(default=None, ge=1, le=5)
    attachment_url: str | None = Field(default=None, max_length=500)


# --- INTERAÇÃO ---
class InteractionCreate(BaseModel):
    child_id: UUID
    material_id: UUID | None = None
    scheduled_at: date
    recipient_type: str = Field(pattern="^(child|parent)$")
    message: str = Field(min_length=2)
    context_json: dict | None = None


class InteractionRead(Timestamped):
    child_id: UUID
    material_id: UUID | None
    scheduled_at: date
    sent_at: date | None
    recipient_type: str
    message: str
    context_json: dict | None
    status: str
    responses: list[InteractionResponseRead]
    is_active: bool


class InteractionUpdate(BaseModel):
    scheduled_at: date
    recipient_type: str = Field(pattern="^(child|parent)$")
    message: str = Field(min_length=2)
    context_json: dict | None = None
    status: str = Field(default="scheduled", pattern="^(scheduled|sent|read|not_sent)$")
