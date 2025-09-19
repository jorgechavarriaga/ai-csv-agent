from pydantic_settings import BaseSettings
from pydantic import SecretStr


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    ENABLE_FORCE_SEED: bool = True
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()
