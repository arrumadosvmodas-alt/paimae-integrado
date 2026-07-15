from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.child import Child
from app.models.pedagogy import (
    AcademicGrade,
    AttendanceRecord,
    DailyLearningSession,
    Interaction,
    SchoolSchedule,
)
from app.services.schedule_generation import generate_daily_activity_from_schedule


def get_or_create_daily_journey(db: Session, child_id: UUID, target_date: date) -> dict:
    child = db.get(Child, child_id)
    if not child:
        raise ValueError("Crianca nao encontrada.")

    schedules = list(
        db.scalars(
            select(SchoolSchedule)
            .where(
                SchoolSchedule.child_id == child_id,
                SchoolSchedule.date == target_date,
                SchoolSchedule.is_active.is_(True),
            )
            .order_by(SchoolSchedule.subject.asc())
        )
    )

    for schedule in schedules:
        if schedule.status in ("planned", "confirmed"):
            generate_daily_activity_from_schedule(db, schedule.id)

    session = db.scalar(
        select(DailyLearningSession).where(
            DailyLearningSession.child_id == child_id,
            DailyLearningSession.date == target_date,
            DailyLearningSession.is_active.is_(True),
        )
    )
    if not session:
        session = DailyLearningSession(child_id=child_id, date=target_date, source="system", is_active=True)
        db.add(session)
        db.flush()

    interactions = list(
        db.scalars(
            select(Interaction)
            .where(
                Interaction.child_id == child_id,
                Interaction.scheduled_at == target_date,
                Interaction.is_active.is_(True),
            )
            .order_by(Interaction.recipient_type.asc(), Interaction.created_at.asc())
        )
    )
    child_interactions = [item for item in interactions if item.recipient_type == "child"]
    parent_interactions = [item for item in interactions if item.recipient_type == "parent"]

    requires_manual_schedule = len(schedules) == 0
    session.status = _resolve_session_status(session, schedules, interactions, requires_manual_schedule)
    session.source = "schedule" if schedules else "manual_required"
    session.child_activity = _compose_child_activity(child_interactions, schedules)
    session.parent_guidance = _compose_parent_guidance(parent_interactions, requires_manual_schedule)
    session.summary = _compose_summary(child.full_name, schedules, interactions, requires_manual_schedule)
    session.context_json = {
        "schedule_count": len(schedules),
        "interaction_count": len(interactions),
        "requires_manual_schedule": requires_manual_schedule,
    }
    db.flush()

    attendance = db.scalar(
        select(AttendanceRecord).where(
            AttendanceRecord.child_id == child_id,
            AttendanceRecord.date == target_date,
            AttendanceRecord.is_active.is_(True),
        )
    )
    grades = list(
        db.scalars(
            select(AcademicGrade)
            .where(AcademicGrade.child_id == child_id, AcademicGrade.is_active.is_(True))
            .order_by(AcademicGrade.assessment_date.desc().nullslast(), AcademicGrade.created_at.desc())
        )
    )

    return {
        "date": target_date,
        "child_id": child_id,
        "session": session,
        "schedules": schedules,
        "child_interactions": [_interaction_payload(item) for item in child_interactions],
        "parent_interactions": [_interaction_payload(item) for item in parent_interactions],
        "attendance": attendance,
        "grades": grades[:10],
        "requires_manual_schedule": requires_manual_schedule,
    }


def acknowledge_daily_session(db: Session, child_id: UUID, target_date: date) -> DailyLearningSession:
    journey = get_or_create_daily_journey(db, child_id, target_date)
    session = journey["session"]
    session.acknowledged_at = target_date
    if session.status not in ("waiting_schedule", "no_schedule"):
        session.status = "acknowledged"
    db.flush()
    return session


def upsert_attendance(db: Session, child_id: UUID, target_date: date, status: str, reason: str | None, notes: str | None) -> AttendanceRecord:
    record = db.scalar(
        select(AttendanceRecord).where(AttendanceRecord.child_id == child_id, AttendanceRecord.date == target_date)
    )
    if not record:
        record = AttendanceRecord(child_id=child_id, date=target_date)
        db.add(record)
    record.status = status
    record.reason = reason
    record.notes = notes
    record.is_active = True
    db.flush()
    return record


def _resolve_session_status(session: DailyLearningSession, schedules: list[SchoolSchedule], interactions: list[Interaction], missing_schedule: bool) -> str:
    if session.acknowledged_at:
        return "acknowledged"
    if missing_schedule:
        return "waiting_schedule"
    if interactions:
        return "interactions_ready"
    if schedules:
        return "scheduled"
    return "waiting_schedule"


def _compose_child_activity(interactions: list[Interaction], schedules: list[SchoolSchedule]) -> str | None:
    if interactions:
        return "\n\n".join(item.message for item in interactions)
    if schedules:
        parts = [f"{item.subject}: {item.topic or item.subject}" for item in schedules]
        return "Atividade do dia: " + "; ".join(parts)
    return None


def _compose_parent_guidance(interactions: list[Interaction], missing_schedule: bool) -> str:
    if missing_schedule:
        return "Nao ha cronograma para esta data. Inclua a atividade manualmente para o sistema gerar as interacoes automaticamente."
    if interactions:
        return "\n\n".join(item.message for item in interactions)
    return "Acompanhe a atividade do dia, observe dificuldades e registre satisfacao ao final."


def _compose_summary(child_name: str, schedules: list[SchoolSchedule], interactions: list[Interaction], missing_schedule: bool) -> str:
    if missing_schedule:
        return f"Hoje ainda nao existe cronograma registrado para {child_name}."
    subjects = ", ".join(sorted({item.subject for item in schedules}))
    return f"Jornada de {child_name} preparada para {subjects or 'atividade do dia'} com {len(interactions)} interacao(oes) gerada(s)."


def _interaction_payload(interaction: Interaction) -> dict:
    return {
        "id": str(interaction.id),
        "child_id": str(interaction.child_id),
        "material_id": str(interaction.material_id) if interaction.material_id else None,
        "scheduled_at": interaction.scheduled_at,
        "sent_at": interaction.sent_at,
        "recipient_type": interaction.recipient_type,
        "message": interaction.message,
        "context_json": interaction.context_json,
        "status": interaction.status,
        "is_active": interaction.is_active,
        "responses": [],
    }
