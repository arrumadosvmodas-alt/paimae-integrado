from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Boolean, DateTime
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

