#!/usr/bin/env python3

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_URL = "https://live.trading212.com/api/v0"
DB_PATH = Path("/opt/t212-collector/portfolio.db")
ENV_PATH = Path("/opt/t212-collector/.env")

load_dotenv(ENV_PATH)

API_KEY = os.environ["T212_API_KEY"]
API_SECRET = os.environ["T212_API_SECRET"]


SCHEMA = """
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
"""


def initialise_database():
    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(SCHEMA)


def get_account_snapshot():
    response = requests.get(
        f"{BASE_URL}/equity/account/summary",
        auth=(API_KEY, API_SECRET),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def save_snapshot(data):
    captured_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_PATH) as connection:
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
                data["id"],
                data["currency"],
                data["totalValue"],
                data["cash"]["availableToTrade"],
                data["cash"]["reservedForOrders"],
                data["cash"]["inPies"],
                data["investments"]["currentValue"],
                data["investments"]["totalCost"],
                data["investments"]["realizedProfitLoss"],
                data["investments"]["unrealizedProfitLoss"],
                json.dumps(data, separators=(",", ":")),
            ),
        )


def main():
    initialise_database()

    data = get_account_snapshot()

    print(json.dumps(data, indent=2))

    save_snapshot(data)

    print("Snapshot saved successfully.")


if __name__ == "__main__":
    main()
