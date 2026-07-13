from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


# --- METODOLOGIA ---
class PedagogicalMethodologyCreate(BaseModel):
    school_id: UUID
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


class PedagogicalMethodologyRead(Timestamped):
    school_id: UUID
    name: str
    description: str | None
    is_active: bool


class PedagogicalMethodologyUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = None


# --- ITENS DO MATERIAL ---
class MaterialItemCreate(BaseModel):
    chapter: str | None = Field(default=None, max_length=50)
    page: str | None = Field(default=None, max_length=20)
    theme: str = Field(min_length=2, max_length=180)
    description: str | None = None


class MaterialItemRead(Timestamped):
    material_id: UUID
    chapter: str | None
    page: str | None
    theme: str
    description: str | None


# --- MATERIAL DIDÁTICO ---
class PedagogicalMaterialCreate(BaseModel):
    school_id: UUID
    title: str = Field(min_length=2, max_length=180)
    author: str | None = Field(default=None, max_length=100)
    isbn: str | None = Field(default=None, max_length=20)
    subject: str = Field(min_length=2, max_length=80)
    pedagogical_line: str = Field(min_length=2, max_length=100)
    objectives: str | None = None
    family_orientation: str | None = None
    items: list[MaterialItemCreate] | None = None


class PedagogicalMaterialRead(Timestamped):
    school_id: UUID
    title: str
    author: str | None
    isbn: str | None
    subject: str
    pedagogical_line: str
    objectives: str | None
    family_orientation: str | None
    items: list[MaterialItemRead]
    is_active: bool


class PedagogicalMaterialUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    author: str | None = Field(default=None, max_length=100)
    isbn: str | None = Field(default=None, max_length=20)
    subject: str = Field(min_length=2, max_length=80)
    pedagogical_line: str = Field(min_length=2, max_length=100)
    objectives: str | None = None
    family_orientation: str | None = None
    items: list[MaterialItemCreate] | None = None


# --- INTERAÇÃO FAMILIAR ---
class FamilyInteractionSuggestionCreate(BaseModel):
    suggestion_text: str


class FamilyInteractionSuggestionRead(Timestamped):
    daily_record_id: UUID
    suggestion_text: str


# --- DIÁRIO ESCOLAR ---
class DailySchoolRecordCreate(BaseModel):
    child_id: UUID
    date: date
    summary: str = Field(min_length=5)
    observed_skills: str | None = None
    engagement_score: int | None = Field(default=None, ge=1, le=5)
    suggestions: list[FamilyInteractionSuggestionCreate] | None = None


class DailySchoolRecordRead(Timestamped):
    child_id: UUID
    date: date
    summary: str
    observed_skills: str | None
    engagement_score: int | None
    suggestions: list[FamilyInteractionSuggestionRead]
    is_active: bool


class DailySchoolRecordUpdate(BaseModel):
    summary: str = Field(min_length=5)
    observed_skills: str | None = None
    engagement_score: int | None = Field(default=None, ge=1, le=5)
    suggestions: list[FamilyInteractionSuggestionCreate] | None = None
