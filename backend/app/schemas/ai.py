from uuid import UUID

from pydantic import BaseModel


class ChildSummaryRequest(BaseModel):
    child_id: UUID


class ChildSummaryResponse(BaseModel):
    child_id: UUID
    status: str
    summary: str
    data_points: int


class InteractionRequest(BaseModel):
    child_id: UUID
    interaction_type: str  # "conversation", "question", "guidance"


class InteractionResponse(BaseModel):
    child_id: UUID
    interaction_type: str
    status: str
    content: str


