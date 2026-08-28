"""Read-only HTTP API for portfolio data."""

import csv
import io
import os
import sqlite3
from pathlib import Path

from flask import Flask, Response, abort, jsonify, request


def create_app(
    database_path: Path,
    api_token: str,
) -> Flask:
    """Create the portfolio API application."""

    app = Flask(__name__)

    def require_export_auth(token: str) -> None:
        """Validate the export capability token."""

        if not token or not api_token or token != api_token:
            abort(404)

    def connect() -> sqlite3.Connection:
        """Open a read-only SQLite connection."""

        connection = sqlite3.connect(
            f"file:{database_path}?mode=ro",
            uri=True,
        )

        connection.row_factory = sqlite3.Row

        return connection

    def csv_response(
        headers: list[str],
        rows: list[tuple],
    ) -> Response:
        """Return rows as a CSV response."""

        output = io.StringIO()

        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)

        response = Response(
            output.getvalue(),
            mimetype="text/csv",
        )

        response.headers["Cache-Control"] = "no-store"

        return response

    @app.get("/api/v1/health")
    def health():
        """Return basic API health."""

        try:
            with connect() as connection:
                connection.execute(
                    "SELECT 1"
                ).fetchone()

            return jsonify({
                "status": "ok",
            })

        except sqlite3.Error:
            return jsonify({
                "status": "error",
            }), 503

    @app.get("/api/v1/export/accounts/<token>")
    def accounts(token):
        """Return known accounts."""

        require_export_auth(token)

        with connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    provider,
                    external_id,
                    name,
                    currency,
                    active,
                    updated_at
                FROM accounts
                ORDER BY provider, id
                """
            ).fetchall()

        return csv_response(
            [
                "id",
                "provider",
                "external_id",
                "name",
                "currency",
                "active",
                "updated_at",
            ],
            [
                tuple(row)
                for row in rows
            ],
        )

    @app.get("/api/v1/export/balances/<token>")
    def balances(token):
        """Return canonical daily balances."""

        require_export_auth(token)

        with connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    b.business_date,
                    a.provider,
                    a.name AS account,
                    b.currency,
                    b.total_value,
                    b.captured_at
                FROM daily_balances b
                JOIN accounts a
                    ON a.id = b.account_id
                ORDER BY
                    b.business_date,
                    a.provider,
                    a.id
                """
            ).fetchall()

        return csv_response(
            [
                "business_date",
                "provider",
                "account",
                "currency",
                "total_value",
                "captured_at",
            ],
            [
                tuple(row)
                for row in rows
            ],
        )

    @app.get("/api/v1/snapshots")
    @app.get("/api/v1/export/snapshots/<token>")
    def snapshots(token):
        """Return raw collection snapshots."""

        require_export_auth(token)

        with connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    s.captured_at,
                    a.provider,
                    a.name AS account,
                    s.currency,
                    s.total_value,
                    s.cash_available,
                    s.cash_reserved,
                    s.cash_in_pies,
                    s.investment_value,
                    s.investment_cost,
                    s.realized_profit_loss,
                    s.unrealized_profit_loss
                FROM daily_snapshots s
                LEFT JOIN accounts a
                    ON a.external_id =
                       CAST(s.account_id AS TEXT)
                ORDER BY s.captured_at
                """
            ).fetchall()

        return csv_response(
            [
                "captured_at",
                "provider",
                "account",
                "currency",
                "total_value",
                "cash_available",
                "cash_reserved",
                "cash_in_pies",
                "investment_value",
                "investment_cost",
                "realized_profit_loss",
                "unrealized_profit_loss",
            ],
            [
                tuple(row)
                for row in rows
            ],
        )

    @app.get("/api/v1/income")
    @app.get("/api/v1/export/income/<token>")
    def income(token):
        """Return normalised income records."""

        require_export_auth(token)

        with connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    i.transaction_date,
                    i.financial_year,
                    a.provider,
                    a.name AS account,
                    i.income_type,
                    i.currency,
                    i.gross_amount,
                    i.withholding_tax,
                    i.net_amount,
                    i.instrument
                FROM income i
                JOIN accounts a
                    ON a.id = i.account_id
                ORDER BY
                    i.transaction_date,
                    i.id
                """
            ).fetchall()

        return csv_response(
            [
                "transaction_date",
                "financial_year",
                "provider",
                "account",
                "income_type",
                "currency",
                "gross_amount",
                "withholding_tax",
                "net_amount",
                "instrument",
            ],
            [
                tuple(row)
                for row in rows
            ],
        )

    @app.get("/api/v1/tax-summary")
    @app.get("/api/v1/export/tax-summary/<token>")
    def tax_summary(token):
        """Return income aggregated by UK financial year."""

        require_export_auth(token)

        with connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    financial_year,
                    currency,
                    SUM(
                        CASE
                            WHEN income_type = 'interest'
                            THEN gross_amount
                            ELSE 0
                        END
                    ) AS interest,
                    SUM(
                        CASE
                            WHEN income_type = 'dividend'
                            THEN gross_amount
                            ELSE 0
                        END
                    ) AS dividends,
                    SUM(gross_amount) AS total_income
                FROM income
                GROUP BY
                    financial_year,
                    currency
                ORDER BY
                    financial_year,
                    currency
                """
            ).fetchall()

        return csv_response(
            [
                "financial_year",
                "currency",
                "interest",
                "dividends",
                "total_income",
            ],
            [
                tuple(row)
                for row in rows
            ],
        )

    return app


def main() -> None:
    """Run the development API server."""

    database_path = Path(
        os.getenv(
            "T212_DATABASE",
            "/opt/t212-collector/portfolio.db",
        )
    )

    api_token = os.getenv("T212_API_TOKEN")

    if not api_token:
        raise RuntimeError(
            "T212_API_TOKEN is not configured"
        )

    app = create_app(
        database_path=database_path,
        api_token=api_token,
    )

    app.run(
        host="127.0.0.1",
        port=8080,
        debug=False,
    )


if __name__ == "__main__":
    main()
