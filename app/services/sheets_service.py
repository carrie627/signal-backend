import logging
from datetime import datetime, timezone
from functools import lru_cache

import gspread
from google.oauth2.service_account import Credentials

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

SHEET_HEADERS = [
    "timestamp",
    "name",
    "email",
    "company",
    "message",
    "matched_service",
    "confidence",
    "score",
    "status",
    "summary",
]


@lru_cache
def _get_worksheet() -> gspread.Worksheet:
    settings = get_settings()
    credentials = Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    
    # if settings.google_service_account_json:
    #     # Render / most PaaS free tiers: paste the JSON key's contents
    #     # directly into an env var instead of uploading a file.
    #     info = json.loads(settings.google_service_account_json)
    #     credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    # else:
    #     credentials = Credentials.from_service_account_file(
    #         settings.google_service_account_file, scopes=SCOPES
    #     )

    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(settings.google_sheet_id)
    worksheet = spreadsheet.sheet1

    if worksheet.row_count == 0 or not worksheet.row_values(1):
        worksheet.append_row(SHEET_HEADERS)

    return worksheet


def append_lead_row(
    name: str,
    email: str,
    company: str,
    message: str,
    matched_service: str,
    confidence: int,
    score: int,
    status: str,
    summary: str,
) -> None:
    """Runs as a FastAPI background task — network latency here must never
    delay the response sent back to Zap 1."""
    try:
        worksheet = _get_worksheet()
        worksheet.append_row(
            [
                datetime.now(timezone.utc).isoformat(),
                name,
                email,
                company,
                message,
                matched_service,
                confidence,
                score,
                status,
                summary,
            ]
        )
    except Exception:
        # Intentionally broad: a Sheets outage must never crash the request
        # cycle since this always runs after the response is already sent.
        logger.exception("Failed to append lead row to Google Sheets")
