"""
Google Sheets Integration - RSVP tracking.
Expects a sheet with columns: Name | Phone | Email | RSVP Status

Setup:
  1. Go to https://console.cloud.google.com → Create a project
  2. Enable Google Sheets API + Google Drive API
  3. Create a Service Account → download JSON key → save as service_account.json
  4. Share your Google Sheet with the service account email (Editor role)
  5. Set GOOGLE_SHEET_NAME in .env to match your sheet's exact name
"""
import os
import gspread
from dotenv import load_dotenv

load_dotenv()

CREDS_PATH = os.getenv("GOOGLE_SHEETS_CREDS_PATH", "service_account.json")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "GDG Event RSVPs")


def _get_client() -> gspread.Client:
    """Returns an authenticated gspread client using the service account JSON."""
    return gspread.service_account(filename=CREDS_PATH)


def get_rsvp_data() -> tuple[list, dict]:
    """
    Returns (records, summary).
    records : list of dicts, one per row (keyed by header row).
    summary : counts by RSVP status + phone numbers of confirmed attendees.
    """
    gc = _get_client()
    sheet = gc.open(SHEET_NAME).sheet1
    records = sheet.get_all_records()

    confirmed_phones: list[str] = []
    status_counts: dict[str, int] = {}

    for row in records:
        status = str(row.get("RSVP Status", "")).strip().lower()
        status_counts[status] = status_counts.get(status, 0) + 1
        if status == "confirmed" and row.get("Phone"):
            confirmed_phones.append(str(row["Phone"]).strip())

    summary = {
        "total_rows": len(records),
        "status_counts": status_counts,
        "confirmed_count": status_counts.get("confirmed", 0),
        "confirmed_phones": confirmed_phones,
    }
    return records, summary


def get_sheet_url() -> str | None:
    """Returns the URL of the configured sheet, or None on failure."""
    try:
        gc = _get_client()
        sheet = gc.open(SHEET_NAME)
        return f"https://docs.google.com/spreadsheets/d/{sheet.id}"
    except Exception:
        return None


def is_configured() -> bool:
    """True if the service account credentials file exists."""
    return os.path.exists(CREDS_PATH)

