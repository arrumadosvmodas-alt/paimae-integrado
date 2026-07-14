import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Serviço de notificações para enviar interações via múltiplos canais:
    - Email (SMTP)
    - SMS (simulado ou Twilio)
    - Push notifications (simulado ou Firebase)
    """

    def __init__(self):
        self.smtp_server = settings.smtp_server if hasattr(settings, "smtp_server") else None
        self.smtp_port = settings.smtp_port if hasattr(settings, "smtp_port") else 587
        self.smtp_username = settings.smtp_username if hasattr(settings, "smtp_username") else None
        self.smtp_password = settings.smtp_password if hasattr(settings, "smtp_password") else None
        self.from_email = settings.from_email if hasattr(settings, "from_email") else "noreply@paimae.local"

    def send_interaction(
        self,
        child_name: str,
        recipient_type: str,  # "child" ou "parent"
        message: str,
        recipient_email: Optional[str] = None,
        recipient_phone: Optional[str] = None,
    ) -> dict:
        """
        Envia uma interação via email ou SMS.
        Retorna status de sucesso/falha.
        """
        try:
            if not recipient_email and not recipient_phone:
                logger.warning(f"Nenhum canal de contato disponível para {child_name}")
                return self._simulate_send(child_name, recipient_type, message)

            results = []

            if recipient_email:
                email_result = self.send_email(
                    to_email=recipient_email,
                    child_name=child_name,
                    recipient_type=recipient_type,
                    message=message,
                )
                results.append(email_result)

            if recipient_phone:
                sms_result = self.send_sms(
                    phone_number=recipient_phone,
                    child_name=child_name,
                    recipient_type=recipient_type,
                    message=message,
                )
                results.append(sms_result)

            # Se todos os canais falharam
            if all(r["status"] == "failed" for r in results):
                return {
                    "status": "failed",
                    "message": "Falha ao enviar por todos os canais",
                    "channels": results,
                }

            # Se pelo menos um sucesso
            return {
                "status": "success",
                "message": "Interação enviada com sucesso",
                "channels": results,
            }

        except Exception as e:
            logger.error(f"Erro ao enviar interação: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
            }

    def send_email(
        self,
        to_email: str,
        child_name: str,
        recipient_type: str,
        message: str,
    ) -> dict:
        """
        Envia email com a interação.
        Suporta SMTP configurado ou fallback para simulação.
        """
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP não configurado. Simulando envio de email.")
            return self._simulate_email_send(to_email, child_name, recipient_type)

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._get_email_subject(child_name, recipient_type)
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Corpo do email em texto plano
            text_body = self._get_email_body_text(child_name, recipient_type, message)

            # Corpo do email em HTML
            html_body = self._get_email_body_html(child_name, recipient_type, message)

            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, [to_email], msg.as_string())

            logger.info(f"✅ Email enviado para {to_email}")
            return {
                "status": "success",
                "channel": "email",
                "recipient": to_email,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {str(e)}")
            return {
                "status": "failed",
                "channel": "email",
                "recipient": to_email,
                "error": str(e),
            }

    def send_sms(
        self,
        phone_number: str,
        child_name: str,
        recipient_type: str,
        message: str,
    ) -> dict:
        """
        Envia SMS com a interação.
        Simula envio (Twilio pode ser integrado depois).
        """
        try:
            logger.info(f"📱 Simulando envio de SMS para {phone_number}")

            sms_body = self._get_sms_body(child_name, recipient_type, message)

            # TODO: Integrar com Twilio API quando disponível
            # Para agora, apenas simulamos

            logger.info(f"✅ SMS simulado para {phone_number}: {sms_body[:50]}...")
            return {
                "status": "success",
                "channel": "sms",
                "recipient": phone_number,
                "message_preview": sms_body[:100],
            }

        except Exception as e:
            logger.error(f"❌ Erro ao enviar SMS: {str(e)}")
            return {
                "status": "failed",
                "channel": "sms",
                "recipient": phone_number,
                "error": str(e),
            }

    def send_push_notification(
        self,
        device_token: str,
        child_name: str,
        recipient_type: str,
        message: str,
    ) -> dict:
        """
        Envia push notification.
        Simula envio (Firebase pode ser integrado depois).
        """
        try:
            logger.info(f"🔔 Simulando push notification para device {device_token[:20]}...")

            # TODO: Integrar com Firebase Cloud Messaging
            # Para agora, apenas simulamos

            logger.info(f"✅ Push notification simulada para {device_token[:20]}...")
            return {
                "status": "success",
                "channel": "push",
                "device_token": device_token[:20] + "...",
            }

        except Exception as e:
            logger.error(f"❌ Erro ao enviar push: {str(e)}")
            return {
                "status": "failed",
                "channel": "push",
                "device_token": device_token[:20] + "...",
                "error": str(e),
            }

    @staticmethod
    def _simulate_send(child_name: str, recipient_type: str, message: str) -> dict:
        """Simula envio quando nenhum canal configurado."""
        logger.info(f"📤 Simulando envio de interação para {child_name} ({recipient_type})")
        return {
            "status": "success",
            "message": "Interação simulada (nenhum canal real configurado)",
            "simulated": True,
            "preview": message[:100],
        }

    @staticmethod
    def _simulate_email_send(email: str, child_name: str, recipient_type: str) -> dict:
        """Simula envio de email."""
        logger.info(f"📧 Email simulado para {email}")
        return {
            "status": "success",
            "channel": "email",
            "recipient": email,
            "simulated": True,
        }

    @staticmethod
    def _get_email_subject(child_name: str, recipient_type: str) -> str:
        if recipient_type == "child":
            return f"📚 Olá, {child_name}! Sua interação de hoje!"
        else:
            return f"👨‍👩‍👧 Orientação pedagógica para hoje - {child_name}"

    @staticmethod
    def _get_email_body_text(child_name: str, recipient_type: str, message: str) -> str:
        if recipient_type == "child":
            return f"""
