import re
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.pedagogy import (
    PedagogicalMethodology,
    PedagogicalMaterial,
    MaterialItem,
    DailySchoolRecord,
    FamilyInteractionSuggestion,
)
from app.models.user import User
from app.schemas.pedagogy import (
    PedagogicalMethodologyCreate,
    PedagogicalMethodologyRead,
    PedagogicalMaterialCreate,
    PedagogicalMaterialRead,
    DailySchoolRecordCreate,
    DailySchoolRecordRead,
    MaterialItemRead,
    FamilyInteractionSuggestionRead,
)
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_admin

logger = logging.getLogger(__name__)
router = APIRouter()


# --- ISBN LOOKUP ---
@router.get("/isbn/{isbn}", status_code=status.HTTP_200_OK)
def lookup_isbn(isbn: str, current_user: Annotated[User, Depends(get_current_user)]):
    """
    Normaliza o ISBN e registra a tentativa.
    Retorna metadados se for um ISBN simulado conhecido, caso contrário retorna 404
    exigindo inserção manual no frontend.
    """
    # Normalização: remove hífens, espaços e deixa em maiúsculo
    normalized_isbn = re.sub(r"[-\s]", "", isbn).upper()
    logger.info(f"Tentativa de busca de ISBN registrada: {normalized_isbn} pelo usuario {current_user.email}")

    # Mock de banco de dados externo para teste
    mock_db = {
        "9788532283215": {
            "title": "Português Compartilhado",
            "author": "Ana Silva",
            "subject": "Português",
            "pedagogical_line": "Socioconstrutivista",
            "objectives": "Desenvolver a leitura e interpretação de textos literários nacionais.",
            "family_orientation": "Acompanhar a leitura conjunta de 15 minutos à noite com o filho.",
        },
        "9788500000000": {
            "title": "Matemática Criativa v1",
            "author": "Carlos Souza",
            "subject": "Matemática",
            "pedagogical_line": "Tradicional/Cognitivista",
            "objectives": "Fixar conceitos de multiplicação e divisão através de jogos práticos.",
            "family_orientation": "Estimular a criança a contar objetos e fazer divisões na hora de lanchar.",
        }
    }

    if normalized_isbn in mock_db:
        return {
            "resolved": True,
            "isbn": normalized_isbn,
            "data": mock_db[normalized_isbn]
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ISBN não localizado na base nacional. Informe os dados manualmente."
    )


# --- METHODOLOGIES ---
@router.post("/methodologies", response_model=PedagogicalMethodologyRead, status_code=status.HTTP_201_CREATED)
def create_methodology(
    payload: PedagogicalMethodologyCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "admin" and str(current_user.school_id) != str(payload.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    methodology = PedagogicalMethodology(
        school_id=payload.school_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(methodology)
    db.flush()
    record_audit(db, actor=current_user, action="pedagogy.methodology_create", entity_type="pedagogical_methodology", entity_id=methodology.id, school_id=payload.school_id)
    db.commit()
    db.refresh(methodology)
    return methodology


@router.get("/methodologies", response_model=list[PedagogicalMethodologyRead])
def list_methodologies(
    school_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "admin" and str(current_user.school_id) != str(school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    query = select(PedagogicalMethodology).where(PedagogicalMethodology.school_id == school_id)
    return list(db.scalars(query))


# --- MATERIALS ---
@router.post("/materials", response_model=PedagogicalMaterialRead, status_code=status.HTTP_201_CREATED)
def create_material(
    payload: PedagogicalMaterialCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "admin" and str(current_user.school_id) != str(payload.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    material = PedagogicalMaterial(
        school_id=payload.school_id,
        title=payload.title,
        author=payload.author,
        isbn=payload.isbn,
        subject=payload.subject,
        pedagogical_line=payload.pedagogical_line,
        objectives=payload.objectives,
        family_orientation=payload.family_orientation,
    )
    db.add(material)
    db.flush()

    if payload.items:
        for it in payload.items:
            item = MaterialItem(
                material_id=material.id,
                chapter=it.chapter,
                page=it.page,
                theme=it.theme,
                description=it.description,
            )
            db.add(item)
        db.flush()

    record_audit(db, actor=current_user, action="pedagogy.material_create", entity_type="pedagogical_material", entity_id=material.id, school_id=payload.school_id)
    db.commit()
    db.refresh(material)
    return material


@router.get("/materials", response_model=list[PedagogicalMaterialRead])
def list_materials(
    school_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role != "admin" and str(current_user.school_id) != str(school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    query = select(PedagogicalMaterial).where(PedagogicalMaterial.school_id == school_id)
    return list(db.scalars(query))


# --- DAILY RECORDS ---
@router.post("/daily-records", response_model=DailySchoolRecordRead, status_code=status.HTTP_201_CREATED)
def create_daily_record(
    payload: DailySchoolRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    child = ensure_child_access(db, current_user, payload.child_id)

    record = DailySchoolRecord(
        child_id=payload.child_id,
        date=payload.date,
        summary=payload.summary,
        observed_skills=payload.observed_skills,
        engagement_score=payload.engagement_score,
    )
    db.add(record)
    db.flush()

    if payload.suggestions:
        for sug in payload.suggestions:
            suggestion = FamilyInteractionSuggestion(
                daily_record_id=record.id,
                suggestion_text=sug.suggestion_text,
            )
            db.add(suggestion)
        db.flush()

    record_audit(db, actor=current_user, action="pedagogy.daily_record_create", entity_type="daily_school_record", entity_id=record.id, school_id=child.school_id)
    db.commit()
    db.refresh(record)
    return record


@router.get("/daily-records", response_model=list[DailySchoolRecordRead])
def list_daily_records(
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_child_access(db, current_user, child_id)
    query = select(DailySchoolRecord).where(DailySchoolRecord.child_id == child_id).order_by(DailySchoolRecord.date.desc())
    return list(db.scalars(query))
