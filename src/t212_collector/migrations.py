"""Database migration handling."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


MIGRATIONS_DIR = (
    Path(__file__).resolve().parents[2] / "migrations"
)


def ensure_migration_table(
    connection: sqlite3.Connection,
) -> None:
    """Create the migration tracking table."""

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        )
        """
    )


def get_applied_versions(
    connection: sqlite3.Connection,
) -> set[int]:
    """Return all applied migration versions."""

    rows = connection.execute(
        """
        SELECT version
        FROM schema_version
        ORDER BY version
        """
    ).fetchall()

    return {int(row[0]) for row in rows}


def database_has_legacy_schema(
    connection: sqlite3.Connection,
) -> bool:
    """Return True if this looks like a v0.1 database."""

    row = connection.execute(
        """
        SELECT COUNT(*)
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'daily_snapshots'
        """
    ).fetchone()

    return bool(row[0])


def apply_migrations(
    connection: sqlite3.Connection,
) -> None:
    """Apply outstanding database migrations."""

    ensure_migration_table(connection)

    applied = get_applied_versions(connection)
    legacy_schema = database_has_legacy_schema(connection)

    migration_files = sorted(
        MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql")
    )

    for migration_file in migration_files:
        version = int(migration_file.name[:3])

        if version in applied:
            continue

        # Migration 002 specifically migrates the v0.1 database.
        # There is nothing to migrate on a fresh installation.
        if version == 2 and not legacy_schema:
            connection.execute(
                """
                INSERT INTO schema_version(
                    version,
                    applied_at
                )
                VALUES (?, ?)
                """,
                (
                    version,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

            connection.commit()
            continue

        sql = migration_file.read_text(
            encoding="utf-8"
        )

        connection.executescript(sql)

        connection.execute(
            """
            INSERT INTO schema_version(
                version,
                applied_at
            )
            VALUES (?, ?)
            """,
            (
                version,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.commit()
