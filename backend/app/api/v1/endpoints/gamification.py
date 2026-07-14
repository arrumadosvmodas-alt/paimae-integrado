"""Endpoints para gamificação."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.gamification import (
    Badge,
    Mission,
    Leaderboard,
    DailyChallenge,
    Reward,
    RewardClaim,
)
from app.schemas.gamification import (
    BadgeResponse,
    MissionResponse,
    LeaderboardResponse,
    DailyChallengeResponse,
    RewardResponse,
    RewardClaimResponse,
)
from app.services.gamification import GamificationService

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/badges", response_model=List[BadgeResponse])
async def get_badges(
    child_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista badges de um aluno."""
    target_child_id = child_id or current_user.id

    badges = db.query(Badge).filter_by(child_id=target_child_id).all()
    return badges


@router.get("/missions", response_model=List[MissionResponse])
async def get_missions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista missões disponíveis."""
    missions = db.query(Mission).filter_by(
        school_id=current_user.school_id,
        is_active=True
    ).all()
    return missions


@router.get("/leaderboard/{period}", response_model=List[LeaderboardResponse])
async def get_leaderboard(
    period: str = "overall",
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém leaderboard (overall/week/month)."""
    if period not in ["overall", "week", "month"]:
        raise HTTPException(status_code=400, detail="Período inválido")

    leaderboards = db.query(Leaderboard).filter_by(school_id=current_user.school_id)

    if period == "week":
        leaderboards = leaderboards.order_by(Leaderboard.week_points.desc())
    elif period == "month":
        leaderboards = leaderboards.order_by(Leaderboard.month_points.desc())
    else:
        leaderboards = leaderboards.order_by(Leaderboard.total_points.desc())

    result = []
    for idx, lb in enumerate(leaderboards.limit(limit).all()):
        result.append({
            "position": idx + 1,
            "child_id": lb.child_id,
            "total_points": lb.total_points,
            "week_points": lb.week_points,
            "month_points": lb.month_points,
            "badge_count": lb.badge_count,
            "current_streak": lb.current_streak,
            "overall_rank": lb.overall_rank,
        })

    return result


@router.get("/daily-challenges", response_model=List[DailyChallengeResponse])
async def get_daily_challenges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém desafios diários de hoje."""
    from datetime import datetime, timedelta

    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    challenges = db.query(DailyChallenge).filter(
        DailyChallenge.school_id == current_user.school_id,
        DailyChallenge.date >= today,
        DailyChallenge.date < tomorrow,
        DailyChallenge.is_active == True,
    ).all()

    return challenges


@router.get("/stats")
async def get_gamification_stats(
    child_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém estatísticas de gamificação."""
    target_child_id = child_id or current_user.id

    leaderboard = db.query(Leaderboard).filter_by(child_id=target_child_id).first()
    badges = db.query(Badge).filter_by(child_id=target_child_id).count()

    if not leaderboard:
        return {
            "total_points": 0,
            "week_points": 0,
            "month_points": 0,
            "badge_count": 0,
            "current_streak": 0,
            "longest_streak": 0,
        }

    return {
        "total_points": leaderboard.total_points,
        "week_points": leaderboard.week_points,
        "month_points": leaderboard.month_points,
        "badge_count": badges,
        "current_streak": leaderboard.current_streak,
        "longest_streak": leaderboard.longest_streak,
        "overall_rank": leaderboard.overall_rank,
        "week_rank": leaderboard.week_rank,
        "month_rank": leaderboard.month_rank,
    }


@router.get("/rewards", response_model=List[RewardResponse])
async def get_rewards(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista recompensas disponíveis."""
    rewards = db.query(Reward).filter_by(
        school_id=current_user.school_id,
        is_active=True
    ).all()
    return rewards


@router.post("/rewards/{reward_id}/claim", response_model=RewardClaimResponse)
async def claim_reward(
    reward_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reclama uma recompensa."""
    gamification = GamificationService(db)
    claim = gamification.claim_reward(current_user.id, reward_id)

    if not claim:
        raise HTTPException(
            status_code=400,
            detail="Não foi possível reivindicar a recompensa. Verifique se tem pontos suficientes."
        )

    return claim


@router.get("/achievements", response_model=List[dict])
async def get_achievements(
    child_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista achievements desbloqueados."""
    target_child_id = child_id or current_user.id

    from app.models.gamification import Achievement

    achievements = db.query(Achievement).filter_by(child_id=target_child_id).all()

    return [
        {
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "badge_icon": a.badge_icon,
            "points": a.points_awarded,
            "unlocked_at": a.unlocked_at.isoformat(),
            "is_secret": a.is_secret,
        }
        for a in achievements
    ]
