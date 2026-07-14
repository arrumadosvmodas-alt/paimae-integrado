"""Serviço de integração com Google Classroom."""
import os
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.auth.exceptions import GoogleAuthError
import httpx
import logging

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me.readonly",
    "https://www.googleapis.com/auth/classroom.grades",
]


class GoogleClassroomService:
    """Serviço para integração com Google Classroom."""

    def __init__(self):
        self.base_url = "https://classroom.googleapis.com/v1"
        self.credentials = None
        self._init_credentials()

    def _init_credentials(self):
        """Inicializa credenciais do Google."""
        try:
            credentials_path = os.getenv("GOOGLE_CLASSROOM_CREDENTIALS_PATH")
            if not credentials_path:
                logger.warning("Google Classroom credentials não configuradas")
                return

            self.credentials = Credentials.from_service_account_file(
                credentials_path, scopes=SCOPES
            )
        except Exception as e:
            logger.error(f"Erro ao carregar credenciais Google: {e}")

    async def get_courses(self, teacher_email: str) -> List[dict]:
        """Obtém lista de cursos do professor."""
        if not self.credentials:
            return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self._get_access_token()}"}
                response = await client.get(
                    f"{self.base_url}/courses",
                    headers=headers,
                )
                data = response.json()
                return data.get("courses", [])
        except Exception as e:
            logger.error(f"Erro ao obter cursos Google Classroom: {e}")
            return []

    async def get_assignments(self, course_id: str) -> List[dict]:
        """Obtém atividades de um curso."""
        if not self.credentials:
            return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self._get_access_token()}"}
                response = await client.get(
                    f"{self.base_url}/courses/{course_id}/courseWork",
                    headers=headers,
                )
                data = response.json()
                return data.get("courseWork", [])
        except Exception as e:
            logger.error(f"Erro ao obter atividades: {e}")
            return []

    async def get_grades(self, course_id: str, user_id: str) -> Optional[dict]:
        """Obtém notas de um aluno."""
        if not self.credentials:
            return None

        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {self._get_access_token()}"}
                response = await client.get(
                    f"{self.base_url}/courses/{course_id}/courseWork/studentSubmissions",
                    headers=headers,
                    params={"userId": user_id},
                )
                return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter notas: {e}")
            return None

    def _get_access_token(self) -> str:
        """Obtém token de acesso válido."""
        if not self.credentials:
            raise GoogleAuthError("Credenciais não inicializadas")

        request = Request()
        self.credentials.refresh(request)
        return self.credentials.token

    async def sync_classroom_data(self, course_id: str, school_id: str) -> dict:
        """Sincroniza dados de um classroom."""
        try:
            assignments = await self.get_assignments(course_id)

            # Aqui você criaria os registros no banco de dados
            # create_study_plans_from_assignments(assignments, school_id)

            return {
                "status": "success",
                "records_synced": len(assignments),
            }
        except Exception as e:
            logger.error(f"Erro ao sincronizar classroom: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
