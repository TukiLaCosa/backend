from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal, List


class Settings(BaseSettings):
    environment: Literal["test", "production", "development"] = "development"
    CORS_origins: List[str] = ["*"]
    CARDS_CSV_FILE_PTAH: str = "app/resources/cartas.csv"

    model_config = SettingsConfigDict(env_file=".env", extra='allow')

    @property
    def database_sqlite_connection(self):
        return {
            "provider": "sqlite",
            "filename": f"database_{self.environment}.sqlite",
            "create_db": True
        }


settings = Settings()
