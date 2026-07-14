from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class School(IdMixin, TimestampMixin, Base):
    __tablename__ = "schools"

    name: Mapped[str] = mapped_column(String(180), nullable=False)
    document: Mapped[str | None] = mapped_column(String(32), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    children = relationship("Child", back_populates="school")
    users = relationship("User", back_populates="school")
    integrations = relationship("Integration", back_populates="school", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="school", cascade="all, delete-orphan")
    leaderboards = relationship("Leaderboard", back_populates="school", cascade="all, delete-orphan")
    daily_challenges = relationship("DailyChallenge", back_populates="school", cascade="all, delete-orphan")
    rewards = relationship("Reward", back_populates="school", cascade="all, delete-orphan")

