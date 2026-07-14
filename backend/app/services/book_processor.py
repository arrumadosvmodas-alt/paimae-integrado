import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.pedagogy import PedagogicalMaterial
from app.services.ocr import get_ocr_service
from app.services.llm import get_llm_service
from app.services.storage import storage_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class BookProcessorService:
    """
    Serviço orquestrador que coordena:
    1. Upload do arquivo
    2. Extração de texto (OCR)
    3. Análise com IA (LLM)
    4. Armazenamento dos resultados
    """

    def __init__(self):
        self.ocr_service = get_ocr_service(settings.google_vision_api_key)
        self.llm_service = get_llm_service(settings.google_gemini_api_key)

    def process_book_file(
        self,
        db: Session,
        material_id: str,
        file_bytes: bytes,
        file_name: str,
        is_pdf: bool = False,
    ) -> dict[str, Any]:
        """
        Processa um arquivo de livro (PDF ou imagem) de ponta a ponta.

        Passos:
        1. Faz upload do arquivo para Supabase Storage
        2. Extrai texto via OCR
        3. Analisa conteúdo com Gemini LLM
        4. Gera plano de estudos básico
        5. Atualiza o modelo PedagogicalMaterial no DB
        """
        material = db.query(PedagogicalMaterial).filter_by(id=material_id).first()
        if not material:
            return {
                "status": "error",
                "message": "Material pedagógico não encontrado",
            }

        try:
            # Step 1: Upload do arquivo
            logger.info(f"[1/4] Iniciando upload do arquivo: {file_name}")
            material.processing_status = "processing"
            material.processing_error = None
            db.commit()

            file_url = storage_service.upload_file(file_bytes, file_name, "application/pdf" if is_pdf else "image/jpeg")
            if not file_url:
                raise Exception("Falha ao fazer upload para Supabase Storage")

            material.file_url = file_url
            db.commit()

            # Step 2: Extração de texto (OCR)
            logger.info(f"[2/4] Executando OCR no arquivo")
            if is_pdf:
                extracted_text = self.ocr_service.extract_text_from_pdf(file_bytes)
            else:
                extracted_text = self.ocr_service.extract_text_from_image(file_bytes)

            if not extracted_text:
                raise Exception("OCR retornou texto vazio")

            material.extracted_text = extracted_text
            db.commit()

            # Step 3: Análise com LLM
            logger.info(f"[3/4] Analisando conteúdo com IA (Gemini)")
            ai_analysis = self.llm_service.analyze_book_content(
                title=material.title,
                author=material.author or "Desconhecido",
                extracted_text=extracted_text,
            )

            material.ai_analysis = ai_analysis
            db.commit()

            # Step 4: Marcar como processado com sucesso
            logger.info(f"[4/4] Finalizando processamento")
            material.processing_status = "completed"
            db.commit()

            logger.info(f"✅ Livro processado com sucesso: {material.title}")

            return {
                "status": "success",
                "message": "Livro processado com sucesso",
                "material_id": str(material.id),
                "file_url": file_url,
                "extracted_pages": len(extracted_text) // 500,  # Aproximação
                "ai_analysis": ai_analysis,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao processar livro: {str(e)}")
            material.processing_status = "failed"
            material.processing_error = str(e)
            db.commit()

            return {
                "status": "error",
                "message": f"Erro ao processar livro: {str(e)}",
                "material_id": str(material.id),
            }

    def generate_study_plan_for_child(
        self,
        db: Session,
        material_id: str,
        child_id: str,
        child_grade: str | None = None,
        child_preferences: dict | None = None,
    ) -> dict[str, Any]:
        """
        Gera plano de estudos personalizado para uma criança.
        """
        material = db.query(PedagogicalMaterial).filter_by(id=material_id).first()
        if not material:
            return {"status": "error", "message": "Material não encontrado"}

        if not material.ai_analysis:
            return {"status": "error", "message": "Material ainda não foi analisado pela IA"}

        try:
            from app.models.child import Child

            child = db.query(Child).filter_by(id=child_id).first()
            if not child:
                return {"status": "error", "message": "Criança não encontrada"}

            grade = child_grade or child.grade or "Fundamental 1"
            preferences = child_preferences or child.preferences or {}

            study_plan_text = self.llm_service.generate_study_plan(
                book_analysis=material.ai_analysis,
                child_grade=grade,
                child_preferences=preferences,
            )

            logger.info(f"✅ Plano de estudos gerado para criança: {child.full_name}")

            return {
                "status": "success",
                "message": "Plano de estudos gerado com sucesso",
                "child_id": str(child_id),
                "material_id": str(material_id),
                "study_plan": study_plan_text,
            }
        except Exception as e:
            logger.error(f"❌ Erro ao gerar plano de estudos: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao gerar plano: {str(e)}",
            }

    def generate_interaction_for_child(
        self,
        db: Session,
        material_id: str,
        child_id: str,
        chapter: str,
        theme: str,
        recipient_type: str = "child",
    ) -> dict[str, Any]:
        """
        Gera interação personalizada (para criança ou pais).
        """
        try:
            from app.models.child import Child

            child = db.query(Child).filter_by(id=child_id).first()
            if not child:
                return {"status": "error", "message": "Criança não encontrada"}

            interaction_text = self.llm_service.generate_daily_interaction(
                child_name=child.full_name,
                chapter=chapter,
                theme=theme,
                recipient_type=recipient_type,
            )

            logger.info(f"✅ Interação gerada para {recipient_type}: {child.full_name}")

            return {
                "status": "success",
                "message": f"Interação gerada com sucesso para {recipient_type}",
                "child_id": str(child_id),
                "recipient_type": recipient_type,
                "interaction": interaction_text,
            }
        except Exception as e:
            logger.error(f"❌ Erro ao gerar interação: {str(e)}")
            return {
                "status": "error",
                "message": f"Erro ao gerar interação: {str(e)}",
            }


book_processor_service = BookProcessorService()
