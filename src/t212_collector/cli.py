"""Command-line interface."""

import argparse
import logging
import sqlite3

from .collector import collect
from .config import DATABASE_PATH
from .database import Database

from pathlib import Path

def google_auth() -> None:
    """Perform Google OAuth authentication."""

    from .google.auth import authenticate

    base_dir = Path(
        __import__("os").environ.get(
            "T212_BASE_DIR",
            "/opt/t212-collector",
        )
    )

    credentials_file = base_dir / "credentials.json"
    token_file = base_dir / "token.json"

    if not credentials_file.exists():
        raise RuntimeError(
            f"Google credentials file not found: "
            f"{credentials_file}"
        )

    credentials = authenticate(
        credentials_file=credentials_file,
        token_file=token_file,
    )

    print("Google authentication successful.")
    print(f"Token saved to: {token_file}")
    print(f"Scopes: {credentials.scopes}")

def configure_logging() -> None:
    """Configure simple console logging."""

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s "
            "%(name)s: %(message)s"
        ),
    )


def status() -> None:
    """Display basic collector/database status."""

    database = Database(DATABASE_PATH)
    database.initialise()

    with database.connect() as connection:
        snapshot_count = connection.execute(
            "SELECT COUNT(*) FROM daily_snapshots"
        ).fetchone()[0]

        balance_count = connection.execute(
            "SELECT COUNT(*) FROM daily_balances"
        ).fetchone()[0]

        income_count = connection.execute(
            "SELECT COUNT(*) FROM income"
        ).fetchone()[0]

        print(f"Database: {DATABASE_PATH}")
        print(f"Raw snapshots: {snapshot_count}")
        print(f"Daily balances: {balance_count}")
        print(f"Income records: {income_count}")

def main() -> None:
    """Run the command-line interface."""

    parser = argparse.ArgumentParser(
        description="Trading 212 portfolio collector"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    subparsers.add_parser(
        "collect",
        help="Collect a Trading 212 snapshot",
    )

    subparsers.add_parser(
        "status",
        help="Display database status",
    )

    subparsers.add_parser(
        "google-auth",
        help="Authenticate with Google",
)

    args = parser.parse_args()

    configure_logging()

    if args.command == "collect":
        collect()
    elif args.command == "status":
        status()
    elif args.command == "google-auth":
        google_auth()


if __name__ == "__main__":
    main()
