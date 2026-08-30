"""SQLite database handling."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .migrations import apply_migrations


SCHEMA_VERSION = 1


class Database:
    """Application database."""

    def __init__(self, path: Path):
        self.path = path

    def connect(self) -> sqlite3.Connection:
        """Open a database connection."""

        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialise(self) -> None:
        """Create the current database schema if required."""

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.connect() as connection:
            apply_migrations(connection)
            connection.commit()

    def get_account(
        self,
        provider: str,
        external_id: str,
    ) -> sqlite3.Row | None:
        """Return an account by provider and external ID."""

        with self.connect() as connection:
            return connection.execute(
                """
                SELECT *
                FROM accounts
                WHERE provider = ?
                  AND external_id = ?
                """,
                (provider, external_id),
            ).fetchone()

    def ensure_account(
        self,
        external_id: str,
        currency: str,
        name: str = "Trading 212",
    ) -> int:
        """Create or update the Trading 212 account."""

        now = datetime.now(timezone.utc).isoformat()

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO accounts (
                    provider,
                    external_id,
                    name,
                    currency,
                    active,
                    created_at,
                    updated_at
                )
                VALUES (
                    'trading212',
                    ?,
                    ?,
                    ?,
                    1,
                    ?,
                    ?
                )
                ON CONFLICT(provider, external_id)
                DO UPDATE SET
                    name = excluded.name,
                    currency = excluded.currency,
                    active = 1,
                    updated_at = excluded.updated_at
                """,
                (
                    str(external_id),
                    name,
                    currency,
                    now,
                    now,
                ),
            )

            row = connection.execute(
                """
                SELECT id
                FROM accounts
                WHERE provider = 'trading212'
                  AND external_id = ?
                """,
                (str(external_id),),
            ).fetchone()

        if row is None:
            raise RuntimeError(
                f"Trading 212 account not found after ensure: "
                f"{external_id}"
            )
        return int(row["id"])

    def save_snapshot(
        self,
        account_id: int,
        data: dict,
    ) -> None:
        """Save a raw Trading 212 snapshot."""

        captured_at = datetime.now(timezone.utc).isoformat()

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO daily_snapshots (
                    captured_at,
                    account_id,
                    currency,
                    total_value,
                    cash_available,
                    cash_reserved,
                    cash_in_pies,
                    investment_value,
                    investment_cost,
                    realized_profit_loss,
                    unrealized_profit_loss,
                    raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    captured_at,
                    account_id,
                    data["currency"],
                    float(data["totalValue"]),
                    float(data["cash"]["availableToTrade"]),
                    float(data["cash"]["reservedForOrders"]),
                    float(data["cash"]["inPies"]),
                    float(data["investments"]["currentValue"]),
                    float(data["investments"]["totalCost"]),
                    float(data["investments"]["realizedProfitLoss"]),
                    float(data["investments"]["unrealizedProfitLoss"]),
                    json.dumps(data, separators=(",", ":")),
                ),
            )

            connection.commit()

    def save_daily_balance(
        self,
        account_id: int,
        data: dict,
        business_date: str,
        captured_at: str,
    ) -> None:
        """Create or replace the canonical daily balance."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO daily_balances (
                    account_id,
                    business_date,
                    captured_at,
                    total_value,
                    currency
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(account_id, business_date)
                DO UPDATE SET
                    captured_at = excluded.captured_at,
                    total_value = excluded.total_value,
                    currency = excluded.currency
                """,
                (
                    account_id,
                    business_date,
                    captured_at,
                    float(data["totalValue"]),
                    data["currency"],
                ),
            )

            connection.commit()

    def save_income(
            self,
            account_id: int,
            items: list[dict],
        ) -> int:
        """Save normalised Trading 212 income records."""

        saved = 0

        with self.connect() as connection:
            for item in items:
                income_type = item.get("type")

                if income_type not in {"DIVIDEND", "INTEREST_ON_FREE_CASH"}:
                    continue

                reference = item.get("reference")
                paid_on = item.get("paidOn") or item.get("dateTime")
                amount = item.get("amount")
                currency = item.get("currency")
                instrument = item.get("ticker")

                if not reference:
                    raise ValueError(
                        "Dividend response missing reference"
                    )

                if not paid_on:
                    raise ValueError(
                        f"Dividend {reference} missing paidOn"
                    )

                if amount is None:
                    raise ValueError(
                        f"Dividend {reference} missing amount"
                    )

                if not currency:
                    raise ValueError(
                        f"Dividend {reference} missing currency"
                    )

                transaction_date = paid_on[:10]

                year = int(transaction_date[:4])
                month = int(transaction_date[5:7])

                if month >= 4:
                    financial_year = f"{year}/{str(year + 1)[-2:]}"
                else:
                    financial_year = f"{year - 1}/{str(year)[-2:]}"

                connection.execute(
                    """
                    INSERT INTO income (
                        transaction_id,
                        transaction_date,
                        financial_year,
                        account_id,
                        income_type,
                        currency,
                        gross_amount,
                        withholding_tax,
                        net_amount,
                        instrument,
                        raw_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(transaction_id)
                    DO UPDATE SET
                        transaction_date = excluded.transaction_date,
                        financial_year = excluded.financial_year,
                        account_id = excluded.account_id,
                        income_type = excluded.income_type,
                        currency = excluded.currency,
                        gross_amount = excluded.gross_amount,
                        withholding_tax = excluded.withholding_tax,
                        net_amount = excluded.net_amount,
                        instrument = excluded.instrument,
                        raw_json = excluded.raw_json
                    """,
                    (
                        reference,
                        transaction_date,
                        financial_year,
                        account_id,
                        "dividend"
                        if income_type == "DIVIDEND"
                        else "interest",
                        currency,
                        float(amount),
                        0.0,
                        float(amount),
                        instrument,
                        json.dumps(
                            item,
                            separators=(",", ":"),
                        ),
                    ),
                )

                saved += 1

            connection.commit()

        return saved

    def record_sync_start(self, operation: str) -> int:
        """Record the beginning of a synchronisation operation."""

        started_at = datetime.now(timezone.utc).isoformat()

        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO sync_runs (
                    started_at,
                    operation,
                    status
                )
                VALUES (?, ?, 'running')
                """,
                (started_at, operation),
            )

            connection.commit()

            return int(cursor.lastrowid)

    def record_sync_complete(
        self,
        sync_id: int,
        status: str,
        records_processed: int = 0,
        error: str | None = None,
    ) -> None:
        """Complete a synchronisation record."""

        finished_at = datetime.now(timezone.utc).isoformat()

        with self.connect() as connection:
            connection.execute(
                """
                UPDATE sync_runs
                SET finished_at = ?,
                    status = ?,
                    records_processed = ?,
                    error = ?
                WHERE id = ?
                """,
                (
                    finished_at,
                    status,
                    records_processed,
                    error,
                    sync_id,
                ),
            )

            connection.commit()
