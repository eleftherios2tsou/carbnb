from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
