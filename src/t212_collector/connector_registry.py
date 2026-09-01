"""Provider connector registry."""

from .t212 import Trading212Client


CONNECTORS = {
    "trading212": Trading212Client,
}


def get_connector(provider: str):
    """Return the connector class for a provider."""

    try:
        return CONNECTORS[provider]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported provider: {provider}"
        ) from exc
