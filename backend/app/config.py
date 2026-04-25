from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/recipes.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    upload_dir: str = "./data/uploads"
    max_upload_size_mb: int = 10
    allow_registration: bool = True

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
