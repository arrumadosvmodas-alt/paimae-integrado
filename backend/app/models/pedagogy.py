from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text, Integer, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class PedagogicalMethodology(IdMixin, TimestampMixin, Base):
    __tablename__ = "pedagogical_methodologies"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    school = relationship("School")


class PedagogicalMaterial(IdMixin, TimestampMixin, Base):
    __tablename__ = "pedagogical_materials"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    author: Mapped[str | None] = mapped_column(String(100))
    isbn: Mapped[str | None] = mapped_column(String(20), index=True)
    subject: Mapped[str] = mapped_column(String(80), nullable=False)
    pedagogical_line: Mapped[str] = mapped_column(String(100), nullable=False)
    objectives: Mapped[str | None] = mapped_column(Text)
    family_orientation: Mapped[str | None] = mapped_column(Text)
    file_url: Mapped[str | None] = mapped_column(String(500))
    extracted_text: Mapped[str | None] = mapped_column(Text)
    ai_analysis: Mapped[dict | None] = mapped_column(JSON)
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    processing_error: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    school = relationship("School")
    items = relationship("MaterialItem", back_populates="material", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="material", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="material", cascade="all, delete-orphan")


class MaterialItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "material_items"

    material_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("pedagogical_materials.id"), nullable=False, index=True)
    chapter: Mapped[str | None] = mapped_column(String(50))
    page: Mapped[str | None] = mapped_column(String(20))
    theme: Mapped[str] = mapped_column(String(180), nullable=False)  # tema, conteúdo ou habilidade
    description: Mapped[str | None] = mapped_column(Text)

    material = relationship("PedagogicalMaterial", back_populates="items")


class DailySchoolRecord(IdMixin, TimestampMixin, Base):
    __tablename__ = "daily_school_records"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)  # resumo do dia
    observed_skills: Mapped[str | None] = mapped_column(Text)  # habilidades observadas no dia
    engagement_score: Mapped[int | None] = mapped_column(Integer)  # nota de engajamento do dia (1 a 5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    child = relationship("Child")
    suggestions = relationship("FamilyInteractionSuggestion", back_populates="daily_record", cascade="all, delete-orphan")


class FamilyInteractionSuggestion(IdMixin, TimestampMixin, Base):
    __tablename__ = "family_interaction_suggestions"

    daily_record_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("daily_school_records.id"), nullable=False, index=True)
    suggestion_text: Mapped[str] = mapped_column(Text, nullable=False)

    daily_record = relationship("DailySchoolRecord", back_populates="suggestions")


class StudyPlan(IdMixin, TimestampMixin, Base):
    __tablename__ = "study_plans"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    material_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("pedagogical_materials.id"), nullable=False, index=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date)
    ai_generated_plan: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    child = relationship("Child", back_populates="study_plans")
    material = relationship("PedagogicalMaterial", back_populates="study_plans")
    daily_items = relationship("DailyStudyPlanItem", back_populates="study_plan", cascade="all, delete-orphan")


class DailyStudyPlanItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "daily_study_plan_items"

    study_plan_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("study_plans.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    chapter_or_theme: Mapped[str] = mapped_column(String(180), nullable=False)
    activity_description: Mapped[str | None] = mapped_column(Text)
    difficulty_level: Mapped[str] = mapped_column(String(20), default="medium")
    estimated_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    study_plan = relationship("StudyPlan", back_populates="daily_items")


class Interaction(IdMixin, TimestampMixin, Base):
    __tablename__ = "interactions"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    material_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("pedagogical_materials.id"))
    scheduled_at: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sent_at: Mapped[date | None] = mapped_column(Date)
    recipient_type: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    context_json: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    child = relationship("Child", back_populates="interactions")
    material = relationship("PedagogicalMaterial", back_populates="interactions")
    responses = relationship("InteractionResponse", back_populates="interaction", cascade="all, delete-orphan")


class InteractionResponse(IdMixin, TimestampMixin, Base):
    __tablename__ = "interaction_responses"

    interaction_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("interactions.id"), nullable=False, index=True)
    responder_type: Mapped[str] = mapped_column(String(20), nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_score: Mapped[int | None] = mapped_column(Integer)
    attachment_url: Mapped[str | None] = mapped_column(String(500))
    responded_at: Mapped[date] = mapped_column(Date, nullable=False)
    ai_evaluation: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    interaction = relationship("Interaction", back_populates="responses")
