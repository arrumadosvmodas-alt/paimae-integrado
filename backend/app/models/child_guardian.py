from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class ChildGuardian(IdMixin, TimestampMixin, Base):
    __tablename__ = "child_guardians"
    __table_args__ = (UniqueConstraint("child_id", "guardian_id", name="uq_child_guardian"),)

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    guardian_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    relationship_type: Mapped[str] = mapped_column(String(40), nullable=False)
    can_view: Mapped[bool] = mapped_column(default=True)
    can_manage_routine: Mapped[bool] = mapped_column(default=False)
    can_mark_notifications: Mapped[bool] = mapped_column(default=True)

    child = relationship("Child", back_populates="guardians")
    guardian = relationship("User", back_populates="guardian_links")

