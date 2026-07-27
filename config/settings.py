"""Environment-driven settings for the automation suite."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings."""

    api_base_url: str
    api_timeout: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings loaded from environment / .env."""
    return Settings(
        api_base_url=os.getenv(
            "API_BASE_URL", "https://jsonplaceholder.typicode.com"
        ).rstrip("/"),
        api_timeout=int(os.getenv("API_TIMEOUT", "30")),
    )
