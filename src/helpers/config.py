from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APPLICATION_NAME: str
    APPLICATION_VERSION: str
    ALLOWED_FILE_TYPES: list[str]
    MAX_FILE_SIZE_MB: int
    FILE_DEFAULT_CHUNK_SIZE: int
    FILE_DEFAULT_OVERLAP_SIZE: int
    MONGO_URL: str
    MONGODB_NAME: str
    OPENAI_API_KEY: str
    OPENAI_API_URL: str
    OLLAMA_BASE_URL: str
    LLM_PROVIDER: str
    EMBEDDING_SIZE: int
    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    VECTOR_DB_PATH: str
    
    DEFAULT_INPUT_MAX_CHARACTERS: int = 1000
    DEFAULT_GENERATION_MAX_OUTPUT_TOKENS: int = 1000
    DEFAULT_GENERATION_TEMPERATURE: float = 0.1
    
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    CELERY_TASK_SERIALIZER: str
    CELERY_TASK_TIME_LIMIT: int
    CELERY_TASK_ACKS_LATE: bool
    CELERY_WORKER_CONCURRENCY: int
    CELERY_FLOWER_PASSWORD: str
    QDRANT_HOST: str
    QDRANT_PORT: int

    class Config(SettingsConfigDict):
        env_file = ".env"
        
def get_settings() -> Settings:
    return Settings()