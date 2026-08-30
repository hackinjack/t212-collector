"""Trading 212 API client."""

from typing import Any

import requests


BASE_URL = "https://live.trading212.com/api/v0"
PROVIDER = "trading212"


class Trading212Error(RuntimeError):
    """Trading 212 API error."""


class Trading212Client:
    """Small client for the Trading 212 API."""

    def __init__(
        self,
        api_key: str,
        api_secret: str,
        timeout: int = 30,
    ):
        self.auth = (api_key, api_secret)
        self.timeout = timeout

    def get_account_summary(self) -> dict[str, Any]:
        """Retrieve the current account summary."""

        url = f"{BASE_URL}/equity/account/summary"

        try:
            response = requests.get(
                url,
                auth=self.auth,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise Trading212Error(
                f"Trading 212 request failed: {exc}"
            ) from exc

        if response.status_code == 429:
            raise Trading212Error(
                "Trading 212 API rate limit exceeded"
            )

        if response.status_code in (401, 403):
            raise Trading212Error(
                f"Trading 212 authentication/authorisation failed "
                f"(HTTP {response.status_code})"
            )

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise Trading212Error(
                f"Trading 212 returned HTTP {response.status_code}"
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise Trading212Error(
                "Trading 212 returned invalid JSON"
            ) from exc
    def get_dividends(
        self,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Retrieve all historical dividend events."""

        url = f"{BASE_URL}/equity/history/dividends"

        params = {
            "limit": limit,
        }

        items: list[dict[str, Any]] = []

        while True:
            try:
                response = requests.get(
                    url,
                    auth=self.auth,
                    params=params,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                raise Trading212Error(
                    f"Trading 212 request failed: {exc}"
                ) from exc

            if response.status_code == 429:
                raise Trading212Error(
                    "Trading 212 API rate limit exceeded"
                )

            if response.status_code in (401, 403):
                raise Trading212Error(
                    f"Trading 212 authentication/authorisation failed "
                    f"(HTTP {response.status_code})"
                )

            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise Trading212Error(
                    f"Trading 212 returned HTTP {response.status_code}"
                ) from exc

            try:
                data = response.json()
            except ValueError as exc:
                raise Trading212Error(
                    "Trading 212 returned invalid JSON"
                ) from exc

            page_items = data.get("items")

            if not isinstance(page_items, list):
                raise Trading212Error(
                    "Trading 212 dividends response has invalid items"
                )

            items.extend(page_items)

            next_page_path = data.get("nextPagePath")

            if not next_page_path:
                break

            url = f"https://live.trading212.com{next_page_path}"
            params = {}

        return items

    def get_transactions(
        self,
        max_pages: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve all historical account transactions."""

        items: list[dict[str, Any]] = []
        url = f"{BASE_URL}/equity/history/transactions"
        params = {"limit": 50}
        pages = 0

        while True:
            try:
                response = requests.get(
                    url,
                    auth=self.auth,
                    params=params,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                raise Trading212Error(
                    f"Trading 212 request failed: {exc}"
                ) from exc

            if response.status_code == 429:
                raise Trading212Error(
                    "Trading 212 API rate limit exceeded"
                )

            if response.status_code in (401, 403):
                raise Trading212Error(
                    f"Trading 212 authentication/authorisation failed "
                    f"(HTTP {response.status_code})"
                )

            try:
                response.raise_for_status()
            except requests.HTTPError as exc:
                raise Trading212Error(
                    f"Trading 212 returned HTTP {response.status_code}"
                ) from exc

            try:
                data = response.json()
            except ValueError as exc:
                raise Trading212Error(
                    "Trading 212 returned invalid JSON"
                ) from exc

            page_items = data.get("items", [])

            if not isinstance(page_items, list):
                raise Trading212Error(
                    "Trading 212 transactions response has invalid items"
                )

            items.extend(page_items)
            pages += 1

            if max_pages is not None and pages >= max_pages:
                break

            next_page_path = data.get("nextPagePath")

            if not next_page_path:
                break

            url = f"https://live.trading212.com{next_page_path}"
            params = {}

        return items

def validate_account_summary(data: dict[str, Any]) -> None:
    """Validate the fields required by the collector."""

    required = {
        "id",
        "currency",
        "totalValue",
        "cash",
        "investments",
    }

    missing = required - data.keys()

    if missing:
        raise Trading212Error(
            "Trading 212 response missing fields: "
            + ", ".join(sorted(missing))
        )

    required_cash = {
        "availableToTrade",
        "reservedForOrders",
        "inPies",
    }

    missing_cash = required_cash - data["cash"].keys()

    if missing_cash:
        raise Trading212Error(
            "Trading 212 cash response missing fields: "
            + ", ".join(sorted(missing_cash))
        )

    required_investments = {
        "currentValue",
        "totalCost",
        "realizedProfitLoss",
        "unrealizedProfitLoss",
    }

    missing_investments = (
        required_investments - data["investments"].keys()
    )

    if missing_investments:
        raise Trading212Error(
            "Trading 212 investment response missing fields: "
            + ", ".join(sorted(missing_investments))
        )

    if not isinstance(data["id"], int):
        raise Trading212Error("Trading 212 account ID is not an integer")

    if not isinstance(data["currency"], str) or not data["currency"]:
        raise Trading212Error("Trading 212 currency is invalid")
