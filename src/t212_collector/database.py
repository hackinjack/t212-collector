"""SQLite database handling."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


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

        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    name TEXT,
                    currency TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(provider, external_id)
                );

                CREATE TABLE IF NOT EXISTS daily_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    captured_at TEXT NOT NULL,
                    account_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    total_value REAL NOT NULL,
                    cash_available REAL NOT NULL,
                    cash_reserved REAL NOT NULL,
                    cash_in_pies REAL NOT NULL,
                    investment_value REAL NOT NULL,
                    investment_cost REAL NOT NULL,
                    realized_profit_loss REAL NOT NULL,
                    unrealized_profit_loss REAL NOT NULL,
                    raw_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_daily_snapshots_captured_at
                    ON daily_snapshots(captured_at);

                CREATE INDEX IF NOT EXISTS idx_daily_snapshots_account
                    ON daily_snapshots(account_id);

                CREATE TABLE IF NOT EXISTS daily_balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    business_date TEXT NOT NULL,
                    captured_at TEXT NOT NULL,
                    total_value REAL NOT NULL,
                    currency TEXT NOT NULL,
                    UNIQUE(account_id, business_date),
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                );

                CREATE INDEX IF NOT EXISTS idx_daily_balances_account_date
                    ON daily_balances(account_id, business_date);

                CREATE TABLE IF NOT EXISTS income (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id TEXT,
                    transaction_date TEXT NOT NULL,
                    financial_year TEXT NOT NULL,
                    account_id INTEGER NOT NULL,
                    income_type TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    gross_amount REAL NOT NULL,
                    withholding_tax REAL DEFAULT 0,
                    net_amount REAL,
                    instrument TEXT,
                    raw_json TEXT,
                    UNIQUE(transaction_id)
                );

                CREATE TABLE IF NOT EXISTS sync_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    operation TEXT NOT NULL,
                    status TEXT NOT NULL,
                    records_processed INTEGER NOT NULL DEFAULT 0,
                    error TEXT
                );
                """
            )

            connection.execute(
                """
                INSERT OR IGNORE INTO schema_version(version, applied_at)
                VALUES (?, ?)
                """,
                (
                    SCHEMA_VERSION,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

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

            connection.commit()

        if row is None:
            raise RuntimeError("Unable to create Trading 212 account")

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
                    int(data["id"]),
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
