import logging
import urllib.request
import urllib.error
from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    def __init__(self) -> None:
        self.url = settings.supabase_url.rstrip("/") if settings.supabase_url else ""
        self.key = settings.supabase_key
        self.bucket = settings.supabase_bucket

    def upload_file(self, file_content: bytes, file_name: str, mime_type: str = "application/octet-stream") -> str | None:
        """
        Realiza o upload de um arquivo para o Supabase Storage.
        Retorna a URL pública do arquivo enviado, ou None se falhar ou se não estiver configurado.
        """
        if not self.url or not self.key or not self.bucket:
            logger.warning("Supabase Storage não está configurado. O arquivo não foi enviado.")
            return None

        # O endpoint do Supabase Storage para upload é /storage/v1/object/{bucket}/{filename}
        upload_url = f"{self.url}/storage/v1/object/{self.bucket}/{file_name}"
        
        headers = {
            "Authorization": f"Bearer {self.key}",
            "ApiKey": self.key,
            "Content-Type": mime_type
        }
        
        req = urllib.request.Request(upload_url, data=file_content, headers=headers, method="POST")
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 201):
                    # Retorna a URL pública
                    return f"{self.url}/storage/v1/object/public/{self.bucket}/{file_name}"
                else:
                    logger.error(f"Erro ao enviar arquivo para o Supabase: Status {response.status}")
                    return None
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Erro HTTP ao enviar arquivo para o Supabase: {e.code} - {error_body}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao enviar arquivo para o Supabase: {str(e)}")
            return None


storage_service = SupabaseStorageService()
