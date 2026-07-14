"""Schemas para gamificação."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class BadgeResponse(BaseModel):
    """Response de badge."""

    id: UUID
    child_id: UUID
    badge_type: str
    title: str
    description: str
    icon_emoji: str
    points_awarded: int
    unlocked_at: datetime
    rarity: str

    class Config:
        from_attributes = True


class MissionBase(BaseModel):
    """Base para missão."""

    title: str
    description: str
    reward_points: int
    required_activity_count: int = 1
    required_score: float = 0.0
    required_theme: Optional[str] = None
    time_limit_days: Optional[int] = None
    difficulty: str = "normal"


class MissionCreate(MissionBase):
    """Criar missão."""

    pass


class MissionResponse(MissionBase):
    """Response de missão."""

    id: UUID
    school_id: UUID
    is_active: bool
    reward_badge: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LeaderboardResponse(BaseModel):
    """Response de leaderboard."""

    position: int
    child_id: UUID
    total_points: int
    week_points: int
    month_points: int
    badge_count: int
    current_streak: int
    overall_rank: Optional[int] = None
    week_rank: Optional[int] = None
    month_rank: Optional[int] = None


class DailyChallengeResponse(BaseModel):
    """Response de desafio diário."""

    id: UUID
    title: str
    description: str
    challenge_type: str
    required_theme: Optional[str] = None
    required_count: int = 1
    required_score: float = 0.0
    bonus_points: int
    reward_badge: Optional[str] = None
    is_active: bool
    date: datetime

    class Config:
        from_attributes = True


class RewardBase(BaseModel):
    """Base para recompensa."""

    title: str
    description: str
    icon: str
    cost_points: int
    reward_type: str


class RewardCreate(RewardBase):
    """Criar recompensa."""

    reward_data: Optional[Dict[str, Any]] = None
    available_count: Optional[int] = None


class RewardResponse(RewardBase):
    """Response de recompensa."""

    id: UUID
    school_id: UUID
    is_active: bool
    available_count: Optional[int] = None
    reward_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RewardClaimResponse(BaseModel):
    """Response de recompensa reivindicada."""

    id: UUID
    child_id: UUID
    reward_id: UUID
    points_spent: int
    claimed_at: datetime
    delivered: bool
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GamificationStatsResponse(BaseModel):
    """Response de estatísticas de gamificação."""

    total_points: int
    week_points: int
    month_points: int
    badge_count: int
    current_streak: int
    longest_streak: int
    overall_rank: Optional[int] = None
    week_rank: Optional[int] = None
    month_rank: Optional[int] = None
