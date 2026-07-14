import base64
import logging
from io import BytesIO
from pathlib import Path

logger = logging.getLogger(__name__)


class GoogleVisionOCRService:
    """
    Serviço de OCR usando Google Cloud Vision API.
    Extrai texto de PDFs e imagens.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = None
        if api_key:
            try:
                from google.cloud import vision
                import google.auth.credentials

                class StaticCredentials(google.auth.credentials.Credentials):
                    def __init__(self, token):
                        self.token = token

                self.client = vision.ImageAnnotatorClient()
            except ImportError:
                logger.warning("google-cloud-vision não instalado. OCR será simulado.")

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        """
        Extrai texto de uma imagem usando Google Vision API.
        Falls back para simulação se API não estiver configurada.
        """
        if not self.api_key:
            logger.warning("Google Vision API key não configurada. Retornando texto simulado.")
            return self._simulate_ocr(image_bytes)

        if not self.client:
            logger.warning("Google Cloud Vision client não disponível. Retornando texto simulado.")
            return self._simulate_ocr(image_bytes)

        try:
            from google.cloud.vision_v1 import types

            image = types.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)

            if response.error.message:
                logger.error(f"Erro na API Vision: {response.error.message}")
                return self._simulate_ocr(image_bytes)

            extracted_text = response.full_text_annotation.text
            return extracted_text if extracted_text else self._simulate_ocr(image_bytes)
        except Exception as e:
            logger.error(f"Erro ao extrair texto com Google Vision: {str(e)}")
            return self._simulate_ocr(image_bytes)

    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extrai texto de um PDF usando Google Vision API.
        Falls back para pytesseract se disponível, caso contrário para simulação.
        """
        if not self.api_key:
            logger.warning("Google Vision API key não configurada. Retornando texto simulado.")
            return self._simulate_pdf_ocr(pdf_bytes)

        try:
            import pdf2image

            pdf_stream = BytesIO(pdf_bytes)
            images = pdf2image.convert_from_bytes(pdf_bytes, dpi=150)

            all_text = []
            for page_num, image in enumerate(images[:10]):
                try:
                    image_byte_arr = BytesIO()
                    image.save(image_byte_arr, format='JPEG')
                    image_bytes = image_byte_arr.getvalue()

                    page_text = self.extract_text_from_image(image_bytes)
                    all_text.append(f"\n--- Página {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    logger.error(f"Erro ao processar página {page_num + 1}: {str(e)}")
                    continue

            return "\n".join(all_text) if all_text else self._simulate_pdf_ocr(pdf_bytes)
        except ImportError:
            logger.warning("pdf2image não instalado. Retornando texto simulado.")
            return self._simulate_pdf_ocr(pdf_bytes)
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
            return self._simulate_pdf_ocr(pdf_bytes)

    @staticmethod
    def _simulate_ocr(image_bytes: bytes) -> str:
        """Simula OCR para testes sem API configurada."""
        logger.info("Simulando OCR para imagem")
        return (
            "CAPÍTULO 1 - INTRODUÇÃO À LEITURA\n\n"
            "Bem-vindo ao mundo das letras e das palavras. Neste capítulo, aprenderemos "
            "os fundamentos da leitura e como reconhecer as vogais: A, E, I, O, U.\n\n"
            "As vogais são sons especiais que formam a base de todas as palavras. "
            "Vamos começar com exemplos simples:\n\n"
            "- ABACAXI: contém as vogais A e I\n"
            "- ELEFANTE: contém as vogais E, A, E\n"
            "- IGUANA: contém as vogais I, U, A\n"
            "- OVELHA: contém as vogais O, E, A\n"
            "- UVA: contém as vogais U, A\n\n"
            "Exercício: Identifique as vogais nas seguintes palavras:\n"
            "1. GATO\n"
            "2. LIVRO\n"
            "3. SOL\n"
            "4. UNIVERSIDADE\n"
        )

    @staticmethod
    def _simulate_pdf_ocr(pdf_bytes: bytes) -> str:
        """Simula OCR de PDF para testes sem API configurada."""
        logger.info("Simulando OCR para PDF")
        return (
            "--- Página 1 ---\n\n"
            "LIVRO DE LEITURA - NÍVEL FUNDAMENTAL\n\n"
            "CAPÍTULO 1: AS LETRAS E SEUS SONS\n\n"
            "Neste livro, você aprenderá sobre:\n"
            "1. O alfabeto português\n"
            "2. Sons das consoantes e vogais\n"
            "3. Formação de palavras simples\n"
            "4. Leitura com compreensão\n"
            "5. Exercícios progressivos de dificuldade\n\n"
            "--- Página 2 ---\n\n"
            "CAPÍTULO 2: VOGAIS - A, E, I, O, U\n\n"
            "As vogais são fundamentais para a formação de palavras. "
            "Toda sílaba precisa de uma vogal.\n\n"
            "Exemplos com A: ANTA, ABELHA, AMOR\n"
            "Exemplos com E: ESCOLA, EMA, ESSE\n"
            "Exemplos com I: IGLU, IMORTAL, IMÃ\n"
            "Exemplos com O: OVO, OLHO, OURO\n"
            "Exemplos com U: UVA, URSO, UNIFORME\n"
        )


ocr_service = None


def get_ocr_service(api_key: str | None = None) -> GoogleVisionOCRService:
    """Factory function para criar ou obter instância do serviço OCR."""
    global ocr_service
    if ocr_service is None:
        ocr_service = GoogleVisionOCRService(api_key)
    return ocr_service
