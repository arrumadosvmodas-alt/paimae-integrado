from fastapi import APIRouter

from app.api.v1.endpoints import ai, audit, auth, children, guardians, notifications, routines, schools, tasks, evolution, pedagogy, reports, study_plan

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(children.router, prefix="/children", tags=["children"])
api_router.include_router(guardians.router, prefix="/child-guardians", tags=["child-guardians"])
api_router.include_router(routines.router, prefix="/routines", tags=["routines"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(evolution.router, prefix="/evolution-events", tags=["evolution"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(audit.router, prefix="/audit-logs", tags=["audit"])
api_router.include_router(pedagogy.router, prefix="/pedagogy", tags=["pedagogy"])
api_router.include_router(study_plan.router, prefix="/study-plans", tags=["study-plans"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])

