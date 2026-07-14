from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Pai&MaeIntegrado"
    app_env: str = "local"
    app_timezone: str = "America/Recife"
    database_url: str = "postgresql+psycopg://paimae:paimae@localhost:5432/paimae"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Supabase Storage settings
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_bucket: str = "paimae-storage"

    # Google APIs (Vision OCR + Gemini LLM)
    google_vision_api_key: str = ""
    google_gemini_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def reject_default_secret_outside_local(self) -> "Settings":
        if self.app_env != "local" and self.jwt_secret_key == "change-me-in-production":
            raise ValueError("JWT_SECRET_KEY deve ser configurado fora do ambiente local.")
        
        # Corrige URL de conexão do PostgreSQL para usar o driver psycopg3
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif self.database_url.startswith("postgresql://") and not self.database_url.startswith("postgresql+psycopg://"):
            self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
            
        return self


settings = Settings()
