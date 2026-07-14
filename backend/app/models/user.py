from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(180), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    school_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    document: Mapped[str | None] = mapped_column(String(14), nullable=True, unique=True, index=True)
    first_access_completed: Mapped[bool] = mapped_column(default=False)
    lgpd_accepted: Mapped[bool] = mapped_column(default=False)
    lgpd_accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    school = relationship("School", back_populates="users")
    guardian_links = relationship("ChildGuardian", back_populates="guardian")
    guardian_profile = relationship("GuardianProfile", back_populates="guardian", uselist=False, cascade="all, delete-orphan")


class GuardianProfile(IdMixin, TimestampMixin, Base):
    __tablename__ = "guardian_profiles"

    guardian_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    preferred_channel: Mapped[str] = mapped_column(String(20), default="app")
    daily_summary_time: Mapped[str | None] = mapped_column(String(5))
    evening_activity_time: Mapped[str | None] = mapped_column(String(5))
    notification_preferences: Mapped[dict | None] = mapped_column(JSON)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False)

    guardian = relationship("User", back_populates="guardian_profile")

