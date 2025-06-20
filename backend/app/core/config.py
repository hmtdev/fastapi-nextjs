from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv
import os 

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f".env.{ENVIRONMENT}",extra = "allow")

    environment: str
    secret_key: str
    database_url: str
    debug: bool
    admin_email: str
    api_key: str
    app_name: str 
    access_token_expire_minutes: int = 30

settings = Settings()

@lru_cache
def get_settings() -> Settings:
    return settings