"""
WhatsApp Reminder Sender via Twilio Sandbox.
Falls back to a simulated/logged send if Twilio isn't configured,
so the demo never breaks even without live credentials.
"""
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
FROM_NUMBER = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

LOG_FILE = "sent_messages_log.txt"


def is_configured() -> bool:
    return bool(ACCOUNT_SID and AUTH_TOKEN and "your_account_sid" not in (ACCOUNT_SID or ""))


def send_whatsapp_message(to_phone: str, message: str) -> dict:
    """
    Sends a WhatsApp message via Twilio. Falls back to simulation+logging
    if credentials aren't set up, so this never crashes a live demo.
    """
    if not is_configured():
        return _simulate_send(to_phone, message)

    try:
        from twilio.rest import Client
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        to_formatted = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
        msg = client.messages.create(from_=FROM_NUMBER, to=to_formatted, body=message)
        _log(to_phone, message, status=f"SENT (sid={msg.sid})")
        return {"status": "sent", "sid": msg.sid, "to": to_phone}
    except Exception as e:
        _log(to_phone, message, status=f"FAILED ({e})")
        return {"status": "failed", "error": str(e), "to": to_phone}


def _simulate_send(to_phone: str, message: str) -> dict:
    _log(to_phone, message, status="SIMULATED (no Twilio creds configured)")
    return {"status": "simulated", "to": to_phone}


def _log(to_phone: str, message: str, status: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] TO: {to_phone} | STATUS: {status}\nMESSAGE: {message}\n{'-'*50}\n")


def send_bulk_reminders(phone_list: list, message: str) -> list:
    """Send the same reminder to a list of confirmed attendees."""
    results = []
    for phone in phone_list:
        results.append(send_whatsapp_message(phone, message))
    return results
