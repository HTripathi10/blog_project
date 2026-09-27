"""
config.py — Centralised settings loaded from .env

💡 CONCEPT: Environment Variables
   Never hardcode secrets (DB passwords, JWT keys, OAuth credentials).
   Instead, read them from the environment. The .env file is for local dev;
   in production these come from your cloud provider's secrets manager.

   pydantic-settings reads the .env file and validates every variable,
   giving you type safety + clear error messages if something is missing.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # OAuth — Google
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    # App
    frontend_url: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    max_file_size_mb: int = 5

    class Config:
        env_file = ".env"


# lru_cache means this function is only called ONCE — settings are a singleton
@lru_cache()
def get_settings() -> Settings:
    return Settings()