Olá, {child_name}!

Sua atividade de hoje:

{message}

Divirta-se aprendendo! 📚✨

---
Pai & Mãe Integrado
"""
        else:
            return f"""
Olá, responsável!

Orientação pedagógica para {child_name}:

{message}

Obrigado por apoiar a educação de seu filho(a)! 🌟

---
Pai & Mãe Integrado
"""

    @staticmethod
    def _get_email_body_html(child_name: str, recipient_type: str, message: str) -> str:
        if recipient_type == "child":
            return f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #2c5282;">📚 Olá, {child_name}!</h2>
      <p>Sua interação de hoje:</p>
      <div style="background-color: #f0f7ff; padding: 15px; border-left: 4px solid #2c5282; margin: 20px 0;">
        <p>{message}</p>
      </div>
      <p>Divirta-se aprendendo! ✨</p>
      <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
      <p style="font-size: 12px; color: #999;">Pai & Mãe Integrado</p>
    </div>
  </body>
</html>
"""
        else:
            return f"""
<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #2c5282;">👨‍👩‍👧 Orientação para {child_name}</h2>
      <p>Sugestões pedagógicas de hoje:</p>
      <div style="background-color: #fff5f5; padding: 15px; border-left: 4px solid #c53030; margin: 20px 0;">
        <p>{message}</p>
      </div>
      <p>Obrigado por apoiar a educação! 🌟</p>
      <hr style="border: none; border-top: 1px solid #e0e0e0; margin: 20px 0;">
      <p style="font-size: 12px; color: #999;">Pai & Mãe Integrado</p>
    </div>
  </body>
</html>
"""

    @staticmethod
    def _get_sms_body(child_name: str, recipient_type: str, message: str) -> str:
        if recipient_type == "child":
            return f"Olá {child_name}! 📚 Sua atividade: {message[:50]}..."
        else:
            return f"Dica pedagógica para {child_name}: {message[:60]}..."
