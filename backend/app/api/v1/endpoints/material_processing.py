import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.pedagogy import PedagogicalMaterial
from app.models.user import User
from app.schemas.common import Timestamped
from app.services.audit import record_audit
from app.services.book_processor import book_processor_service
from app.services.permissions import ensure_school_access
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class ProcessingStatusResponse(BaseModel):
    material_id: UUID
    status: str
    processing_status: str
    file_url: str | None
    error: str | None
    ai_analysis: dict | None


class StudyPlanResponse(BaseModel):
    status: str
    message: str
    study_plan: str | None = None


class InteractionResponse(BaseModel):
    status: str
    message: str
    interaction: str | None = None


@router.post("/materials/{material_id}/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_book_file(
    material_id: UUID,
    file: UploadFile = File(...),
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Upload um arquivo de livro (PDF ou imagem) para processamento automático.

    O arquivo será:
    1. Enviado para Supabase Storage
    2. Processado com OCR (extração de texto)
    3. Analisado com IA (Gemini) para estrutura pedagógica

    A resposta é imediata (202 Accepted), e o processamento acontece em background.
    """
    material = db.scalar(select(PedagogicalMaterial).where(PedagogicalMaterial.id == material_id))
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")

    ensure_school_access(current_user, material.school_id)

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo sem nome")

    # Validar tipo de arquivo
    allowed_types = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de arquivo não permitido. Use: PDF, JPEG, PNG, WEBP. Recebido: {file.content_type}",
        )

    try:
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio")

        if len(file_bytes) > 50 * 1024 * 1024:  # 50 MB
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Arquivo muito grande")

        is_pdf = file.content_type == "application/pdf"
        result = book_processor_service.process_book_file(
            db=db,
            material_id=material_id,
            file_bytes=file_bytes,
            file_name=f"books/{material.school_id}/{material_id}/{file.filename}",
            is_pdf=is_pdf,
        )

        record_audit(
            db,
            actor=current_user,
            action="material.upload_file",
            entity_type="pedagogical_material",
            entity_id=material.id,
            school_id=material.school_id,
        )

        return {
            "status": "processing_initiated",
            "message": "Arquivo recebido. Processamento em andamento...",
            "material_id": str(material_id),
            "details": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao fazer upload do arquivo: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/materials/{material_id}/processing-status", response_model=ProcessingStatusResponse)
def get_processing_status(
    material_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Obtém o status de processamento de um livro.
    """
    material = db.scalar(select(PedagogicalMaterial).where(PedagogicalMaterial.id == material_id))
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")

    ensure_school_access(current_user, material.school_id)

    return ProcessingStatusResponse(
        material_id=material.id,
        status="ok",
        processing_status=material.processing_status,
        file_url=material.file_url,
        error=material.processing_error,
        ai_analysis=material.ai_analysis,
    )


@router.post("/materials/{material_id}/generate-study-plan", response_model=StudyPlanResponse)
def generate_study_plan(
    material_id: UUID,
    child_id: UUID,
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Gera um plano de estudos personalizado para uma criança,
    baseado na análise IA do livro.

    Pré-requisito: O livro deve ter sido processado (status: 'completed').
    """
    material = db.scalar(select(PedagogicalMaterial).where(PedagogicalMaterial.id == material_id))
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")

    ensure_school_access(current_user, material.school_id)

    if material.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Material ainda não foi processado. Status: {material.processing_status}",
        )

    result = book_processor_service.generate_study_plan_for_child(
        db=db,
        material_id=material_id,
        child_id=child_id,
    )

    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])

    record_audit(
        db,
        actor=current_user,
        action="study_plan.generate",
        entity_type="pedagogical_material",
        entity_id=material.id,
        school_id=material.school_id,
    )

    return StudyPlanResponse(
        status=result["status"],
        message=result["message"],
        study_plan=result.get("study_plan"),
    )


@router.post("/materials/{material_id}/generate-interaction", response_model=InteractionResponse)
def generate_interaction(
    material_id: UUID,
    child_id: UUID,
    chapter: str,
    theme: str,
    recipient_type: str = "child",
    db: Annotated[Session, Depends(get_db)] = None,
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    """
    Gera uma interação personalizada (para criança ou pais).

    Pré-requisito: O livro deve ter sido processado (status: 'completed').
    """
    if recipient_type not in ("child", "parent"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="recipient_type deve ser 'child' ou 'parent'",
        )

    material = db.scalar(select(PedagogicalMaterial).where(PedagogicalMaterial.id == material_id))
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")

    ensure_school_access(current_user, material.school_id)

    if material.processing_status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Material ainda não foi processado. Status: {material.processing_status}",
        )

    result = book_processor_service.generate_interaction_for_child(
        db=db,
        material_id=material_id,
        child_id=child_id,
        chapter=chapter,
        theme=theme,
        recipient_type=recipient_type,
    )

    if result["status"] == "error":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"])

    record_audit(
        db,
        actor=current_user,
        action="interaction.generate",
        entity_type="pedagogical_material",
        entity_id=material.id,
        school_id=material.school_id,
    )

    return InteractionResponse(
        status=result["status"],
        message=result["message"],
        interaction=result.get("interaction"),
    )
