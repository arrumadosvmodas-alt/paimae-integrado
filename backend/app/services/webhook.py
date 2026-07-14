"""Serviço de Webhooks customizados."""
import httpx
import logging
import json
import hmac
import hashlib
from datetime import datetime
from typing import List, Optional
import asyncio

logger = logging.getLogger(__name__)


class WebhookService:
    """Serviço para gerenciar webhooks customizados."""

    def __init__(self):
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 5

    async def send_event(
        self,
        subscriptions: List[dict],
        event_type: str,
        payload: dict,
        event_filters: Optional[dict] = None,
    ) -> dict:
        """Envia evento para todos os webhooks subscritos."""
        results = {
            "total": len(subscriptions),
            "sent": 0,
            "failed": 0,
            "failures": [],
        }

        for subscription in subscriptions:
            # Verificar filtros
            if subscription.get("filters") and not self._match_filters(
                payload, subscription["filters"]
            ):
                continue

            # Verificar se o evento está inscrito
            if event_type not in subscription.get("events", []):
                continue

            success = await self._deliver_webhook(
                subscription["url"],
                subscription["secret"],
                event_type,
                payload,
            )

            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
                results["failures"].append(
                    {
                        "url": subscription["url"],
                        "event": event_type,
                    }
                )

        return results

    async def _deliver_webhook(
        self,
        url: str,
        secret: str,
        event_type: str,
        payload: dict,
        retry_count: int = 0,
    ) -> bool:
        """Entrega webhook com retry automático."""
        try:
            # Preparar payload
            webhook_payload = {
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": payload,
            }

            # Gerar assinatura
            payload_json = json.dumps(webhook_payload, sort_keys=True)
            signature = self._generate_signature(payload_json, secret)

            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Event": event_type,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=webhook_payload, headers=headers)

                if response.status_code in [200, 201, 202]:
                    logger.info(f"Webhook enviado para {url}: {event_type}")
                    return True
                else:
                    logger.warning(
                        f"Webhook falhou {url}: {response.status_code} - {response.text}"
                    )

                    # Retry
                    if retry_count < self.max_retries:
                        await asyncio.sleep(self.retry_delay)
                        return await self._deliver_webhook(
                            url, secret, event_type, payload, retry_count + 1
                        )

                    return False

        except Exception as e:
            logger.error(f"Erro ao enviar webhook para {url}: {e}")

            # Retry
            if retry_count < self.max_retries:
                await asyncio.sleep(self.retry_delay)
                return await self._deliver_webhook(
                    url, secret, event_type, payload, retry_count + 1
                )

            return False

    def _generate_signature(self, payload: str, secret: str) -> str:
        """Gera assinatura HMAC para webhook."""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify_webhook_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verifica assinatura recebida."""
        expected = self._generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected)

    def _match_filters(self, payload: dict, filters: dict) -> bool:
        """Verifica se payload corresponde aos filtros."""
        for key, value in filters.items():
            if key not in payload:
                return False

            payload_value = payload[key]

            # Suportar múltiplos valores
            if isinstance(value, list):
                if payload_value not in value:
                    return False
            else:
                if payload_value != value:
                    return False

        return True

    async def test_webhook(self, url: str, secret: str) -> dict:
        """Testa um webhook com payload de teste."""
        test_payload = {
            "event": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"test": True},
        }

        success = await self._deliver_webhook(url, secret, "test", test_payload["data"])

        return {
            "url": url,
            "success": success,
            "tested_at": datetime.utcnow().isoformat(),
        }


# Eventos que podem ser disparados
WEBHOOK_EVENTS = {
    "assignment.created": "Nova atividade criada",
    "assignment.updated": "Atividade atualizada",
    "assignment.deleted": "Atividade deletada",
    "grade.created": "Nova nota registrada",
    "grade.updated": "Nota atualizada",
    "interaction.created": "Nova interação criada",
    "interaction.responded": "Interação respondida",
    "student.enrolled": "Aluno inscrito",
    "student.unenrolled": "Aluno removido",
    "notification.sent": "Notificação enviada",
}
