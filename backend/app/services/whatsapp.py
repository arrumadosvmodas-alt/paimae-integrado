"""Serviço de integração com WhatsApp Business API."""
import os
import httpx
import logging
from typing import Optional
import hashlib
import hmac

logger = logging.getLogger(__name__)


class WhatsAppBusinessService:
    """Serviço para integração com WhatsApp Business."""

    def __init__(self):
        self.base_url = "https://graph.instagram.com/v18.0"
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.webhook_verify_token = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN")

    async def send_message(
        self, phone_number: str, message: str, message_type: str = "text"
    ) -> bool:
        """Envia mensagem WhatsApp."""
        if not self.phone_number_id or not self.access_token:
            logger.warning("WhatsApp não configurado")
            return False

        try:
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number.replace("+", "").replace("-", "").replace(" ", ""),
                "type": message_type,
            }

            if message_type == "text":
                payload["text"] = {"body": message}
            elif message_type == "template":
                payload["template"] = message

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.phone_number_id}/messages",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )

                if response.status_code == 200:
                    logger.info(f"Mensagem enviada para {phone_number}")
                    return True
                else:
                    logger.error(f"Erro ao enviar mensagem: {response.text}")
                    return False
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {e}")
            return False

    async def send_notification(
        self,
        phone_number: str,
        child_name: str,
        notification_type: str,
        data: dict,
    ) -> bool:
        """Envia notificação formatada via WhatsApp."""
        messages = {
            "grade_update": f"Atualização de Nota\n\n{child_name} recebeu uma nova nota: {data.get('grade')} em {data.get('subject')}",
            "assignment": f"Nova Atividade\n\n{data.get('title')}\nVencimento: {data.get('due_date')}",
            "interaction": f"Interação Aguardando Resposta\n\n{data.get('message')}",
            "alert": f"Alerta Importante\n\n{data.get('alert_message')}",
        }

        message = messages.get(notification_type, "Nova notificação")
        return await self.send_message(phone_number, message)

    async def mark_as_read(self, message_id: str) -> bool:
        """Marca mensagem como lida."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{self.phone_number_id}/messages",
                    json={
                        "messaging_product": "whatsapp",
                        "status": "read",
                        "message_id": message_id,
                    },
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao marcar como lida: {e}")
            return False

    def verify_webhook(self, token: str) -> bool:
        """Verifica token de webhook."""
        return token == self.webhook_verify_token

    def verify_webhook_signature(self, body: str, signature: str) -> bool:
        """Verifica assinatura da webhook."""
        if not self.webhook_verify_token:
            return False

        expected_signature = hmac.new(
            self.webhook_verify_token.encode(),
            body.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    async def get_media_url(self, media_id: str) -> Optional[str]:
        """Obtém URL de um arquivo de mídia."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/{media_id}",
                    params={"fields": "url"},
                    headers={"Authorization": f"Bearer {self.access_token}"},
                )
                data = response.json()
                return data.get("url")
        except Exception as e:
            logger.error(f"Erro ao obter URL de mídia: {e}")
            return None

    async def handle_incoming_message(self, webhook_data: dict) -> dict:
        """Processa mensagem recebida via webhook."""
        try:
            messages = webhook_data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("messages", [])

            if not messages:
                return {"status": "no_messages"}

            message = messages[0]
            return {
                "status": "success",
                "message_id": message.get("id"),
                "from": message.get("from"),
                "timestamp": message.get("timestamp"),
                "type": message.get("type"),
                "text": message.get("text", {}).get("body") if message.get("type") == "text" else None,
            }
        except Exception as e:
            logger.error(f"Erro ao processar mensagem recebida: {e}")
            return {"status": "error", "error": str(e)}
