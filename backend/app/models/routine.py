from datetime import time
from uuid import UUID

from sqlalchemy import ForeignKey, String, Time, JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class RoutineItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "routine_items"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    scheduled_time: Mapped[time] = mapped_column(Time, nullable=False)
    weekdays: Mapped[list[int]] = mapped_column(JSON, nullable=False)
    target_audience: Mapped[str] = mapped_column(String(32), nullable=False, default="child")
    is_active: Mapped[bool] = mapped_column(default=True)

    child = relationship("Child", back_populates="routine_items")

