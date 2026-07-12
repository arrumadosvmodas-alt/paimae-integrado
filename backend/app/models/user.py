from uuid import UUID

from sqlalchemy import ForeignKey, String
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

    school = relationship("School", back_populates="users")
    guardian_links = relationship("ChildGuardian", back_populates="guardian")

