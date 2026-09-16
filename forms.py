"""
Registration Form — writes new attendee submissions directly to the
GDG Event RSVPs Google Sheet using the existing gspread service account.

This is the practical alternative to Google Forms API (which doesn't
support service account authentication).
"""
import os
import gspread
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CREDS_PATH = os.getenv("GOOGLE_SHEETS_CREDS_PATH", "service_account.json")
SHEET_NAME  = os.getenv("GOOGLE_SHEET_NAME", "GDG Event RSVPs")

EXPECTED_HEADERS = ["Name", "Phone", "Email", "Year & Branch", "RSVP Status", "Registered At"]


def is_configured() -> bool:
    return os.path.exists(CREDS_PATH)


def _get_sheet():
    gc = gspread.service_account(filename=CREDS_PATH)
    return gc.open(SHEET_NAME).sheet1


def _ensure_headers(sheet):
    """Make sure the sheet has the right headers in row 1. Safe to call every time."""
    first_row = sheet.row_values(1)
    if first_row != EXPECTED_HEADERS:
        sheet.update("A1:F1", [EXPECTED_HEADERS])


def register_attendee(name: str, phone: str, email: str, year_branch: str = "") -> dict:
    """
    Adds a new attendee row to the RSVP sheet with status 'pending'.

    Returns:
        {"status": "ok", "row": int} on success
        {"status": "error", "message": str} on failure
    """
    if not is_configured():
        return {"status": "error", "message": "Google Sheets not configured."}

    # Basic validation
    name  = name.strip()
    phone = phone.strip()
    email = email.strip()
    if not name or not phone or not email:
        return {"status": "error", "message": "Name, phone and email are required."}

    # Normalize phone — ensure + prefix for E.164
    if not phone.startswith("+") and not phone.startswith("whatsapp:"):
        phone = "+" + phone

    try:
        sheet = _get_sheet()
        _ensure_headers(sheet)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [name, phone, email, year_branch, "pending", timestamp]
        sheet.append_row(new_row, value_input_option="USER_ENTERED")

        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_registration_count() -> int:
    """Returns total number of registrations (rows excluding header)."""
    try:
        sheet = _get_sheet()
        return max(0, sheet.row_count - 1)
    except Exception:
        return 0
