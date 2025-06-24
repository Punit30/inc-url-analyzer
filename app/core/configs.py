import os
from typing import List, Optional, Union

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "INC URL Analyzer"
    PROJECT_DESCRIPTION: str = "A URL analyzer to manage social media reach"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            # Support both comma-separated and JSON-style input
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                # JSON-style list in string
                import json
                return json.loads(v)
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        raise ValueError(
            "CORS_ORIGINS must be a list or a comma-separated string")

    # Database settings
    DATABASE_URL: Optional[PostgresDsn]
    # DATABASE_URL: str = "sqlite:///database.db"

    model_config = SettingsConfigDict(
        env_file=f".env.{os.getenv('ENV', 'local')}", case_sensitive=True)


settings = Settings()  # type: ignore
