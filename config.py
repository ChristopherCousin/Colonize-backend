from __future__ import annotations

import json
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings

_DEFAULT_CORS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
]


def _parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    """Acepta JSON array, string separado por comas, o URL única."""
    if isinstance(v, list):
        return [str(x).strip() for x in v]
    s = str(v).strip()
    if not s:
        return []
    if s.startswith("["):
        try:
            return [str(x).strip() for x in json.loads(s)]
        except json.JSONDecodeError:
            pass
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return [p if p.startswith("http") else f"https://{p}" for p in parts]


class Settings(BaseSettings):
    APP_NAME: str = "Colonize API"
    DATABASE_URL: str = "sqlite+aiosqlite:///./colonize.db"
    SECRET_KEY: str = "change-me-in-production-use-env-var"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    # Usar str para evitar que pydantic intente parsear JSON y falle con URLs sueltas
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:3001,http://localhost:3002"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        defaults = _DEFAULT_CORS.copy()
        if v is None or (isinstance(v, str) and not v.strip()):
            return defaults
        parsed = _parse_cors_origins(v)  # type: ignore
        if not parsed:
            return defaults
        seen = set(parsed)
        for d in defaults:
            if d not in seen:
                parsed.append(d)
        return parsed

    class Config:
        env_file = ".env"

    @property
    def async_database_url(self) -> str:
        """Convert Railway's postgresql:// to postgresql+asyncpg:// automatically."""
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url


settings = Settings()
