from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.child import Child
from app.models.child_guardian import ChildGuardian
from app.models.user import User
from app.schemas.common import ActiveStatusUpdate
from app.schemas.child import ChildCreate, ChildRead, ChildUpdate
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_school_access

router = APIRouter()


@router.post("", response_model=ChildRead, status_code=status.HTTP_201_CREATED)
def create_child(payload: ChildCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    ensure_school_access(current_user, payload.school_id)
    child = Child(**payload.model_dump())
    db.add(child)
    db.flush()
    record_audit(db, actor=current_user, action="child.create", entity_type="child", entity_id=child.id, school_id=child.school_id)
    db.commit()
    db.refresh(child)
    return child


@router.get("", response_model=list[ChildRead])
def list_children(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    query = select(Child).order_by(Child.full_name)
    if current_user.role == "admin":
        return list(db.scalars(query))
    if current_user.school_id:
        return list(db.scalars(query.where(Child.school_id == current_user.school_id)))
    linked_ids = select(ChildGuardian.child_id).where(ChildGuardian.guardian_id == current_user.id, ChildGuardian.can_view.is_(True))
    return list(db.scalars(query.where(Child.id.in_(linked_ids), Child.is_active.is_(True))))


@router.get("/{child_id}", response_model=ChildRead)
def get_child(child_id: UUID, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    return ensure_child_access(db, current_user, child_id)


@router.put("/{child_id}", response_model=ChildRead)
def update_child(
    child_id: UUID,
    payload: ChildUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = db.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Criança não encontrada.")
    ensure_school_access(current_user, child.school_id)
    ensure_school_access(current_user, payload.school_id)
    
    child.full_name = payload.full_name
    child.birth_date = payload.birth_date
    child.school_id = payload.school_id
    child.class_name = payload.class_name
    
    record_audit(db, actor=current_user, action="child.update", entity_type="child", entity_id=child.id, school_id=child.school_id)
    db.commit()
    db.refresh(child)
    return child


@router.patch("/{child_id}/status", response_model=ChildRead)
def update_child_status(
    child_id: UUID,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = db.get(Child, child_id)
    if not child:
        raise HTTPException(status_code=404, detail="Criança não encontrada.")
    ensure_school_access(current_user, child.school_id)
    
    previous_status = child.is_active
    child.is_active = payload.is_active
    record_audit(
        db,
        actor=current_user,
        action="child.status_update",
        entity_type="child",
        entity_id=child.id,
        school_id=child.school_id,
        payload={"previous_is_active": previous_status, "is_active": child.is_active},
    )
    db.commit()
    db.refresh(child)
    return child


@router.get("/{child_id}/export-lgpd")
def export_child_lgpd(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = ensure_child_access(db, current_user, child_id)
    
    # Busca todos os dados vinculados ao aluno
    from app.models.routine import RoutineItem
    from app.models.task import Task
    from app.models.pedagogy import DailySchoolRecord
    from app.models.evolution import EvolutionEvent
    from app.models.child_guardian import ChildGuardian
    from fastapi.responses import JSONResponse
    
    routines = db.scalars(select(RoutineItem).where(RoutineItem.child_id == child_id)).all()
    tasks = db.scalars(select(Task).where(Task.child_id == child_id)).all()
    daily_records = db.scalars(select(DailySchoolRecord).where(DailySchoolRecord.child_id == child_id)).all()
    evolution_events = db.scalars(select(EvolutionEvent).where(EvolutionEvent.child_id == child_id)).all()
    guardians = db.scalars(select(ChildGuardian).where(ChildGuardian.child_id == child_id)).all()
    
    data = {
        "child": {
            "id": str(child.id),
            "name": child.name,
            "birth_date": child.birth_date.strftime("%Y-%m-%d") if child.birth_date else None,
            "class_name": child.class_name,
            "created_at": child.created_at.isoformat() if child.created_at else None,
        },
        "routines": [
            {
                "id": str(r.id),
                "title": r.title,
                "description": r.description,
                "hour": r.hour,
                "period": r.period,
            } for r in routines
        ],
        "tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "due_date": t.due_date.strftime("%Y-%m-%d") if t.due_date else None,
                "status": t.status,
            } for t in tasks
        ],
        "daily_records": [
            {
                "id": str(dr.id),
                "date": dr.date.strftime("%Y-%m-%d"),
                "summary": dr.summary,
                "observed_skills": dr.observed_skills,
                "engagement_score": dr.engagement_score,
            } for dr in daily_records
        ],
        "evolution_events": [
            {
                "id": str(ee.id),
                "occurred_at": ee.occurred_at.isoformat(),
                "notes": ee.notes,
                "score": ee.score,
            } for ee in evolution_events
        ],
        "guardians_linked": [
            {
                "guardian_id": str(g.guardian_id),
                "can_view": g.can_view,
                "can_edit": g.can_edit,
            } for g in guardians
        ]
    }
    
    headers = {
        "Content-Disposition": f"attachment; filename=portabilidade_aluno_{child.id}.json"
    }
    return JSONResponse(content=data, headers=headers)


@router.delete("/{child_id}/forget-lgpd", status_code=status.HTTP_204_NO_CONTENT)
def forget_child_lgpd(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = ensure_child_access(db, current_user, child_id)
    if current_user.role != "admin" and current_user.role != "guardian":
        raise HTTPException(status_code=403, detail="Apenas responsáveis ou administradores podem remover definitivamente os dados.")
        
    from app.models.routine import RoutineItem
    from app.models.task import Task
    from app.models.pedagogy import DailySchoolRecord
    from app.models.evolution import EvolutionEvent
    from app.models.child_guardian import ChildGuardian
    from sqlalchemy import delete
    
    db.execute(delete(RoutineItem).where(RoutineItem.child_id == child_id))
    db.execute(delete(Task).where(Task.child_id == child_id))
    db.execute(delete(DailySchoolRecord).where(DailySchoolRecord.child_id == child_id))
    db.execute(delete(EvolutionEvent).where(EvolutionEvent.child_id == child_id))
    db.execute(delete(ChildGuardian).where(ChildGuardian.child_id == child_id))
    
    db.delete(child)
    
    record_audit(db, actor=current_user, action="child.forget_lgpd", entity_type="child", entity_id=child_id, school_id=child.school_id)
    db.commit()
    return
