"""Application configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(
    os.getenv("T212_BASE_DIR", "/opt/t212-collector")
)

ENV_FILE = Path(
    os.getenv("T212_ENV_FILE", BASE_DIR / ".env")
)

# Load environment before reading configuration values.
load_dotenv(ENV_FILE)

DATABASE_PATH = Path(
    os.getenv("T212_DATABASE", BASE_DIR / "portfolio.db")
)

MIGRATIONS_PATH = Path(
    os.getenv("T212_MIGRATIONS", BASE_DIR / "migrations")
)

GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    "T212_GOOGLE_SERVICE_ACCOUNT_FILE"
)

GOOGLE_SPREADSHEET_ID = os.getenv(
    "T212_GOOGLE_SPREADSHEET_ID"
)

GOOGLE_API_BASE_URL = os.getenv(
    "T212_GOOGLE_API_BASE_URL",
    "http://127.0.0.1:8080",
)


def get_api_credentials() -> tuple[str, str]:
    """Return Trading 212 API credentials from the environment."""

    api_key = os.getenv("T212_API_KEY")
    api_secret = os.getenv("T212_API_SECRET")

    if not api_key:
        raise RuntimeError("T212_API_KEY is not configured")

    if not api_secret:
        raise RuntimeError("T212_API_SECRET is not configured")

    return api_key, api_secret
