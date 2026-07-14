import re
import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
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
from app.schemas.common import ActiveStatusUpdate
from app.schemas.pedagogy import (
    PedagogicalMethodologyCreate,
    PedagogicalMethodologyRead,
    PedagogicalMethodologyUpdate,
    PedagogicalMaterialCreate,
    PedagogicalMaterialRead,
    PedagogicalMaterialUpdate,
    DailySchoolRecordCreate,
    DailySchoolRecordRead,
    DailySchoolRecordUpdate,
    MaterialItemRead,
    MaterialItemCreate,
    FamilyInteractionSuggestionRead,
)
from app.services.audit import record_audit
from app.services.permissions import ensure_child_access, ensure_admin, ensure_school_staff

logger = logging.getLogger(__name__)
router = APIRouter()


import urllib.request
import urllib.error
import json


# --- ISBN LOOKUP ---
@router.get("/isbn/{isbn}", status_code=status.HTTP_200_OK)
def lookup_isbn(
    isbn: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    school_id: UUID | None = None
):
    """
    Normaliza o ISBN, consulta a API do Google Books e registra a tentativa.
    Salva o livro encontrado automaticamente no banco de dados para a escola informada.
    Caso não localize na API, faz o fallback para uma lista mockada.
    Se ainda assim não encontrar, retorna 404.
    """
    normalized_isbn = re.sub(r"[^0-9X]", "", isbn.upper())
    logger.info(f"Busca de ISBN em execucao: {normalized_isbn} pelo usuario {current_user.email}")

    # Determinar escola de destino
    target_school_id = school_id or current_user.school_id
    if not target_school_id:
        # Fallback para admins: busca a primeira escola cadastrada
        from app.models.school import School
        first_school = db.scalar(select(School))
        if first_school:
            target_school_id = first_school.id

    if not target_school_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nenhuma escola cadastrada ou vinculada encontrada para associar o livro."
        )

    # 1. Consulta à API nacional do BrasilAPI (Excelente para acervo brasileiro da CBL)
    resolved_data = None
    try:
        url = f"https://brasilapi.com.br/api/isbn/v1/{normalized_isbn}"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "PaiMaeIntegrado-PedagogyApp/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            title = res_data.get("title", "")
            authors = res_data.get("authors", [])
            author = ", ".join(authors) if authors else "Autor Desconhecido"
            
            subjects = res_data.get("subjects", [])
            subject = subjects[0] if subjects else "Geral"
            
            synopsis = res_data.get("synopsis", "")
            objectives = synopsis[:300] + "..." if synopsis and len(synopsis) > 300 else (synopsis or "Objetivos pedagógicos a serem definidos.")
            
            resolved_data = {
                "title": title,
                "author": author,
                "subject": subject,
                "pedagogical_line": "A definir pela escola",
                "objectives": objectives,
                "family_orientation": "Acompanhar leitura conjunta e revisar atividades escolares.",
            }
            logger.info(f"ISBN {normalized_isbn} resolvido com sucesso pela BrasilAPI")
    except Exception as e:
        logger.error(f"Erro ao buscar ISBN na BrasilAPI: {e}")

    # 2. Consulta à API externa da Open Library (Se BrasilAPI falhou ou não encontrou)
    if not resolved_data:
        try:
            url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{normalized_isbn}&format=json&jscmd=data"
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "PaiMaeIntegrado-PedagogyApp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode())
                key = f"ISBN:{normalized_isbn}"
                if key in res_data:
                    book_info = res_data[key]
                    title = book_info.get("title", "")
                    authors_list = book_info.get("authors", [])
                    author = ", ".join([a.get("name", "") for a in authors_list]) if authors_list else "Autor Desconhecido"
                    
                    # Assunto derivado de subjects
                    subjects = book_info.get("subjects", [])
                    subject = subjects[0].get("name", "Geral") if subjects else "Geral"
                    
                    # Descrição / notas
                    notes = book_info.get("notes", "")
                    objectives = notes[:300] + "..." if len(notes) > 300 else notes
                    
                    resolved_data = {
                        "title": title,
                        "author": author,
                        "subject": subject,
                        "pedagogical_line": "A definir pela school",
                        "objectives": objectives or "Objetivos pedagógicos a serem definidos.",
                        "family_orientation": "Acompanhar leitura conjunta e revisar atividades escolares.",
                    }
        except Exception as e:
            logger.error(f"Erro ao buscar ISBN no Open Library: {e}")

    # 2. Fallback para Google Books se Open Library falhou ou não encontrou
    if not resolved_data:
        try:
            url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{normalized_isbn}"
            req = urllib.request.Request(
                url, 
                headers={"User-Agent": "PaiMaeIntegrado-PedagogyApp/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode())
                if res_data.get("totalItems", 0) > 0:
                    volume_info = res_data["items"][0]["volumeInfo"]
                    
                    title = volume_info.get("title", "")
                    authors = volume_info.get("authors", [])
                    author = ", ".join(authors) if authors else "Autor Desconhecido"
                    
                    # Assunto derivado de categorias
                    categories = volume_info.get("categories", [])
                    subject = categories[0] if categories else "Geral"
                    
                    # Descrição vira objetivos
                    description = volume_info.get("description", "")
                    objectives = description[:300] + "..." if len(description) > 300 else description
                    
                    resolved_data = {
                        "title": title,
                        "author": author,
                        "subject": subject,
                        "pedagogical_line": "A definir pela escola",
                        "objectives": objectives or "Objetivos pedagógicos a serem definidos.",
                        "family_orientation": "Acompanhar leitura conjunta e revisar atividades escolares.",
                    }
        except Exception as e:
            logger.error(f"Erro ao buscar ISBN no Google Books: {e}")

    # 3. Fallback para banco mockado de teste
    if not resolved_data:
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
                "family_orientation": "Estimular a criança a conta objetos e fazer divisões na hora de lanchar.",
            }
        }
        if normalized_isbn in mock_db:
            resolved_data = mock_db[normalized_isbn]

    # Se localizou de alguma forma, retorna os dados sem gravar no banco.
    # A persistencia acontece no POST /materials, apos confirmacao do usuario.
    if resolved_data:
        existing = db.scalar(
            select(PedagogicalMaterial).where(
                PedagogicalMaterial.isbn == normalized_isbn,
                PedagogicalMaterial.school_id == target_school_id,
            )
        )
        return {
            "resolved": True,
            "isbn": normalized_isbn,
            "already_registered": existing is not None,
            "data": {
                **resolved_data,
                "id": str(existing.id) if existing else None,
            },
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="ISBN não localizado na base global de livros (Open Library e Google Books). Por favor, preencha os dados do livro manualmente abaixo."
    )



