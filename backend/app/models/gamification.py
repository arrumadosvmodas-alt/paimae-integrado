"""Modelos para gamificação."""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Float, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base, BaseModel


class BadgeType(str, enum.Enum):
    """Tipos de badges."""
    FIRST_ACTIVITY = "first_activity"
    STREAK_7 = "streak_7"
    STREAK_30 = "streak_30"
    PERFECT_SCORE = "perfect_score"
    HELPFUL = "helpful"
    QUICK_LEARNER = "quick_learner"
    MASTER = "master"
    CHAMPION = "champion"


class Badge(Base, BaseModel):
    """Badges conquistados por alunos."""
    __tablename__ = "badges"

    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    badge_type = Column(String(50), nullable=False)  # BadgeType
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    icon_emoji = Column(String(10), nullable=False)

    # Critério de desbloqueio
    unlock_criteria = Column(JSON, nullable=True)
    points_awarded = Column(Integer, default=0)

    # Timestamps
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary

    # Relacionamentos
    child = relationship("Child", back_populates="badges")


class Mission(Base, BaseModel):
    """Missões (desafios específicos)."""
    __tablename__ = "missions"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    reward_points = Column(Integer, default=0)
    reward_badge = Column(String(50), nullable=True)

    # Condições
    required_activity_count = Column(Integer, default=1)
    required_score = Column(Float, default=0.0)
    required_theme = Column(String(100), nullable=True)
    time_limit_days = Column(Integer, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    difficulty = Column(String(20), default="normal")  # easy, normal, hard, expert

    # Relacionamentos
    school = relationship("School", back_populates="missions")
    completions = relationship("MissionCompletion", back_populates="mission")


class MissionCompletion(Base, BaseModel):
    """Conclusão de missões."""
    __tablename__ = "mission_completions"

    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    mission_id = Column(String(36), ForeignKey("missions.id"), nullable=False)

    # Status
    progress = Column(Float, default=0.0)  # 0-100%
    completed = Column(Boolean, default=False)

    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Recompensas
    points_earned = Column(Integer, default=0)
    badge_earned = Column(String(50), nullable=True)

    # Relacionamentos
    child = relationship("Child", back_populates="mission_completions")
    mission = relationship("Mission", back_populates="completions")


class Leaderboard(Base, BaseModel):
    """Ranking de alunos."""
    __tablename__ = "leaderboards"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)

    # Pontuação
    total_points = Column(Integer, default=0)
    week_points = Column(Integer, default=0)
    month_points = Column(Integer, default=0)

    # Posições
    overall_rank = Column(Integer, nullable=True)
    week_rank = Column(Integer, nullable=True)
    month_rank = Column(Integer, nullable=True)

    # Streaks
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)

    # Badges
    badge_count = Column(Integer, default=0)
    epic_badge_count = Column(Integer, default=0)
    legendary_badge_count = Column(Integer, default=0)

    # Atualizações
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    school = relationship("School", back_populates="leaderboards")
    child = relationship("Child", back_populates="leaderboard")


class Achievement(Base, BaseModel):
    """Achievements (marcos alcançados)."""
    __tablename__ = "achievements"

    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False)  # milestone, challenge, discovery

    # Critério
    criteria = Column(JSON, nullable=False)

    # Recompensa
    points_awarded = Column(Integer, default=0)
    badge_icon = Column(String(10), nullable=False)

    # Timestamp
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    is_secret = Column(Boolean, default=False)  # Surprise achievements

    # Relacionamentos
    child = relationship("Child", back_populates="achievements")


class DailyChallenge(Base, BaseModel):
    """Desafios diários."""
    __tablename__ = "daily_challenges"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    date = Column(DateTime, nullable=False)

    # Challenge details
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    challenge_type = Column(String(50), nullable=False)  # activity, quiz, interaction

    # Criteria
    required_theme = Column(String(100), nullable=True)
    required_count = Column(Integer, default=1)
    required_score = Column(Float, default=0.0)

    # Reward
    bonus_points = Column(Integer, default=10)
    reward_badge = Column(String(50), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Relacionamentos
    school = relationship("School", back_populates="daily_challenges")
    completions = relationship("DailyChallengeCompletion", back_populates="challenge")


class DailyChallengeCompletion(Base, BaseModel):
    """Conclusão de desafios diários."""
    __tablename__ = "daily_challenge_completions"

    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    challenge_id = Column(String(36), ForeignKey("daily_challenges.id"), nullable=False)

    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    points_earned = Column(Integer, default=0)
    badge_earned = Column(String(50), nullable=True)

    # Relacionamentos
    child = relationship("Child", back_populates="daily_challenge_completions")
    challenge = relationship("DailyChallenge", back_populates="completions")


class Reward(Base, BaseModel):
    """Recompensas desbloqueáveis."""
    __tablename__ = "rewards"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=False)
    icon = Column(String(10), nullable=False)

    # Custo em pontos
    cost_points = Column(Integer, nullable=False)

    # Tipo de recompensa
    reward_type = Column(String(50), nullable=False)  # certificate, badge, privilege, discount

    # Recompensa específica
    reward_data = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    available_count = Column(Integer, nullable=True)  # None = ilimitado

    # Relacionamentos
    school = relationship("School", back_populates="rewards")
    claims = relationship("RewardClaim", back_populates="reward")


class RewardClaim(Base, BaseModel):
    """Recompensas reclamadas por alunos."""
    __tablename__ = "reward_claims"

    child_id = Column(String(36), ForeignKey("children.id"), nullable=False)
    reward_id = Column(String(36), ForeignKey("rewards.id"), nullable=False)

    points_spent = Column(Integer, nullable=False)
    claimed_at = Column(DateTime, default=datetime.utcnow)
    delivered = Column(Boolean, default=False)
    delivered_at = Column(DateTime, nullable=True)

    # Relacionamentos
    child = relationship("Child", back_populates="reward_claims")
    reward = relationship("Reward", back_populates="claims")
