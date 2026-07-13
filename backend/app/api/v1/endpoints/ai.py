from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import ChildSummaryRequest, ChildSummaryResponse
from app.services.ai import build_child_summary
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access

router = APIRouter()


@router.post("/summaries", response_model=ChildSummaryResponse)
def summarize_child(payload: ChildSummaryRequest, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    child = ensure_child_access(db, current_user, payload.child_id)
    result = build_child_summary(db, payload.child_id)
    record_audit(
        db,
        actor=current_user,
        action="ai.summary",
        entity_type="child",
        entity_id=payload.child_id,
        school_id=child.school_id,
        payload={"status": result["status"], "data_points": result["data_points"]},
    )
    db.commit()
    return ChildSummaryResponse(child_id=payload.child_id, **result)


from app.schemas.ai import InteractionRequest, InteractionResponse
from app.services.ai import build_child_interaction


@router.post("/interactions", response_model=InteractionResponse)
def get_child_interaction(
    payload: InteractionRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    child = ensure_child_access(db, current_user, payload.child_id)
    result = build_child_interaction(db, payload.child_id, payload.interaction_type)
    
    record_audit(
        db,
        actor=current_user,
        action="ai.interaction",
        entity_type="child",
        entity_id=payload.child_id,
        school_id=child.school_id,
        payload={"interaction_type": payload.interaction_type, "status": result["status"]},
    )
    db.commit()
    return InteractionResponse(
        child_id=payload.child_id,
        interaction_type=payload.interaction_type,
        status=result["status"],
        content=result["content"]
    )


