"""Common provider connector types."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountSnapshot:
    """Normalised account snapshot produced by a provider connector."""

    provider: str
    external_id: str
    name: str
    currency: str
    total_value: float
    raw_data: dict[str, Any]
