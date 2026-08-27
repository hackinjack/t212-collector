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

DATABASE_PATH = Path(
    os.getenv("T212_DATABASE", BASE_DIR / "portfolio.db")
)

load_dotenv(ENV_FILE)


def get_api_credentials() -> tuple[str, str]:
    """Return Trading 212 API credentials from the environment."""

    api_key = os.getenv("T212_API_KEY")
    api_secret = os.getenv("T212_API_SECRET")

    if not api_key:
        raise RuntimeError("T212_API_KEY is not configured")

    if not api_secret:
        raise RuntimeError("T212_API_SECRET is not configured")

    return api_key, api_secret
