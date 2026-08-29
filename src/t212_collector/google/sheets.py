"""Google Sheets exporter."""

import csv
import io
from pathlib import Path

import requests
from googleapiclient.discovery import build

from google.oauth2.service_account import Credentials


SHEETS = {
    "balances": (
        "Balances",
        "/api/v1/export/balances/",
    ),
    "snapshots": (
        "Snapshots",
        "/api/v1/export/snapshots/",
    ),
    "income": (
        "Income",
        "/api/v1/export/income/",
    ),
    "tax-summary": (
        "Tax Summary",
        "/api/v1/export/tax-summary/",
    ),
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_credentials(credentials_file: Path) -> Credentials:
    """Load Google service-account credentials."""

    return Credentials.from_service_account_file(
        str(credentials_file),
        scopes=SCOPES,
    )

def fetch_csv(
    api_base_url: str,
    api_token: str,
    endpoint: str,
) -> list[list[str]]:
    """Fetch CSV data from the local portfolio API."""

    response = requests.get(
        f"{api_base_url.rstrip('/')}{endpoint}{api_token}",
        timeout=30,
    )
    response.raise_for_status()

    return list(
        csv.reader(
            io.StringIO(response.text)
        )
    )


def ensure_sheet(
    service,
    spreadsheet_id: str,
    title: str,
) -> None:
    """Create the worksheet if it doesn't already exist."""

    spreadsheet = (
        service.spreadsheets()
        .get(
            spreadsheetId=spreadsheet_id,
            fields="sheets.properties",
        )
        .execute()
    )

    existing_titles = {
        sheet["properties"]["title"]
        for sheet in spreadsheet.get("sheets", [])
    }

    if title in existing_titles:
        return

    (
        service.spreadsheets()
        .batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": title,
                            }
                        }
                    }
                ]
            },
        )
        .execute()
    )


def write_sheet(
    service,
    spreadsheet_id: str,
    title: str,
    values: list[list[str]],
) -> None:
    """Replace the contents of one worksheet."""

    ensure_sheet(
        service,
        spreadsheet_id,
        title,
    )

    values_api = service.spreadsheets().values()

    values_api.clear(
        spreadsheetId=spreadsheet_id,
        range=f"'{title}'",
    ).execute()

    if not values:
        return

    values_api.update(
        spreadsheetId=spreadsheet_id,
        range=f"'{title}'!A1",
        valueInputOption="RAW",
        body={
            "values": values,
        },
    ).execute()

def export(
    *,
    credentials_file: Path,
    spreadsheet_id: str,
    api_base_url: str,
    api_token: str,
) -> None:
    """Export portfolio data to Google Sheets."""

    credentials = get_credentials(credentials_file)

    service = build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )

    for endpoint, (title, path) in SHEETS.items():
        values = fetch_csv(
            api_base_url=api_base_url,
            api_token=api_token,
            endpoint=path,
        )

        write_sheet(
            service=service,
            spreadsheet_id=spreadsheet_id,
            title=title,
            values=values,
        )

        print(
            f"{title}: {max(len(values) - 1, 0)} records"
        )
