from pydantic_settings import BaseSettings
from pydantic import SecretStr
from typing import List


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    ENABLE_FORCE_SEED: bool = True
    OPENAI_API_KEY: str | None = None
    LLM_PROVIDERS: List[str] = ["openai"]
    OPENAI_MODEL: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()
