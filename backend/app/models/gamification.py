"""Modelos para gamificação."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class BadgeType:
    """Tipos de badges (valores usados na coluna badge_type)."""
    FIRST_ACTIVITY = "first_activity"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    PERFECT_SCORE = "perfect_score"
    HELPFUL = "helpful"
    QUICK_LEARNER = "quick_learner"
    MASTER = "master"
    CHAMPION = "champion"


class Badge(IdMixin, TimestampMixin, Base):
    """Badges conquistados por alunos."""
    __tablename__ = "badges"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    badge_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    icon_emoji: Mapped[str] = mapped_column(String(10), nullable=False)

    # Critério de desbloqueio
    unlock_criteria: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    rarity: Mapped[str] = mapped_column(String(20), default="common")  # common, rare, epic, legendary

    # Relacionamentos
    child = relationship("Child", back_populates="badges")


class Mission(IdMixin, TimestampMixin, Base):
    """Missões (desafios específicos)."""
    __tablename__ = "missions"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    reward_points: Mapped[int] = mapped_column(Integer, default=0)
    reward_badge: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Condições
    required_activity_count: Mapped[int] = mapped_column(Integer, default=1)
    required_score: Mapped[float] = mapped_column(Float, default=0.0)
    required_theme: Mapped[str | None] = mapped_column(String(100), nullable=True)
    time_limit_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    difficulty: Mapped[str] = mapped_column(String(20), default="normal")  # easy, normal, hard, expert

    # Relacionamentos
    school = relationship("School", back_populates="missions")
    completions = relationship("MissionCompletion", back_populates="mission", cascade="all, delete-orphan")


class MissionCompletion(IdMixin, TimestampMixin, Base):
    """Conclusão de missões."""
    __tablename__ = "mission_completions"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    mission_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)

    # Status
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100%
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Recompensas
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    badge_earned: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relacionamentos
    child = relationship("Child", back_populates="mission_completions")
    mission = relationship("Mission", back_populates="completions")


class Leaderboard(IdMixin, TimestampMixin, Base):
    """Ranking de alunos."""
    __tablename__ = "leaderboards"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, unique=True, index=True)

    # Pontuação
    total_points: Mapped[int] = mapped_column(Integer, default=0)
    week_points: Mapped[int] = mapped_column(Integer, default=0)
    month_points: Mapped[int] = mapped_column(Integer, default=0)

    # Posições
    overall_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    week_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    month_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Streaks
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_activity: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Badges
    badge_count: Mapped[int] = mapped_column(Integer, default=0)
    epic_badge_count: Mapped[int] = mapped_column(Integer, default=0)
    legendary_badge_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relacionamentos
    school = relationship("School", back_populates="leaderboards")
    child = relationship("Child", back_populates="leaderboard")


class Achievement(IdMixin, TimestampMixin, Base):
    """Achievements (marcos alcançados)."""
    __tablename__ = "achievements"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # milestone, challenge, discovery

    # Critério
    criteria: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Recompensa
    points_awarded: Mapped[int] = mapped_column(Integer, default=0)
    badge_icon: Mapped[str] = mapped_column(String(10), nullable=False)

    # Timestamp
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_secret: Mapped[bool] = mapped_column(Boolean, default=False)  # Surprise achievements

    # Relacionamentos
    child = relationship("Child", back_populates="achievements")


class DailyChallenge(IdMixin, TimestampMixin, Base):
    """Desafios diários."""
    __tablename__ = "daily_challenges"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Challenge details
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    challenge_type: Mapped[str] = mapped_column(String(50), nullable=False)  # activity, quiz, interaction

    # Criteria
    required_theme: Mapped[str | None] = mapped_column(String(100), nullable=True)
    required_count: Mapped[int] = mapped_column(Integer, default=1)
    required_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Reward
    bonus_points: Mapped[int] = mapped_column(Integer, default=10)
    reward_badge: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relacionamentos
    school = relationship("School", back_populates="daily_challenges")
    completions = relationship("DailyChallengeCompletion", back_populates="challenge", cascade="all, delete-orphan")


class DailyChallengeCompletion(IdMixin, TimestampMixin, Base):
    """Conclusão de desafios diários."""
    __tablename__ = "daily_challenge_completions"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    challenge_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("daily_challenges.id"), nullable=False, index=True)

    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    points_earned: Mapped[int] = mapped_column(Integer, default=0)
    badge_earned: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relacionamentos
    child = relationship("Child", back_populates="daily_challenge_completions")
    challenge = relationship("DailyChallenge", back_populates="completions")


class Reward(IdMixin, TimestampMixin, Base):
    """Recompensas desbloqueáveis."""
    __tablename__ = "rewards"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    icon: Mapped[str] = mapped_column(String(10), nullable=False)

    # Custo em pontos
    cost_points: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tipo de recompensa
    reward_type: Mapped[str] = mapped_column(String(50), nullable=False)  # certificate, badge, privilege, discount

    # Recompensa específica
    reward_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    available_count: Mapped[int | None] = mapped_column(Integer, nullable=True)  # None = ilimitado

    # Relacionamentos
    school = relationship("School", back_populates="rewards")
    claims = relationship("RewardClaim", back_populates="reward", cascade="all, delete-orphan")


class RewardClaim(IdMixin, TimestampMixin, Base):
    """Recompensas reclamadas por alunos."""
    __tablename__ = "reward_claims"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    reward_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("rewards.id"), nullable=False, index=True)

    points_spent: Mapped[int] = mapped_column(Integer, nullable=False)
    claimed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relacionamentos
    child = relationship("Child", back_populates="reward_claims")
    reward = relationship("Reward", back_populates="claims")
