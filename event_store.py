"""
Event Storage — Persists events as JSON so that the GDG lead / admin can
browse past events and review draft (unpublished) events across sessions.

Events are stored in a local JSON file. Each event has a status:
  - "draft"     → Generated but not yet published/used
  - "upcoming"  → Confirmed as a live event
  - "past"      → Event date has passed (auto-detected or manually marked)
"""
import os
import json
from datetime import datetime, date

EVENTS_FILE = os.path.join(os.path.dirname(__file__), "events_store.json")


def _load_events() -> list[dict]:
    """Load all events from the JSON store."""
    if not os.path.exists(EVENTS_FILE):
        return []
    try:
        with open(EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_events(events: list[dict]):
    """Write the full event list back to disk."""
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2, ensure_ascii=False, default=str)


def _auto_update_statuses(events: list[dict]) -> list[dict]:
    """Mark upcoming events as 'past' if their date has passed."""
    today = date.today().isoformat()
    changed = False
    for ev in events:
        if ev.get("status") == "upcoming" and ev.get("date", "") < today:
            ev["status"] = "past"
            changed = True
    if changed:
        _save_events(events)
    return events


def save_event(meta: dict, package: dict, status: str = "draft") -> dict:
    """
    Save a new event (meta + generated content) to the store.
    Returns the saved event dict (including generated id).
    """
    events = _load_events()

    event = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S") + f"_{len(events)}",
        "status": status,
        "created_at": datetime.now().isoformat(),
        **meta,
        "package": package,
    }

    events.append(event)
    _save_events(events)
    return event


def get_all_events() -> list[dict]:
    """Return all events, with statuses auto-updated."""
    events = _load_events()
    return _auto_update_statuses(events)


def get_draft_events() -> list[dict]:
    """Return only draft events."""
    return [e for e in get_all_events() if e.get("status") == "draft"]


def get_past_events() -> list[dict]:
    """Return past events (most recent first)."""
    past = [e for e in get_all_events() if e.get("status") == "past"]
    past.sort(key=lambda e: e.get("date", ""), reverse=True)
    return past


def get_upcoming_events() -> list[dict]:
    """Return upcoming (published) events."""
    upcoming = [e for e in get_all_events() if e.get("status") == "upcoming"]
    upcoming.sort(key=lambda e: e.get("date", ""))
    return upcoming


def update_event_status(event_id: str, new_status: str) -> bool:
    """Update the status of an event by its id. Returns True on success."""
    events = _load_events()
    for ev in events:
        if ev.get("id") == event_id:
            ev["status"] = new_status
            _save_events(events)
            return True
    return False


def delete_event(event_id: str) -> bool:
    """Delete an event by its id. Returns True on success."""
    events = _load_events()
    original_len = len(events)
    events = [e for e in events if e.get("id") != event_id]
    if len(events) < original_len:
        _save_events(events)
        return True
    return False
