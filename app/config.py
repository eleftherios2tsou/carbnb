from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: AnyUrl | str = "postgresql+psycopg://postgres:postgres@localhost:5432/turolite"

    aws_region: str | None = None
    aws_s3_bucket: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
