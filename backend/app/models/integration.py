"""Modelos para integrações externas."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Integration(IdMixin, TimestampMixin, Base):
    """Configuração de integração externa."""
    __tablename__ = "integrations"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # google_classroom, microsoft_teams, whatsapp_business, generic_webhook
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Credenciais encriptadas (guardar em vault em produção)
    credentials: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Configurações específicas do provider
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # URLs de webhook
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    webhook_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Sincronização
    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_interval_minutes: Mapped[int] = mapped_column(Integer, default=60)

    # Relacionamentos
    school = relationship("School", back_populates="integrations")
    sync_logs = relationship("IntegrationSyncLog", back_populates="integration", cascade="all, delete-orphan")
    webhooks = relationship("WebhookEvent", back_populates="integration", cascade="all, delete-orphan")


class IntegrationSyncLog(IdMixin, TimestampMixin, Base):
    """Histórico de sincronização."""
    __tablename__ = "integration_sync_logs"

    integration_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # success, error, partial, started
    records_synced: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    integration = relationship("Integration", back_populates="sync_logs")


class WebhookEvent(IdMixin, TimestampMixin, Base):
    """Eventos recebidos via webhook."""
    __tablename__ = "webhook_events"

    integration_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("integrations.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    integration = relationship("Integration", back_populates="webhooks")


class GoogleClassroomSync(IdMixin, TimestampMixin, Base):
    """Sincronização com Google Classroom."""
    __tablename__ = "google_classroom_syncs"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    classroom_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    classroom_name: Mapped[str] = mapped_column(String(255), nullable=False)
    teacher_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # Mapeamento
    mapped_class_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=True)

    # Configuração de sincronização
    sync_assignments: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_grades: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_announcements: Mapped[bool] = mapped_column(Boolean, default=False)

    last_assignment_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_grade_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MicrosoftTeamsSync(IdMixin, TimestampMixin, Base):
    """Sincronização com Microsoft Teams."""
    __tablename__ = "microsoft_teams_syncs"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    team_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_id: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Mapeamento
    mapped_class_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("children.id"), nullable=True)

    # Configuração
    sync_assignments: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_messages: Mapped[bool] = mapped_column(Boolean, default=False)
    post_to_channel: Mapped[bool] = mapped_column(Boolean, default=True)

    last_sync: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WhatsAppBusinessSync(IdMixin, TimestampMixin, Base):
    """Sincronização com WhatsApp Business."""
    __tablename__ = "whatsapp_business_syncs"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    phone_number_id: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relacionamento com responsáveis
    guardian_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Configuração
    send_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    send_grades: Mapped[bool] = mapped_column(Boolean, default=False)
    send_assignments: Mapped[bool] = mapped_column(Boolean, default=True)

    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WebhookSubscription(IdMixin, TimestampMixin, Base):
    """Inscrição em webhooks customizados."""
    __tablename__ = "webhook_subscriptions"

    school_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)

    # Eventos que disparam
    events: Mapped[list] = mapped_column(JSON, nullable=False)  # ["assignment.created", "grade.updated"]

    # Filtros
    filters: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Estatísticas
    total_delivered: Mapped[int] = mapped_column(Integer, default=0)
    total_failed: Mapped[int] = mapped_column(Integer, default=0)
    last_delivery: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
