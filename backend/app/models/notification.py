from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Notification(IdMixin, TimestampMixin, Base):
    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("routine_item_id", "scheduled_at", name="uq_notification_routine_scheduled"),)

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    routine_item_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("routine_items.id"), index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    target_audience: Mapped[str] = mapped_column(String(32), nullable=False, default="child")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    child = relationship("Child", back_populates="notifications")

