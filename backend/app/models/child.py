from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Child(IdMixin, TimestampMixin, Base):
    __tablename__ = "children"

    full_name: Mapped[str] = mapped_column(String(180), nullable=False)
    birth_date: Mapped[date | None] = mapped_column(Date)
    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    class_name: Mapped[str | None] = mapped_column(String(80))
    grade: Mapped[str | None] = mapped_column(String(20))
    shift: Mapped[str | None] = mapped_column(String(20))
    preferences: Mapped[dict | None] = mapped_column(JSON)
    difficulties: Mapped[dict | None] = mapped_column(JSON)
    observations: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(default=True)

    school = relationship("School", back_populates="children")
    guardians = relationship("ChildGuardian", back_populates="child", cascade="all, delete-orphan")
    routine_items = relationship("RoutineItem", back_populates="child")
    notifications = relationship("Notification", back_populates="child")
    tasks = relationship("Task", back_populates="child")
    evolution_events = relationship("EvolutionEvent", back_populates="child")
    study_plans = relationship("StudyPlan", back_populates="child", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="child", cascade="all, delete-orphan")

