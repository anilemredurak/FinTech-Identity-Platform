import os
from pathlib import Path
from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str | None = None

    JWT_PRIVATE_KEY_PATH: str
    JWT_PUBLIC_KEY_PATH: str
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 900
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 604800

    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    RATELIMIT_REQUESTS: int = 10
    RATELIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"


settings = Settings()
