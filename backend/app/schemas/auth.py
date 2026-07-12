from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Timestamped


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(admin|school_admin|teacher|guardian)$")
    school_id: UUID | None = None


class UserRead(Timestamped):
    name: str
    email: EmailStr
    role: str
    school_id: UUID | None
    is_active: bool

