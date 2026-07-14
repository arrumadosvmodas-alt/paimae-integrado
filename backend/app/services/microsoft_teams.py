"""Serviço de integração com Microsoft Teams."""
import os
import httpx
import logging
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class MicrosoftTeamsService:
    """Serviço para integração com Microsoft Teams."""

    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.client_id = os.getenv("MICROSOFT_TEAMS_CLIENT_ID")
        self.client_secret = os.getenv("MICROSOFT_TEAMS_CLIENT_SECRET")
        self.tenant_id = os.getenv("MICROSOFT_TEAMS_TENANT_ID")
        self.access_token = None

    async def _get_access_token(self) -> str:
        """Obtém token de acesso do Microsoft Graph."""
        if self.access_token:
            return self.access_token

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "scope": "https://graph.microsoft.com/.default",
                        "grant_type": "client_credentials",
                    },
                )
                data = response.json()
                self.access_token = data["access_token"]
                return self.access_token
        except Exception as e:
            logger.error(f"Erro ao obter token Microsoft Teams: {e}")
            raise

    async def get_teams(self, user_id: str) -> List[dict]:
        """Obtém lista de times do usuário."""
        try:
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.base_url}/me/joinedTeams",
                    headers=headers,
                )
                data = response.json()
                return data.get("value", [])
        except Exception as e:
            logger.error(f"Erro ao obter times: {e}")
            return []

    async def get_channels(self, team_id: str) -> List[dict]:
        """Obtém canais de um time."""
        try:
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.base_url}/teams/{team_id}/channels",
                    headers=headers,
                )
                data = response.json()
                return data.get("value", [])
        except Exception as e:
            logger.error(f"Erro ao obter canais: {e}")
            return []

    async def send_message(
        self, team_id: str, channel_id: str, message: str
    ) -> bool:
        """Envia mensagem para um canal."""
        try:
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                payload = {
                    "body": {
                        "contentType": "html",
                        "content": message,
                    }
                }
                response = await client.post(
                    f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages",
                    headers=headers,
                    json=payload,
                )
                return response.status_code == 201
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem Teams: {e}")
            return False

    async def get_assignments(self, team_id: str, channel_id: str) -> List[dict]:
        """Obtém tarefas de um canal."""
        try:
            token = await self._get_access_token()
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {token}"}
                response = await client.get(
                    f"{self.base_url}/teams/{team_id}/channels/{channel_id}/messages",
                    headers=headers,
                )
                data = response.json()
                messages = data.get("value", [])

                # Filtrar apenas mensagens com tarefas
                assignments = [
                    msg for msg in messages if "assignment" in msg.get("subject", "").lower()
                ]
                return assignments
        except Exception as e:
            logger.error(f"Erro ao obter tarefas: {e}")
            return []

    async def sync_team_data(self, team_id: str, channel_id: str, school_id: str) -> dict:
        """Sincroniza dados de um time/canal."""
        try:
            assignments = await self.get_assignments(team_id, channel_id)

            # Aqui você criaria os registros no banco de dados
            # create_study_plans_from_assignments(assignments, school_id)

            return {
                "status": "success",
                "records_synced": len(assignments),
            }
        except Exception as e:
            logger.error(f"Erro ao sincronizar Teams: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
