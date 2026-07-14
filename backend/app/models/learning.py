from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Integer, Float, JSON, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class LearningProfile(IdMixin, TimestampMixin, Base):
    """
    Perfil dinâmico de aprendizagem de uma criança.
    Atualizado continuamente baseado em respostas e interações.
    """
    __tablename__ = "learning_profiles"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, unique=True, index=True)

    # Estilo de aprendizagem (0.0-1.0)
    visual_preference: Mapped[float] = mapped_column(Float, default=0.33)  # Imagens, diagramas
    auditory_preference: Mapped[float] = mapped_column(Float, default=0.33)  # Sons, explicações verbais
    kinesthetic_preference: Mapped[float] = mapped_column(Float, default=0.33)  # Prática, movimento

    # Velocidade de aprendizagem (0.5-2.0, 1.0 = normal)
    learning_speed: Mapped[float] = mapped_column(Float, default=1.0)

    # Confiança geral (1-5, 5 = muito confiante)
    confidence_level: Mapped[int] = mapped_column(Integer, default=3)

    # Taxa de retenção (0-1, quanto aprende e retém)
    retention_rate: Mapped[float] = mapped_column(Float, default=0.7)

    # Competências por disciplina/tema (JSON)
    # Ex: {"Português": 0.75, "Matemática": 0.60, "Vogais": 0.85}
    competencies: Mapped[dict] = mapped_column(JSON, default={})

    # Dificuldades identificadas (JSON)
    # Ex: {"dislexia": true, "concentração": 0.5}
    identified_challenges: Mapped[dict] = mapped_column(JSON, default={})

    # Nível de engajamento geral (1-5)
    engagement_level: Mapped[int] = mapped_column(Integer, default=3)

    # Última atualização automática
    last_auto_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Flag se deve usar adaptação automática
    use_adaptive_difficulty: Mapped[bool] = mapped_column(Boolean, default=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    child = relationship("Child")


class LearningHistory(IdMixin, TimestampMixin, Base):
    """
    Histórico completo de aprendizagem de uma criança.
    Armazena todas as interações, respostas e resultados.
    """
    __tablename__ = "learning_histories"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    interaction_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("interactions.id"))
    response_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("interaction_responses.id"))

    # Tema/capítulo estudado
    theme: Mapped[str] = mapped_column(String(180), nullable=False, index=True)

    # Tipo de atividade (pergunta, exercício, leitura, etc)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)

    # Dificuldade apresentada (easy, medium, hard)
    difficulty_presented: Mapped[str] = mapped_column(String(20), default="medium")

    # Resultado (sucesso/falha)
    was_successful: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Score obtido (1-5, ou 0-100, ou similar)
    score: Mapped[int | None] = mapped_column(Integer)

    # Tempo gasto (em segundos)
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer)

    # Feedback fornecido (do LLM)
    feedback: Mapped[str | None] = mapped_column(Text)

    # Estilos de aprendizagem que funcionaram bem (JSON)
    # Ex: ["visual", "kinesthetic"]
    effective_styles: Mapped[list] = mapped_column(JSON, default=[])

    # Data da atividade
    activity_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    child = relationship("Child")


class AdaptiveRecommendation(IdMixin, TimestampMixin, Base):
    """
    Recomendações geradas automaticamente baseadas no perfil de aprendizagem.
    Usado para próximas interações.
    """
    __tablename__ = "adaptive_recommendations"

    child_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    learning_profile_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("learning_profiles.id"), nullable=False, index=True)

    # Tema recomendado
    recommended_theme: Mapped[str] = mapped_column(String(180), nullable=False)

    # Dificuldade recomendada
    recommended_difficulty: Mapped[str] = mapped_column(String(20), nullable=False)  # easy, medium, hard

    # Estilo de aprendizagem recomendado
    recommended_style: Mapped[str] = mapped_column(String(50), nullable=False)  # visual, auditory, kinesthetic

    # Confiança na recomendação (0-1)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)

    # Razão da recomendação (para logging/debug)
    reason: Mapped[str] = mapped_column(Text)

    # Previsão de sucesso (0-1)
    predicted_success_rate: Mapped[float] = mapped_column(Float, default=0.5)

    # Risco de desistência (0-1, 1 = alto risco)
    risk_of_dropout: Mapped[float] = mapped_column(Float, default=0.0)

    # Status (pending, applied, completed)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    child = relationship("Child")
    learning_profile = relationship("LearningProfile")
