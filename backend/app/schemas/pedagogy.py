from __future__ import annotations
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
    file_url: str | None = Field(default=None, max_length=500)
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
    file_url: str | None
    extracted_text: str | None
    ai_analysis: dict | None
    processing_status: str
    processing_error: str | None
    items: list[MaterialItemRead]
    index_entries: list[MaterialIndexEntryRead]
    is_active: bool


class PedagogicalMaterialUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    author: str | None = Field(default=None, max_length=100)
    isbn: str | None = Field(default=None, max_length=20)
    subject: str = Field(min_length=2, max_length=80)
    pedagogical_line: str = Field(min_length=2, max_length=100)
    objectives: str | None = None
    family_orientation: str | None = None
    file_url: str | None = Field(default=None, max_length=500)
    items: list[MaterialItemCreate] | None = None



# --- INDICE DO MATERIAL ---
class MaterialIndexEntryCreate(BaseModel):
    source_type: str = Field(default="book", pattern="^(book|pdf|image|ocr|manual)$")
    chapter: str | None = Field(default=None, max_length=80)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    theme: str = Field(min_length=2, max_length=180)
    skills: dict | None = None
    extracted_text: str | None = None
    ai_summary: str | None = None
    review_status: str = Field(default="pending", pattern="^(pending|reviewed|rejected)$")


class MaterialIndexEntryRead(Timestamped):
    material_id: UUID
    source_type: str
    chapter: str | None
    page_start: int | None
    page_end: int | None
    theme: str
    skills: dict | None
    extracted_text: str | None
    ai_summary: str | None
    review_status: str
    is_active: bool


# --- CRONOGRAMA ESCOLAR ---
class SchoolScheduleCreate(BaseModel):
    child_id: UUID
    school_id: UUID
    date: date
    subject: str = Field(min_length=2, max_length=80)
    topic: str | None = Field(default=None, max_length=180)
    material_id: UUID | None = None
    chapter: str | None = Field(default=None, max_length=80)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    source: str = Field(default="manual", pattern="^(manual|pdf|image|ocr|fallback)$")
    source_file_url: str | None = Field(default=None, max_length=500)
    confidence_score: int | None = Field(default=None, ge=0, le=100)
    fallback_used: bool = False
    status: str = Field(default="planned", pattern="^(planned|confirmed|completed|skipped)$")


class SchoolScheduleRead(Timestamped):
    child_id: UUID
    school_id: UUID
    date: date
    subject: str
    topic: str | None
    material_id: UUID | None
    chapter: str | None
    page_start: int | None
    page_end: int | None
    source: str
    source_file_url: str | None
    confidence_score: int | None
    fallback_used: bool
    status: str
    is_active: bool


class SchoolScheduleUpdate(BaseModel):
    date: date
    subject: str = Field(min_length=2, max_length=80)
    topic: str | None = Field(default=None, max_length=180)
    material_id: UUID | None = None
    chapter: str | None = Field(default=None, max_length=80)
    page_start: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    source: str = Field(default="manual", pattern="^(manual|pdf|image|ocr|fallback)$")
    source_file_url: str | None = Field(default=None, max_length=500)
    confidence_score: int | None = Field(default=None, ge=0, le=100)
    fallback_used: bool = False
    status: str = Field(default="planned", pattern="^(planned|confirmed|completed|skipped)$")

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