# --- METHODOLOGIES ---
@router.post("/methodologies", response_model=PedagogicalMethodologyRead, status_code=status.HTTP_201_CREATED)
def create_methodology(
    payload: PedagogicalMethodologyCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
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
    # Responsáveis veem apenas metodologias ativas
    if current_user.role == "guardian":
        query = query.where(PedagogicalMethodology.is_active.is_(True))
    return list(db.scalars(query))


@router.put("/methodologies/{methodology_id}", response_model=PedagogicalMethodologyRead)
def update_methodology(
    methodology_id: UUID,
    payload: PedagogicalMethodologyUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    methodology = db.get(PedagogicalMethodology, methodology_id)
    if not methodology:
        raise HTTPException(status_code=404, detail="Metodologia não encontrada.")
    if current_user.role != "admin" and str(current_user.school_id) != str(methodology.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    methodology.name = payload.name
    methodology.description = payload.description
    record_audit(db, actor=current_user, action="pedagogy.methodology_update", entity_type="pedagogical_methodology", entity_id=methodology.id, school_id=methodology.school_id)
    db.commit()
    db.refresh(methodology)
    return methodology


@router.patch("/methodologies/{methodology_id}/status", response_model=PedagogicalMethodologyRead)
def update_methodology_status(
    methodology_id: UUID,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    methodology = db.get(PedagogicalMethodology, methodology_id)
    if not methodology:
        raise HTTPException(status_code=404, detail="Metodologia não encontrada.")
    if current_user.role != "admin" and str(current_user.school_id) != str(methodology.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    previous_status = methodology.is_active
    methodology.is_active = payload.is_active
    record_audit(db, actor=current_user, action="pedagogy.methodology_status_update", entity_type="pedagogical_methodology", entity_id=methodology.id, school_id=methodology.school_id, payload={"previous_is_active": previous_status, "is_active": methodology.is_active})
    db.commit()
    db.refresh(methodology)
    return methodology


# --- MATERIALS ---
@router.post("/materials", response_model=PedagogicalMaterialRead, status_code=status.HTTP_201_CREATED)
def create_material(
    payload: PedagogicalMaterialCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
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
    # Responsáveis veem apenas materiais ativos
    if current_user.role == "guardian":
        query = query.where(PedagogicalMaterial.is_active.is_(True))
    return list(db.scalars(query))


@router.put("/materials/{material_id}", response_model=PedagogicalMaterialRead)
def update_material(
    material_id: UUID,
    payload: PedagogicalMaterialUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    material = db.get(PedagogicalMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material didático não encontrado.")
    if current_user.role != "admin" and str(current_user.school_id) != str(material.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    material.title = payload.title
    material.author = payload.author
    material.isbn = payload.isbn
    material.subject = payload.subject
    material.pedagogical_line = payload.pedagogical_line
    material.objectives = payload.objectives
    material.family_orientation = payload.family_orientation

    # Limpa itens antigos e reinsere novos
    db.execute(delete(MaterialItem).where(MaterialItem.material_id == material.id))
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
    record_audit(db, actor=current_user, action="pedagogy.material_update", entity_type="pedagogical_material", entity_id=material.id, school_id=material.school_id)
    db.commit()
    db.refresh(material)
    return material


@router.patch("/materials/{material_id}/status", response_model=PedagogicalMaterialRead)
def update_material_status(
    material_id: UUID,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    material = db.get(PedagogicalMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material didático não encontrado.")
    if current_user.role != "admin" and str(current_user.school_id) != str(material.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    previous_status = material.is_active
    material.is_active = payload.is_active
    record_audit(db, actor=current_user, action="pedagogy.material_status_update", entity_type="pedagogical_material", entity_id=material.id, school_id=material.school_id, payload={"previous_is_active": previous_status, "is_active": material.is_active})
    db.commit()
    db.refresh(material)
    return material


@router.delete("/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    material = db.get(PedagogicalMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material didático não encontrado.")
    if current_user.role != "admin" and str(current_user.school_id) != str(material.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    db.delete(material)
    db.commit()
    return


@router.post("/materials/{material_id}/items", response_model=MaterialItemRead, status_code=status.HTTP_201_CREATED)
def create_material_item(
    material_id: UUID,
    payload: MaterialItemCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    material = db.get(PedagogicalMaterial, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material didático não encontrado.")
    if current_user.role != "admin" and str(current_user.school_id) != str(material.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    item = MaterialItem(
        material_id=material.id,
        chapter=payload.chapter,
        page=payload.page,
        theme=payload.theme,
        description=payload.description,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/materials/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material_item(
    item_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    item = db.get(MaterialItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item didático não encontrado.")
    material = db.get(PedagogicalMaterial, item.material_id)
    if current_user.role != "admin" and str(current_user.school_id) != str(material.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    db.delete(item)
    db.commit()
    return


@router.put("/materials/items/{item_id}", response_model=MaterialItemRead)
def update_material_item(
    item_id: UUID,
    payload: MaterialItemCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    item = db.get(MaterialItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item didático não encontrado.")
    material = db.get(PedagogicalMaterial, item.material_id)
    if current_user.role != "admin" and str(current_user.school_id) != str(material.school_id):
        raise HTTPException(status_code=403, detail="Sem permissão para esta escola.")

    item.chapter = payload.chapter
    item.page = payload.page
    item.theme = payload.theme
    item.description = payload.description
    db.commit()
    db.refresh(item)
    return item


# --- DAILY RECORDS ---
@router.post("/daily-records", response_model=DailySchoolRecordRead, status_code=status.HTTP_201_CREATED)
def create_daily_record(
    payload: DailySchoolRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
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
    # Responsáveis veem apenas diários ativos
    if current_user.role == "guardian":
        query = query.where(DailySchoolRecord.is_active.is_(True))
    return list(db.scalars(query))


@router.put("/daily-records/{record_id}", response_model=DailySchoolRecordRead)
def update_daily_record(
    record_id: UUID,
    payload: DailySchoolRecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    record = db.get(DailySchoolRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro diário não encontrado.")
    child = ensure_child_access(db, current_user, record.child_id)

    record.summary = payload.summary
    record.observed_skills = payload.observed_skills
    record.engagement_score = payload.engagement_score

    # Limpa sugestões antigas e reinsere novas
    db.execute(delete(FamilyInteractionSuggestion).where(FamilyInteractionSuggestion.daily_record_id == record.id))
    if payload.suggestions:
        for sug in payload.suggestions:
            suggestion = FamilyInteractionSuggestion(
                daily_record_id=record.id,
                suggestion_text=sug.suggestion_text,
            )
            db.add(suggestion)

    db.flush()
    record_audit(db, actor=current_user, action="pedagogy.daily_record_update", entity_type="daily_school_record", entity_id=record.id, school_id=child.school_id)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/daily-records/{record_id}/status", response_model=DailySchoolRecordRead)
def update_daily_record_status(
    record_id: UUID,
    payload: ActiveStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    ensure_school_staff(current_user)
    record = db.get(DailySchoolRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Registro diário não encontrado.")
    child = ensure_child_access(db, current_user, record.child_id)

    previous_status = record.is_active
    record.is_active = payload.is_active
    record_audit(db, actor=current_user, action="pedagogy.daily_record_status_update", entity_type="daily_school_record", entity_id=record.id, school_id=child.school_id, payload={"previous_is_active": previous_status, "is_active": record.is_active})
    db.commit()
    db.refresh(record)
    return record
