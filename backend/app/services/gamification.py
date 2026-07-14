"""Serviço de gamificação."""
import logging
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.gamification import (
    Badge,
    Mission,
    MissionCompletion,
    Leaderboard,
    Achievement,
    DailyChallenge,
    DailyChallengeCompletion,
    Reward,
    RewardClaim,
    BadgeType,
)
from app.models.learning import LearningHistory

logger = logging.getLogger(__name__)


class GamificationService:
    """Serviço para gerenciar gamificação."""

    def __init__(self, db: Session):
        self.db = db

    def award_points(self, child_id: str, points: int, reason: str = "activity") -> int:
        """Adiciona pontos para um aluno."""
        leaderboard = self.db.query(Leaderboard).filter_by(child_id=child_id).first()

        if not leaderboard:
            leaderboard = Leaderboard(child_id=child_id)
            self.db.add(leaderboard)

        leaderboard.total_points += points
        leaderboard.week_points += points
        leaderboard.month_points += points

        # Verificar streaks
        self._update_streak(child_id, leaderboard)

        self.db.commit()
        logger.info(f"Pontos adicionados para {child_id}: +{points} ({reason})")

        return leaderboard.total_points

    def _update_streak(self, child_id: str, leaderboard: Leaderboard):
        """Atualiza streaks de atividade."""
        now = datetime.utcnow()
        last_activity = leaderboard.last_activity

        if not last_activity:
            leaderboard.current_streak = 1
            leaderboard.last_activity = now
            return

        days_since = (now.date() - last_activity.date()).days

        if days_since == 0:
            # Mesmo dia, streak continua
            pass
        elif days_since == 1:
            # Dia consecutivo, aumentar streak
            leaderboard.current_streak += 1
            if leaderboard.current_streak > leaderboard.longest_streak:
                leaderboard.longest_streak = leaderboard.current_streak

            # Verificar badges de streak
            self._check_streak_badges(child_id, leaderboard.current_streak)
        else:
            # Quebrou a streak
            leaderboard.current_streak = 1

        leaderboard.last_activity = now

    def _check_streak_badges(self, child_id: str, streak: int):
        """Verifica badges baseado em streak."""
        if streak == 7:
            self.unlock_badge(child_id, BadgeType.STREAK_7)
        elif streak == 30:
            self.unlock_badge(child_id, BadgeType.STREAK_30)

    def unlock_badge(
        self, child_id: str, badge_type: BadgeType, silent: bool = False
    ) -> bool:
        """Desbloqueia um badge para um aluno."""
        existing = self.db.query(Badge).filter_by(
            child_id=child_id, badge_type=badge_type
        ).first()

        if existing:
            return False

        badge_data = {
            BadgeType.FIRST_ACTIVITY: {
                "title": "Primeira Atividade",
                "description": "Concluiu a primeira atividade",
                "emoji": "🚀",
                "points": 5,
            },
            BadgeType.STREAK_7: {
                "title": "Semana Consistente",
                "description": "7 dias de atividades seguidas",
                "emoji": "🔥",
                "points": 25,
            },
            BadgeType.STREAK_30: {
                "title": "Mês Perfeito",
                "description": "30 dias de atividades seguidas",
                "emoji": "⭐",
                "points": 100,
            },
            BadgeType.PERFECT_SCORE: {
                "title": "Pontuação Perfeita",
                "description": "100% em uma atividade",
                "emoji": "💯",
                "points": 15,
            },
            BadgeType.HELPFUL: {
                "title": "Prestativo",
                "description": "Ajudou outros alunos",
                "emoji": "🤝",
                "points": 10,
            },
            BadgeType.QUICK_LEARNER: {
                "title": "Aprendiz Rápido",
                "description": "Completou atividade em tempo recorde",
                "emoji": "⚡",
                "points": 20,
            },
            BadgeType.MASTER: {
                "title": "Mestre",
                "description": "Dominou um tema completamente",
                "emoji": "🧙",
                "points": 50,
            },
            BadgeType.CHAMPION: {
                "title": "Campeão",
                "description": "1º lugar no ranking",
                "emoji": "👑",
                "points": 200,
            },
        }

        badge_info = badge_data.get(badge_type, {})

        badge = Badge(
            child_id=child_id,
            badge_type=badge_type,
            title=badge_info.get("title", badge_type),
            description=badge_info.get("description", ""),
            icon_emoji=badge_info.get("emoji", "🏆"),
            points_awarded=badge_info.get("points", 0),
        )

        self.db.add(badge)

        # Atualizar leaderboard
        leaderboard = self.db.query(Leaderboard).filter_by(child_id=child_id).first()
        if leaderboard:
            leaderboard.badge_count += 1

        self.db.commit()

        if not silent:
            logger.info(f"Badge desbloqueado para {child_id}: {badge_type}")

        return True

    def check_mission_progress(
        self, child_id: str, school_id: str, mission_id: str
    ) -> bool:
        """Verifica e atualiza progresso de uma missão."""
        mission = self.db.query(Mission).filter_by(id=mission_id).first()
        if not mission:
            return False

        completion = self.db.query(MissionCompletion).filter_by(
            child_id=child_id, mission_id=mission_id
        ).first()

        if not completion:
            completion = MissionCompletion(child_id=child_id, mission_id=mission_id)
            self.db.add(completion)

        if completion.completed:
            return False

        # Calcular progresso
        query = self.db.query(LearningHistory).filter_by(child_id=child_id)

        if mission.required_theme:
            query = query.filter_by(theme=mission.required_theme)

        if mission.required_score:
            query = query.filter(
                LearningHistory.score >= mission.required_score
            )

        count = query.count()
        completion.progress = min(100, (count / mission.required_activity_count) * 100)

        # Verificar conclusão
        if completion.progress >= 100:
            completion.completed = True
            completion.completed_at = datetime.utcnow()
            completion.points_earned = mission.reward_points

            # Award badge if applicable
            if mission.reward_badge:
                self.unlock_badge(child_id, mission.reward_badge)

            # Award points
            self.award_points(child_id, mission.reward_points, f"mission:{mission_id}")

            logger.info(f"Missão completada: {child_id} - {mission_id}")

        self.db.commit()
        return completion.completed

    def get_leaderboard(self, school_id: str, period: str = "overall", limit: int = 10) -> List[dict]:
        """Obtém leaderboard."""
        query = self.db.query(Leaderboard).filter_by(school_id=school_id)

        if period == "week":
            query = query.order_by(Leaderboard.week_points.desc())
        elif period == "month":
            query = query.order_by(Leaderboard.month_points.desc())
        else:  # overall
            query = query.order_by(Leaderboard.total_points.desc())

        leaderboards = query.limit(limit).all()

        return [
            {
                "position": idx + 1,
                "child_id": lb.child_id,
                "points": getattr(lb, f"{period}_points"),
                "badges": lb.badge_count,
                "streak": lb.current_streak,
            }
            for idx, lb in enumerate(leaderboards)
        ]

    def get_daily_challenges(self, school_id: str) -> List[DailyChallenge]:
        """Obtém desafios diários de hoje."""
        today = datetime.utcnow().date()
        tomorrow = today + timedelta(days=1)

        challenges = self.db.query(DailyChallenge).filter(
            DailyChallenge.school_id == school_id,
            DailyChallenge.date >= today,
            DailyChallenge.date < tomorrow,
            DailyChallenge.is_active == True,
        ).all()

        return challenges

    def claim_reward(self, child_id: str, reward_id: str) -> Optional[RewardClaim]:
        """Reclama uma recompensa."""
        reward = self.db.query(Reward).filter_by(id=reward_id).first()
        if not reward:
            return None

        leaderboard = self.db.query(Leaderboard).filter_by(child_id=child_id).first()
        if not leaderboard or leaderboard.total_points < reward.cost_points:
            return None

        # Verificar disponibilidade
        if reward.available_count:
            claimed = self.db.query(RewardClaim).filter_by(reward_id=reward_id).count()
            if claimed >= reward.available_count:
                return None

        # Reivindicar
        claim = RewardClaim(
            child_id=child_id,
            reward_id=reward_id,
            points_spent=reward.cost_points,
        )

        leaderboard.total_points -= reward.cost_points

        self.db.add(claim)
        self.db.commit()
        self.db.refresh(claim)

        logger.info(f"Recompensa reivindicada: {child_id} - {reward_id}")

        return claim
