import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.child import Child
from app.models.pedagogy import (
    DailyStudyPlanItem,
    Interaction,
    MaterialIndexEntry,
    PedagogicalMaterial,
    SchoolSchedule,
    StudyPlan,
)
from app.services.llm import get_llm_service

logger = logging.getLogger(__name__)
llm_service = get_llm_service(settings.google_gemini_api_key)


def generate_daily_activity_from_schedule(db: Session, schedule_id: UUID) -> dict:
    schedule = db.get(SchoolSchedule, schedule_id)
    if not schedule or not schedule.is_active:
        return {"status": "error", "message": "Cronograma nao encontrado ou inativo."}

    child = db.get(Child, schedule.child_id)
    if not child:
        return {"status": "error", "message": "Crianca nao encontrada."}

    material = _select_material_for_schedule(db, schedule)
    study_plan = _get_or_create_schedule_study_plan(db, child, schedule, material)
    theme = schedule.topic or schedule.subject
    chapter = _resolve_chapter(db, material, theme)

    daily_item = _get_or_create_daily_item(db, study_plan, schedule, theme)
    child_interaction = _get_or_create_schedule_interaction(
        db,
        schedule=schedule,
        child=child,
        material=material,
        recipient_type="child",
        chapter=chapter,
        theme=theme,
    )
    parent_interaction = _get_or_create_schedule_interaction(
        db,
        schedule=schedule,
        child=child,
        material=material,
        recipient_type="parent",
        chapter=chapter,
        theme=theme,
    )

    schedule.status = "confirmed" if schedule.status == "planned" else schedule.status
    db.flush()

    return {
        "status": "success",
        "message": "Atividades geradas a partir do cronograma.",
        "schedule_id": str(schedule.id),
        "daily_item_id": str(daily_item.id),
        "child_interaction_id": str(child_interaction.id),
        "parent_interaction_id": str(parent_interaction.id),
        "material_id": str(material.id) if material else None,
        "fallback_used": schedule.fallback_used,
    }


def generate_daily_activities_for_date(db: Session, target_date: date) -> list[dict]:
    schedules = db.scalars(
        select(SchoolSchedule)
        .where(
            SchoolSchedule.date == target_date,
            SchoolSchedule.is_active.is_(True),
            SchoolSchedule.status.in_(("planned", "confirmed")),
        )
        .order_by(SchoolSchedule.child_id, SchoolSchedule.subject)
    ).all()

    results = []
    for schedule in schedules:
        try:
            results.append(generate_daily_activity_from_schedule(db, schedule.id))
        except Exception as exc:  # pragma: no cover - job resilience
            logger.exception("Erro ao gerar atividade do cronograma %s", schedule.id)
            results.append({"status": "error", "schedule_id": str(schedule.id), "message": str(exc)})
    return results


def _select_material_for_schedule(db: Session, schedule: SchoolSchedule) -> PedagogicalMaterial | None:
    subject_term = f"%{schedule.subject.lower()}%"
    topic_term = f"%{(schedule.topic or schedule.subject).lower()}%"

    material = db.scalar(
        select(PedagogicalMaterial)
        .where(
            PedagogicalMaterial.school_id == schedule.school_id,
            PedagogicalMaterial.is_active.is_(True),
            PedagogicalMaterial.subject.ilike(subject_term),
        )
        .order_by(PedagogicalMaterial.updated_at.desc())
    )
    if material:
        return material

    indexed = db.scalar(
        select(PedagogicalMaterial)
        .join(MaterialIndexEntry, MaterialIndexEntry.material_id == PedagogicalMaterial.id)
        .where(
            PedagogicalMaterial.school_id == schedule.school_id,
            PedagogicalMaterial.is_active.is_(True),
            MaterialIndexEntry.is_active.is_(True),
            MaterialIndexEntry.theme.ilike(topic_term),
        )
        .order_by(PedagogicalMaterial.updated_at.desc())
    )
    if indexed:
        return indexed

    schedule.fallback_used = True
    return db.scalar(
        select(PedagogicalMaterial)
        .where(
            PedagogicalMaterial.school_id == schedule.school_id,
            PedagogicalMaterial.is_active.is_(True),
        )
        .order_by(PedagogicalMaterial.updated_at.desc())
    )


