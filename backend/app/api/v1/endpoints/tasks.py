from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskStatusUpdate
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, scoped_child_ids_query

router = APIRouter()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    child = ensure_child_access(db, current_user, payload.child_id)
    task = Task(**payload.model_dump())
    db.add(task)
    db.flush()
    record_audit(db, actor=current_user, action="task.create", entity_type="task", entity_id=task.id, school_id=child.school_id)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=list[TaskRead])
def list_tasks(db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)], child_id: UUID | None = None):
    query = select(Task).order_by(Task.created_at.desc()).limit(100)
    if child_id:
        ensure_child_access(db, current_user, child_id)
        query = query.where(Task.child_id == child_id)
    else:
        query = query.where(Task.child_id.in_(scoped_child_ids_query(current_user)))
    return list(db.scalars(query))


@router.patch("/{task_id}/status", response_model=TaskRead)
def update_task_status(task_id: UUID, payload: TaskStatusUpdate, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    child = ensure_child_access(db, current_user, task.child_id)
    task.status = payload.status
    record_audit(db, actor=current_user, action="task.status_update", entity_type="task", entity_id=task.id, school_id=child.school_id, payload=payload.model_dump())
    db.commit()
    db.refresh(task)
    return task
