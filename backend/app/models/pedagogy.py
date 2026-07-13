from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text, Integer, Boolean
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
    subject: Mapped[str] = mapped_column(String(80), nullable=False)  # ex: Matemática, Português
    pedagogical_line: Mapped[str] = mapped_column(String(100), nullable=False)  # ex: Construtivista, Montessori
    objectives: Mapped[str | None] = mapped_column(Text)
    family_orientation: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    school = relationship("School")
    items = relationship("MaterialItem", back_populates="material", cascade="all, delete-orphan")


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
