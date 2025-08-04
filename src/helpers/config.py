from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APPLICATION_NAME: str
    APPLICATION_VERSION: str
    OPENAI_API_KEY: str
    ALLOWED_FILE_TYPES: list[str]
    MAX_FILE_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int

    class Config(SettingsConfigDict):
        env_file = ".env"
        
def get_settings() -> Settings:
    return Settings()