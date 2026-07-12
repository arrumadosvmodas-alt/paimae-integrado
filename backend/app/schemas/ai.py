from uuid import UUID

from pydantic import BaseModel


class ChildSummaryRequest(BaseModel):
    child_id: UUID


class ChildSummaryResponse(BaseModel):
    child_id: UUID
    status: str
    summary: str
    data_points: int

