"""Google OAuth authentication."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]


def authenticate(
    credentials_file: Path,
    token_file: Path,
) -> Credentials:
    """Authenticate the user and return Google OAuth credentials."""

    credentials = None

    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_file),
            SCOPES,
        )

    if credentials and credentials.valid:
        return credentials

    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file),
            SCOPES,
        )

        credentials = flow.run_local_server(
            port=0,
            access_type="offline",
            prompt="consent",
        )

    token_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    token_file.write_text(
        credentials.to_json(),
        encoding="utf-8",
    )

    token_file.chmod(0o600)

    return credentials
