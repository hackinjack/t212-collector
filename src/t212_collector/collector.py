"""Trading 212 collection orchestration."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import DATABASE_PATH, get_api_credentials
from .database import Database
from .t212 import Trading212Client


LOG = logging.getLogger(__name__)

LONDON = ZoneInfo("Europe/London")


def collect() -> None:
    """Collect and persist one Trading 212 account snapshot."""

    database = Database(DATABASE_PATH)
    database.initialise()

    sync_id = database.record_sync_start("t212_account_snapshot")

    try:
        api_key, api_secret = get_api_credentials()

        client = Trading212Client(
            api_key=api_key,
            api_secret=api_secret,
        )

        snapshot = client.get_account_snapshot()

        data = snapshot.raw_data

        account_id = database.ensure_account(
            provider=snapshot.provider,
            external_id=snapshot.external_id,
            currency=snapshot.currency,
            name=snapshot.name,
        )

        captured_at = datetime.now().astimezone()
        captured_at_utc = captured_at.astimezone(
            ZoneInfo("UTC")
        ).isoformat()

        business_date = captured_at.astimezone(
            LONDON
        ).date().isoformat()

        database.save_snapshot(
            account_id=account_id,
            data=data,
        )

        database.save_daily_balance(
            account_id=account_id,
            data=data,
            business_date=business_date,
            captured_at=captured_at_utc,
        )

        dividends = client.get_dividends()

        transactions = client.get_transactions(max_pages=1)

        income_items = dividends + [
            item
            for item in transactions
            if item.get("type") == "INTEREST_ON_FREE_CASH"
        ]

        income_count = database.save_income(
            account_id=account_id,
            items=income_items,
        )

        database.record_sync_complete(
            sync_id=sync_id,
            status="success",
            records_processed=1 + income_count,
        )

        LOG.info(
            "Trading 212 snapshot collected: "
            "account=%s total=%s %s income_records=%s",
            data["id"],
            data["totalValue"],
            data["currency"],
            income_count,
        )

    except Exception as exc:
        database.record_sync_complete(
            sync_id=sync_id,
            status="failed",
            error=str(exc),
        )
        raise
