from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.schemas.common import Timestamped


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str = Field(pattern="^(admin|school_admin|teacher|guardian)$")
    school_id: UUID | None = None
    document: str | None = Field(default=None, min_length=11, max_length=14)

    @model_validator(mode="after")
    def validate_admin_fields(self):
        if self.role == "admin":
            if not self.document:
                raise ValueError("CPF é obrigatório para administradores.")
            clean = "".join(filter(str.isdigit, self.document))
            if len(clean) != 11:
                raise ValueError("CPF deve ter 11 números.")
        return self


class UserRead(Timestamped):
    name: str
    email: EmailStr
    role: str
    school_id: UUID | None
    is_active: bool
    document: str | None
    first_access_completed: bool
    lgpd_accepted: bool
    lgpd_accepted_at: datetime | None


class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    email: EmailStr
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: str = Field(pattern="^(admin|school_admin|teacher|guardian)$")
    school_id: UUID | None = None
    document: str | None = Field(default=None, min_length=11, max_length=14)

    @model_validator(mode="after")
    def validate_admin_fields(self):
        if self.role == "admin":
            if not self.document:
                raise ValueError("CPF é obrigatório para administradores.")
            clean = "".join(filter(str.isdigit, self.document))
            if len(clean) != 11:
                raise ValueError("CPF deve ter 11 números.")
        return self


class UserFirstAccess(BaseModel):
    email: EmailStr
    name: str = Field(min_length=2, max_length=180)
    password: str = Field(min_length=8, max_length=128)
