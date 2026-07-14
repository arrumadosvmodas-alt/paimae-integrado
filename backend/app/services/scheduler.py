import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from uuid import UUID

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.pedagogy import StudyPlan, DailyStudyPlanItem, Interaction
from app.models.child import Child
from app.models.routine import RoutineItem
from app.models.notification import Notification
from app.db.session import SessionLocal
from app.services.notifications_service import NotificationService
from app.services.llm import get_llm_service

logger = logging.getLogger(__name__)

scheduler = None
notification_service = NotificationService()
llm_service = get_llm_service(settings.google_gemini_api_key)


def initialize_scheduler():
    """Inicializa o scheduler de background."""
    global scheduler
    if scheduler is None:
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            job_dispatch_scheduled_interactions,
            trigger=CronTrigger(minute="*/5"),  # A cada 5 minutos
            id="dispatch_interactions",
            name="Dispatch scheduled interactions",
            replace_existing=True,
        )
        scheduler.add_job(
            job_generate_daily_study_items,
            trigger=CronTrigger(hour=0, minute=0),  # Meia-noite
            id="generate_daily_items",
            name="Generate daily study items",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("✅ Scheduler iniciado com sucesso")


def stop_scheduler():
    """Para o scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
        logger.info("⏹️ Scheduler parado")


def job_dispatch_scheduled_interactions():
    """
    Job que dispara interações agendadas.

    Executado a cada 5 minutos para:
    1. Buscar interações agendadas para "agora"
    2. Enviar notificações via email/SMS/push
    3. Marcar como enviadas
    """
    db = SessionLocal()
    try:
        logger.info("🔄 [Job] Iniciando dispatch de interações agendadas")

        now = datetime.now(ZoneInfo(settings.app_timezone))
        threshold = now + timedelta(minutes=5)

        # Buscar interações agendadas para os próximos 5 minutos
        interactions = db.scalars(
            select(Interaction)
            .where(
                Interaction.status == "scheduled",
                Interaction.scheduled_at <= threshold,
                Interaction.is_active.is_(True),
            )
            .order_by(Interaction.scheduled_at)
        ).all()

        logger.info(f"📬 Encontradas {len(interactions)} interações para enviar")

        for interaction in interactions:
            try:
                child = db.get(Child, interaction.child_id)
                if not child:
                    logger.warning(f"Criança {interaction.child_id} não encontrada")
                    continue

                # Enviar notificação
                result = notification_service.send_interaction(
                    child_name=child.full_name,
                    recipient_type=interaction.recipient_type,
                    message=interaction.message,
                    recipient_email=None,  # Seria preenchido do modelo Child/Guardian
                    recipient_phone=None,
                )

                if result["status"] == "success":
                    interaction.status = "sent"
                    interaction.sent_at = datetime.now(ZoneInfo(settings.app_timezone)).date()

                    # Criar notificação no banco para rastreamento
                    notification = Notification(
                        child_id=interaction.child_id,
                        title=f"Interação: {interaction.recipient_type}",
                        message=interaction.message[:200],
                        scheduled_at=interaction.scheduled_at,
                        status="sent",
                        target_audience=interaction.recipient_type,
                    )
                    db.add(notification)
                    logger.info(f"✅ Interação enviada: {interaction.id}")
                else:
                    logger.error(f"❌ Erro ao enviar interação {interaction.id}: {result.get('error')}")

            except Exception as e:
                logger.error(f"❌ Erro ao processar interação {interaction.id}: {str(e)}")
                continue

        db.commit()
        logger.info(f"✅ Job concluído: {len(interactions)} interações processadas")

    except Exception as e:
        logger.error(f"❌ Erro no job_dispatch_scheduled_interactions: {str(e)}")
        db.rollback()
    finally:
        db.close()


def job_generate_daily_study_items():
    """
    Job que gera itens de estudo para o dia seguinte.

    Executado meia-noite para:
    1. Buscar planos de estudo ativos
    2. Criar item para o próximo dia
    3. Agendar interação correspondente
    """
    db = SessionLocal()
    try:
        logger.info("🔄 [Job] Iniciando geração de itens de estudo diários")

        today = datetime.now(ZoneInfo(settings.app_timezone)).date()
        tomorrow = today + timedelta(days=1)

        # Buscar planos ativos
        study_plans = db.scalars(
            select(StudyPlan)
            .where(
                StudyPlan.status == "active",
                StudyPlan.is_active.is_(True),
                StudyPlan.start_date <= tomorrow,
                (StudyPlan.end_date.is_(None)) | (StudyPlan.end_date >= tomorrow),
            )
        ).all()

        logger.info(f"📚 Encontrados {len(study_plans)} planos ativos")

        items_created = 0
        for study_plan in study_plans:
            try:
                # Verificar se já existe item para amanhã
                existing = db.scalar(
                    select(DailyStudyPlanItem)
                    .where(
                        DailyStudyPlanItem.study_plan_id == study_plan.id,
                        DailyStudyPlanItem.date == tomorrow,
                    )
                )

                if existing:
                    logger.info(f"Item para {tomorrow} já existe no plano {study_plan.id}")
                    continue

                # Gerar próximo item do plano (simplificado)
                # Em produção, isso seria mais sofisticado
                daily_items = db.scalars(
                    select(DailyStudyPlanItem)
                    .where(DailyStudyPlanItem.study_plan_id == study_plan.id)
                    .order_by(DailyStudyPlanItem.date.desc())
                ).first()

                if daily_items:
                    new_item = DailyStudyPlanItem(
                        study_plan_id=study_plan.id,
                        date=tomorrow,
                        chapter_or_theme=daily_items.chapter_or_theme,
                        activity_description=daily_items.activity_description,
                        difficulty_level=daily_items.difficulty_level,
                        estimated_duration_minutes=daily_items.estimated_duration_minutes,
                        status="pending",
                    )
                    db.add(new_item)
                    items_created += 1

                    # Agendar interação para amanhã no horário do turno
                    child = db.get(Child, study_plan.child_id)
                    if child and child.shift:
                        scheduled_time = _get_shift_time(child.shift)
                        interaction = Interaction(
                            child_id=study_plan.child_id,
                            material_id=study_plan.material_id,
                            scheduled_at=tomorrow,
                            recipient_type="child",
                            message=f"Hoje vamos estudar: {new_item.chapter_or_theme}",
                            context_json={
                                "chapter": new_item.chapter_or_theme,
                                "theme": new_item.chapter_or_theme,
                                "activity": new_item.activity_description,
                            },
                            status="scheduled",
                        )
                        db.add(interaction)
                        logger.info(f"✅ Item de estudo e interação criados para {study_plan.id}")

            except Exception as e:
                logger.error(f"❌ Erro ao processar plano {study_plan.id}: {str(e)}")
                continue

        db.commit()
        logger.info(f"✅ Job concluído: {items_created} itens de estudo gerados")

    except Exception as e:
        logger.error(f"❌ Erro no job_generate_daily_study_items: {str(e)}")
        db.rollback()
    finally:
        db.close()


def _get_shift_time(shift: str) -> str:
    """Retorna hora típica do turno."""
    shift_lower = shift.lower()
    if "mat" in shift_lower:
        return "09:00"
    elif "vesp" in shift_lower:
        return "13:00"
    elif "integ" in shift_lower:
        return "11:00"
    else:
        return "09:00"


def manually_dispatch_interaction(db: Session, interaction_id: UUID) -> dict:
    """Dispara uma interação manualmente (para testes ou disparo manual)."""
    interaction = db.get(Interaction, interaction_id)
    if not interaction:
        return {"status": "error", "message": "Interação não encontrada"}

    try:
        child = db.get(Child, interaction.child_id)
        if not child:
            return {"status": "error", "message": "Criança não encontrada"}

        result = notification_service.send_interaction(
            child_name=child.full_name,
            recipient_type=interaction.recipient_type,
            message=interaction.message,
            recipient_email=None,
            recipient_phone=None,
        )

        if result["status"] == "success":
            interaction.status = "sent"
            interaction.sent_at = datetime.now(ZoneInfo(settings.app_timezone)).date()

            notification = Notification(
                child_id=interaction.child_id,
                title=f"Interação Manual: {interaction.recipient_type}",
                message=interaction.message[:200],
                scheduled_at=interaction.scheduled_at,
                status="sent",
                target_audience=interaction.recipient_type,
            )
            db.add(notification)
            db.commit()

            return {
                "status": "success",
                "message": "Interação enviada com sucesso",
                "interaction_id": str(interaction_id),
            }
        else:
            return {
                "status": "error",
                "message": result.get("error", "Erro desconhecido"),
            }
    except Exception as e:
        logger.error(f"Erro ao disparar interação manualmente: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
        }
