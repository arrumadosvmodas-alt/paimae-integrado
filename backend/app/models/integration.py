"""Modelos para integrações externas."""
from sqlalchemy import Column, String, JSON, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base, BaseModel


class IntegrationProvider(str, enum.Enum):
    """Provedores de integração suportados."""
    GOOGLE_CLASSROOM = "google_classroom"
    MICROSOFT_TEAMS = "microsoft_teams"
    WHATSAPP_BUSINESS = "whatsapp_business"
    GENERIC_WEBHOOK = "generic_webhook"


class Integration(Base, BaseModel):
    """Configuração de integração externa."""
    __tablename__ = "integrations"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    provider = Column(String(50), nullable=False)  # IntegrationProvider
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    # Credenciais encriptadas (guardar em vault em produção)
    credentials = Column(JSON, nullable=True)

    # Configurações específicas do provider
    config = Column(JSON, nullable=True)

    # URLs de webhook
    webhook_url = Column(String(500), nullable=True)
    webhook_secret = Column(String(255), nullable=True)

    # Sincronização
    last_sync = Column(DateTime, nullable=True)
    sync_enabled = Column(Boolean, default=False)
    sync_interval_minutes = Column(String(50), default="60")

    # Relacionamentos
    school = relationship("School", back_populates="integrations")
    sync_logs = relationship("IntegrationSyncLog", back_populates="integration")
    webhooks = relationship("WebhookEvent", back_populates="integration")


class IntegrationSyncLog(Base, BaseModel):
    """Histórico de sincronização."""
    __tablename__ = "integration_sync_logs"

    integration_id = Column(String(36), ForeignKey("integrations.id"), nullable=False)
    status = Column(String(20), nullable=False)  # success, error, partial
    records_synced = Column(String(50), default="0")
    error_message = Column(String(500), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    integration = relationship("Integration", back_populates="sync_logs")


class WebhookEvent(Base, BaseModel):
    """Eventos recebidos via webhook."""
    __tablename__ = "webhook_events"

    integration_id = Column(String(36), ForeignKey("integrations.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    error = Column(String(500), nullable=True)
    received_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    integration = relationship("Integration", back_populates="webhooks")


class GoogleClassroomSync(Base, BaseModel):
    """Sincronização com Google Classroom."""
    __tablename__ = "google_classroom_syncs"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    classroom_id = Column(String(100), nullable=False, unique=True)
    classroom_name = Column(String(255), nullable=False)
    teacher_email = Column(String(255), nullable=False)

    # Mapeamento
    mapped_class_id = Column(String(36), ForeignKey("children.id"), nullable=True)

    # Configuração de sincronização
    sync_assignments = Column(Boolean, default=True)
    sync_grades = Column(Boolean, default=True)
    sync_announcements = Column(Boolean, default=False)

    last_assignment_sync = Column(DateTime, nullable=True)
    last_grade_sync = Column(DateTime, nullable=True)


class MicrosoftTeamsSync(Base, BaseModel):
    """Sincronização com Microsoft Teams."""
    __tablename__ = "microsoft_teams_syncs"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    team_id = Column(String(100), nullable=False, unique=True)
    team_name = Column(String(255), nullable=False)
    channel_id = Column(String(100), nullable=False)
    channel_name = Column(String(255), nullable=False)

    # Mapeamento
    mapped_class_id = Column(String(36), ForeignKey("children.id"), nullable=True)

    # Configuração
    sync_assignments = Column(Boolean, default=True)
    sync_messages = Column(Boolean, default=False)
    post_to_channel = Column(Boolean, default=True)

    last_sync = Column(DateTime, nullable=True)


class WhatsAppBusinessSync(Base, BaseModel):
    """Sincronização com WhatsApp Business."""
    __tablename__ = "whatsapp_business_syncs"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    phone_number_id = Column(String(50), nullable=False, unique=True)
    phone_number = Column(String(20), nullable=False)

    # Relacionamento com responsáveis
    guardian_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Configuração
    send_notifications = Column(Boolean, default=True)
    send_grades = Column(Boolean, default=False)
    send_assignments = Column(Boolean, default=True)

    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)


class WebhookSubscription(Base, BaseModel):
    """Inscrição em webhooks customizados."""
    __tablename__ = "webhook_subscriptions"

    school_id = Column(String(36), ForeignKey("schools.id"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=False)

    # Eventos que disparam
    events = Column(JSON, nullable=False)  # ["assignment.created", "grade.updated"]

    # Filtros
    filters = Column(JSON, nullable=True)

    active = Column(Boolean, default=True)

    # Estatísticas
    total_delivered = Column(String(50), default="0")
    total_failed = Column(String(50), default="0")
    last_delivery = Column(DateTime, nullable=True)
