from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.pedagogy import AcademicGrade
from app.models.user import User
from app.schemas.pedagogy import (
    AcademicGradeCreate,
    AcademicGradeRead,
    AttendanceRecordCreate,
    AttendanceRecordRead,
    DailyJourneyRead,
    DailyLearningSessionRead,
    DailySessionAcknowledge,
)
from app.services.audit import record_audit
from app.services.daily_journey import acknowledge_daily_session, get_or_create_daily_journey, upsert_attendance
from app.services.permissions import ensure_child_access, ensure_school_staff

router = APIRouter()


@router.get("", response_model=DailyJourneyRead)
def get_daily_journey(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    target_date: date | None = None,
):
    ensure_child_access(db, current_user, child_id)
    try:
        journey = get_or_create_daily_journey(db, child_id, target_date or date.today())
        db.commit()
        return journey
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/acknowledge", response_model=DailyLearningSessionRead)
def acknowledge_journey(
    payload: DailySessionAcknowledge,
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    target_date: date | None = None,
):
    ensure_child_access(db, current_user, child_id)
    if not payload.acknowledged:
        raise HTTPException(status_code=400, detail="Confirmacao de ciencia obrigatoria.")
    session = acknowledge_daily_session(db, child_id, target_date or date.today())
    record_audit(db, actor=current_user, action="daily_journey.acknowledge", entity_type="daily_learning_session", entity_id=session.id, school_id=session.child.school_id)
    db.commit()
    db.refresh(session)
    return session


@router.post("/attendance", response_model=AttendanceRecordRead, status_code=status.HTTP_201_CREATED)
def save_attendance(
    payload: AttendanceRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    child = ensure_child_access(db, current_user, payload.child_id)
    record = upsert_attendance(db, payload.child_id, payload.date, payload.status, payload.reason, payload.notes)
    record_audit(db, actor=current_user, action="daily_journey.attendance_upsert", entity_type="attendance_record", entity_id=record.id, school_id=child.school_id)
    db.commit()
    db.refresh(record)
    return record


@router.post("/grades", response_model=AcademicGradeRead, status_code=status.HTTP_201_CREATED)
def create_grade(
    payload: AcademicGradeCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    child = ensure_child_access(db, current_user, payload.child_id)
    if str(child.school_id) != str(payload.school_id):
        raise HTTPException(status_code=400, detail="Crianca nao pertence a escola informada.")
    grade = AcademicGrade(**payload.model_dump())
    db.add(grade)
    db.flush()
    record_audit(db, actor=current_user, action="daily_journey.grade_create", entity_type="academic_grade", entity_id=grade.id, school_id=payload.school_id)
    db.commit()
    db.refresh(grade)
    return grade


@router.get("/grades", response_model=list[AcademicGradeRead])
def list_grades(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id)
    return list(
        db.scalars(
            select(AcademicGrade)
            .where(AcademicGrade.child_id == child_id, AcademicGrade.is_active.is_(True))
            .order_by(AcademicGrade.assessment_date.desc().nullslast(), AcademicGrade.created_at.desc())
        )
    )
