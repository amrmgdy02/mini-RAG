from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APPLICATION_NAME: str
    APPLICATION_VERSION: str
    OPENAI_API_KEY: str

    class Config(SettingsConfigDict):
        env_file = ".env"
        
def get_settings() -> Settings:
    return Settings()