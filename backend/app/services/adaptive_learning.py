import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.learning import LearningProfile, LearningHistory, AdaptiveRecommendation
from app.models.pedagogy import Interaction, InteractionResponse
from app.services.llm import get_llm_service
from app.core.config import settings

logger = logging.getLogger(__name__)
llm_service = get_llm_service(settings.google_gemini_api_key)


class AdaptiveLearningService:
    """
    Serviço de aprendizagem adaptativa que:
    1. Rastreia histórico de aprendizagem
    2. Atualiza perfil dinâmico
    3. Gera recomendações inteligentes
    4. Prediz sucesso/risco
    """

    @staticmethod
    def create_or_get_learning_profile(db: Session, child_id: UUID) -> LearningProfile:
        """Cria ou obtém perfil de aprendizagem para criança."""
        profile = db.scalar(select(LearningProfile).where(LearningProfile.child_id == child_id))
        if not profile:
            profile = LearningProfile(child_id=child_id)
            db.add(profile)
            db.flush()
            logger.info(f"✅ Perfil de aprendizagem criado para criança: {child_id}")
        return profile

    @staticmethod
    def record_interaction_attempt(
        db: Session,
        child_id: UUID,
        interaction_id: UUID,
        response_id: UUID,
        theme: str,
        activity_type: str,
        difficulty_presented: str,
        was_successful: bool,
        score: int | None = None,
        time_spent_seconds: int | None = None,
        ai_evaluation: str | None = None,
        effective_styles: list | None = None,
    ) -> LearningHistory:
        """Registra uma tentativa de atividade no histórico."""
        history = LearningHistory(
            child_id=child_id,
            interaction_id=interaction_id,
            response_id=response_id,
            theme=theme,
            activity_type=activity_type,
            difficulty_presented=difficulty_presented,
            was_successful=was_successful,
            score=score,
            time_spent_seconds=time_spent_seconds,
            feedback=ai_evaluation,
            effective_styles=effective_styles or [],
            activity_date=datetime.utcnow(),
        )
        db.add(history)
        db.flush()

        logger.info(f"✅ Tentativa registrada: {child_id} - {theme} - Sucesso: {was_successful}")
        return history

    @staticmethod
    def update_learning_profile(
        db: Session,
        child_id: UUID,
        theme: str | None = None,
        success_rate_update: float | None = None,
        style_effectiveness: dict | None = None,
        engagement_delta: int | None = None,
    ) -> LearningProfile:
        """Atualiza dinamicamente o perfil de aprendizagem baseado em histórico recente."""
        profile = AdaptiveLearningService.create_or_get_learning_profile(db, child_id)

        # Atualizar competências por tema
        if theme and success_rate_update is not None:
            if "competencies" not in profile.competencies or profile.competencies is None:
                profile.competencies = {}

            current_competency = profile.competencies.get(theme, 0.5)
            # Moving average: 70% valor anterior, 30% novo valor
            new_competency = (current_competency * 0.7) + (success_rate_update * 0.3)
            profile.competencies[theme] = round(new_competency, 2)

        # Atualizar preferências de estilo
        if style_effectiveness:
            # Registrar quais estilos foram efetivos
            if style_effectiveness.get("visual"):
                profile.visual_preference = min(1.0, profile.visual_preference + 0.05)
            if style_effectiveness.get("auditory"):
                profile.auditory_preference = min(1.0, profile.auditory_preference + 0.05)
            if style_effectiveness.get("kinesthetic"):
                profile.kinesthetic_preference = min(1.0, profile.kinesthetic_preference + 0.05)

            # Normalizar preferências
            total = profile.visual_preference + profile.auditory_preference + profile.kinesthetic_preference
            if total > 0:
                profile.visual_preference /= total
                profile.auditory_preference /= total
                profile.kinesthetic_preference /= total

        # Atualizar engagement
        if engagement_delta:
            profile.engagement_level = max(1, min(5, profile.engagement_level + engagement_delta))

        profile.last_auto_update = datetime.utcnow()
        db.commit()

        logger.info(f"✅ Perfil atualizado: {child_id}")
        return profile

    @staticmethod
    def calculate_progress_metrics(db: Session, child_id: UUID) -> dict[str, Any]:
        """Calcula métricas de progresso de uma criança."""
        # Histórico dos últimos 30 dias
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_history = db.scalars(
            select(LearningHistory)
            .where(
                LearningHistory.child_id == child_id,
                LearningHistory.activity_date >= thirty_days_ago,
                LearningHistory.is_active.is_(True),
            )
            .order_by(LearningHistory.activity_date.desc())
        ).all()

        total_attempts = len(recent_history)
        successful_attempts = sum(1 for h in recent_history if h.was_successful)
        success_rate = successful_attempts / total_attempts if total_attempts > 0 else 0

        # Agrupar por tema
        themes_stats = {}
        for history in recent_history:
            theme = history.theme
            if theme not in themes_stats:
                themes_stats[theme] = {"total": 0, "success": 0, "scores": []}
            themes_stats[theme]["total"] += 1
            if history.was_successful:
                themes_stats[theme]["success"] += 1
            if history.score:
                themes_stats[theme]["scores"].append(history.score)

        # Calcular tendência por tema
        themes_analysis = {}
        for theme, stats in themes_stats.items():
            theme_success_rate = stats["success"] / stats["total"] if stats["total"] > 0 else 0
            avg_score = sum(stats["scores"]) / len(stats["scores"]) if stats["scores"] else 0

            if theme_success_rate >= 0.8:
                status = "mastered"
            elif theme_success_rate >= 0.5:
                status = "in_progress"
            else:
                status = "struggling"

            themes_analysis[theme] = {
                "success_rate": round(theme_success_rate, 2),
                "avg_score": round(avg_score, 1),
                "attempts": stats["total"],
                "status": status,
            }

        # Trends
        if len(recent_history) >= 5:
            recent_5 = recent_history[:5]
            older_5 = recent_history[5:10] if len(recent_history) >= 10 else recent_history[5:]

            recent_rate = sum(1 for h in recent_5 if h.was_successful) / len(recent_5) if recent_5 else 0
            older_rate = sum(1 for h in older_5 if h.was_successful) / len(older_5) if older_5 else 0.5

            if recent_rate > older_rate + 0.1:
                trend = "improving"
            elif recent_rate < older_rate - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "total_attempts": total_attempts,
            "successful_attempts": successful_attempts,
            "overall_success_rate": round(success_rate, 2),
            "themes": themes_analysis,
            "trend": trend,
            "mastered_themes": [t for t, s in themes_analysis.items() if s["status"] == "mastered"],
            "struggling_themes": [t for t, s in themes_analysis.items() if s["status"] == "struggling"],
        }

    @staticmethod
    def predict_success_rate(
        db: Session,
        child_id: UUID,
        theme: str,
        difficulty: str,
    ) -> tuple[float, str]:
        """
        Prediz taxa de sucesso para próxima atividade.
        Retorna: (predicted_rate: 0-1, confidence: "low"/"medium"/"high")
        """
        profile = AdaptiveLearningService.create_or_get_learning_profile(db, child_id)

        # Base: competência no tema
        base_competency = profile.competencies.get(theme, 0.5)

        # Ajuste por dificuldade
        difficulty_factor = {
            "easy": 1.2,  # Mais fácil, mais chance de sucesso
            "medium": 1.0,
            "hard": 0.8,  # Mais difícil, menos chance
        }.get(difficulty, 1.0)

        # Velocidade de aprendizagem
        learning_speed_factor = profile.learning_speed

        # Confiança (mais confiança = mais chance)
        confidence_factor = (profile.confidence_level / 5.0) * 0.2  # 0-20% boost

        # Calcular
        predicted_rate = min(0.95, max(0.05, base_competency * difficulty_factor * learning_speed_factor + confidence_factor))

        # Confidência na predição (baseada em data points)
        history_count = db.scalar(
            func.count(LearningHistory.id)
            .select_from(LearningHistory)
            .where(
                LearningHistory.child_id == child_id,
                LearningHistory.theme == theme,
            )
        )

        if history_count is None or history_count == 0:
            confidence = "low"
        elif history_count < 5:
            confidence = "medium"
        else:
            confidence = "high"

        return (round(predicted_rate, 2), confidence)

    @staticmethod
    def predict_dropout_risk(db: Session, child_id: UUID) -> tuple[float, str]:
        """
        Prediz risco de desistência (dropout).
        Retorna: (risk_score: 0-1, risk_level: "low"/"medium"/"high")
        """
        profile = AdaptiveLearningService.create_or_get_learning_profile(db, child_id)

        # Fatores de risco
        risk_score = 0.0

        # Baixo engajamento
        if profile.engagement_level <= 2:
            risk_score += 0.4

        # Muitas falhas recentes
        metrics = AdaptiveLearningService.calculate_progress_metrics(db, child_id)
        if metrics["overall_success_rate"] < 0.3:
            risk_score += 0.3

        # Muitos temas em dificuldade
        if len(metrics.get("struggling_themes", [])) > 2:
            risk_score += 0.2

        # Falta de confiança
        if profile.confidence_level <= 2:
            risk_score += 0.2

        risk_score = min(1.0, risk_score)

        if risk_score >= 0.7:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return (round(risk_score, 2), risk_level)

    @staticmethod
    def generate_adaptive_recommendation(
        db: Session,
        child_id: UUID,
        available_themes: list[str],
    ) -> AdaptiveRecommendation | None:
        """Gera recomendação adaptativa baseada no perfil."""
        profile = AdaptiveLearningService.create_or_get_learning_profile(db, child_id)
        metrics = AdaptiveLearningService.calculate_progress_metrics(db, child_id)

        # Escolher tema
        if metrics["struggling_themes"]:
            # Se tem tema em dificuldade, oferecer com dificuldade menor
            theme = metrics["struggling_themes"][0]
            difficulty = "easy"
            reason = "Reforço: criança está tendo dificuldade neste tema"
        elif metrics["mastered_themes"]:
            # Se dominou alguns, oferecer novo tema
            available_new = [t for t in available_themes if t not in metrics["mastered_themes"]]
            theme = available_new[0] if available_new else available_themes[0]
            difficulty = "medium"
            reason = "Próximo passo: novo tema após dominar anterior"
        else:
            # Continuar com tema em progresso ou aleatório
            if metrics["themes"]:
                in_progress = [t for t, s in metrics["themes"].items() if s["status"] == "in_progress"]
                theme = in_progress[0] if in_progress else available_themes[0]
            else:
                theme = available_themes[0]
            difficulty = "medium"
            reason = "Continuação: tema em progresso"

        # Estilo recomendado
        if profile.visual_preference > profile.auditory_preference and profile.visual_preference > profile.kinesthetic_preference:
            recommended_style = "visual"
        elif profile.auditory_preference > profile.kinesthetic_preference:
            recommended_style = "auditory"
        else:
            recommended_style = "kinesthetic"

        # Prognóstico
        predicted_success, _ = AdaptiveLearningService.predict_success_rate(db, child_id, theme, difficulty)
        dropout_risk, _ = AdaptiveLearningService.predict_dropout_risk(db, child_id)

        recommendation = AdaptiveRecommendation(
            child_id=child_id,
            learning_profile_id=profile.id,
            recommended_theme=theme,
            recommended_difficulty=difficulty,
            recommended_style=recommended_style,
            confidence=min(0.95, max(0.3, 0.5 + (len(metrics.get("themes", {})) * 0.1))),
            reason=reason,
            predicted_success_rate=predicted_success,
            risk_of_dropout=dropout_risk,
            status="pending",
        )
        db.add(recommendation)
        db.flush()

        logger.info(f"✅ Recomendação gerada para {child_id}: {theme} ({difficulty})")
        return recommendation

    @staticmethod
    def generate_personalized_feedback(
        db: Session,
        child_id: UUID,
        response_score: int,
        theme: str,
    ) -> str:
        """Gera feedback personalizado com base no histórico."""
        profile = AdaptiveLearningService.create_or_get_learning_profile(db, child_id)
        metrics = AdaptiveLearningService.calculate_progress_metrics(db, child_id)

        theme_stats = metrics["themes"].get(theme, {})
        success_rate = theme_stats.get("success_rate", 0)

        # Criar prompt para LLM
        prompt = f"""
Gere um feedback personalizado e motivador para uma criança sobre sua resposta.

**Contexto:**
- Tema: {theme}
- Score desta atividade: {response_score}/5
- Taxa de sucesso neste tema: {success_rate*100:.0f}%
- Nível de confiança: {profile.confidence_level}/5
- Engajamento geral: {profile.engagement_level}/5

Forneça:
1. Feedback positivo específico
2. Área para melhorar (se houver)
3. Encorajamento personalizado
4. Próximo passo sugerido

Mantenha tom amigável e apropriado para criança de 5-8 anos.
Responda em português brasileiro.
"""

        try:
            response = llm_service.model.generate_content(prompt)
            feedback = response.text
            logger.info(f"✅ Feedback gerado para {child_id}")
            return feedback
        except Exception as e:
            logger.error(f"❌ Erro ao gerar feedback: {str(e)}")
            return f"Parabéns! Você acertou {response_score}/5. Continue estudando! 🌟"


adaptive_learning_service = AdaptiveLearningService()
