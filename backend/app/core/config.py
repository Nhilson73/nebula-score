from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BASE_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    nebula_env: str = "development"
    nebula_database_url: str = "sqlite:///./nebula_score.db"
    nebula_cors_origins: str = "http://localhost:5173,http://localhost:3000"
    nebula_host: str = "0.0.0.0"
    nebula_port: int = 8000
    methodologies_path: Path = REPO_ROOT / "methodologies"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.nebula_cors_origins.split(",") if origin.strip()]


settings = Settings()
