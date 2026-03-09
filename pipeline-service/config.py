from __future__ import annotations

"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

SERVICE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SERVICE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)
load_dotenv(SERVICE_DIR / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    """Runtime configuration shared across service modules."""

    mock_server_url: str
    ingest_page_size: int

    @classmethod
    def from_env(cls) -> "Settings":
        """Construct validated settings values from environment variables."""
        page_size = int(os.getenv("INGEST_PAGE_SIZE", "10"))
        if page_size < 1:
            page_size = 1

        return cls(
            mock_server_url=os.getenv("MOCK_SERVER_URL", "http://mock-server:5000"),
            ingest_page_size=page_size,
        )


settings = Settings.from_env()
