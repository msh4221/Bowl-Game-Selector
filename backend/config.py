from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    family_password: str = "bowlpicks2024"
    odds_api_key: str = ""
    secret_key: str = "change-this-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), ".env")


@lru_cache()
def get_settings():
    return Settings()