def _get_or_create_schedule_study_plan(
    db: Session,
    child: Child,
    schedule: SchoolSchedule,
    material: PedagogicalMaterial | None,
) -> StudyPlan:
    if material:
        study_plan = db.scalar(
            select(StudyPlan).where(
                StudyPlan.child_id == child.id,
                StudyPlan.material_id == material.id,
                StudyPlan.status.in_(("draft", "active")),
                StudyPlan.is_active.is_(True),
            )
        )
        if study_plan:
            if study_plan.status == "draft":
                study_plan.status = "active"
            return study_plan

    if not material:
        material = _get_or_create_fallback_material(db, child, schedule)

    study_plan = StudyPlan(
        child_id=child.id,
        material_id=material.id,
        start_date=schedule.date,
        end_date=schedule.date + timedelta(days=30),
        ai_generated_plan=f"Plano automatico gerado a partir do cronograma: {schedule.subject} - {schedule.topic or schedule.subject}.",
        status="active",
        is_active=True,
    )
    db.add(study_plan)
    db.flush()
    return study_plan


def _get_or_create_fallback_material(db: Session, child: Child, schedule: SchoolSchedule) -> PedagogicalMaterial:
    material = db.scalar(
        select(PedagogicalMaterial).where(
            PedagogicalMaterial.school_id == child.school_id,
            PedagogicalMaterial.title == "Cronograma pedagogico",
            PedagogicalMaterial.subject == schedule.subject,
        )
    )
    if material:
        return material

    material = PedagogicalMaterial(
        school_id=child.school_id,
        title="Cronograma pedagogico",
        author="Sistema PaiMae Integrado",
        subject=schedule.subject,
        pedagogical_line="A definir pela escola",
        objectives="Gerado automaticamente para apoiar atividades baseadas no cronograma escolar.",
        family_orientation="Acompanhar a atividade diaria e registrar dificuldades observadas.",
        processing_status="completed",
        is_active=True,
    )
    db.add(material)
    db.flush()
    return material


def _resolve_chapter(db: Session, material: PedagogicalMaterial | None, theme: str) -> str:
    if not material:
        return theme
    entry = db.scalar(
        select(MaterialIndexEntry)
        .where(
            MaterialIndexEntry.material_id == material.id,
            MaterialIndexEntry.is_active.is_(True),
            MaterialIndexEntry.theme.ilike(f"%{theme.lower()}%"),
        )
        .order_by(MaterialIndexEntry.page_start.asc())
    )
    return entry.chapter or entry.theme if entry else theme


def _get_or_create_daily_item(
    db: Session,
    study_plan: StudyPlan,
    schedule: SchoolSchedule,
    theme: str,
) -> DailyStudyPlanItem:
    existing = db.scalar(
        select(DailyStudyPlanItem).where(
            DailyStudyPlanItem.study_plan_id == study_plan.id,
            DailyStudyPlanItem.date == schedule.date,
            DailyStudyPlanItem.chapter_or_theme == theme,
        )
    )
    if existing:
        return existing

    item = DailyStudyPlanItem(
        study_plan_id=study_plan.id,
        date=schedule.date,
        chapter_or_theme=theme,
        activity_description=_build_activity_description(schedule, theme),
        difficulty_level="medium",
        estimated_duration_minutes=30,
        status="pending",
        is_active=True,
    )
    db.add(item)
    db.flush()
    return item


def _get_or_create_schedule_interaction(
    db: Session,
    *,
    schedule: SchoolSchedule,
    child: Child,
    material: PedagogicalMaterial | None,
    recipient_type: str,
    chapter: str,
    theme: str,
) -> Interaction:
    candidates = db.scalars(
        select(Interaction).where(
            Interaction.child_id == child.id,
            Interaction.scheduled_at == schedule.date,
            Interaction.recipient_type == recipient_type,
            Interaction.is_active.is_(True),
        )
    ).all()
    for candidate in candidates:
        if (candidate.context_json or {}).get("schedule_id") == str(schedule.id):
            return candidate

    message = llm_service.generate_daily_interaction(
        child_name=child.full_name,
        chapter=chapter,
        theme=theme,
        recipient_type=recipient_type,
    )
    interaction = Interaction(
        child_id=child.id,
        material_id=material.id if material else None,
        scheduled_at=schedule.date,
        recipient_type=recipient_type,
        message=message,
        context_json={
            "source": "school_schedule",
            "schedule_id": str(schedule.id),
            "subject": schedule.subject,
            "theme": theme,
            "chapter": chapter,
            "fallback_used": schedule.fallback_used,
        },
        status="scheduled",
        is_active=True,
    )
    db.add(interaction)
    db.flush()
    return interaction