from pydantic_settings import BaseSettings
from pydantic import AnyUrl
class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: AnyUrl | str = "postgresql+psycopg://postgres:postgres@localhost:5432/carbnb"
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
