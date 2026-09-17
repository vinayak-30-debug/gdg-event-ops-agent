"""
GDG Event Ops Agent - Core Generation Logic
Takes a rough event idea and produces ready-to-use event content.
"""
import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

MODEL_NAME = "gemini-2.0-flash"


def _call_gemini(prompt: str, max_retries: int = 3) -> str:
    """Single point of contact with Gemini, with retry logic for rate limits."""
    import time

    if not GEMINI_API_KEY or _client is None:
        raise RuntimeError("GEMINI_API_KEY not set. Add it to your .env file.")

    for attempt in range(max_retries):
        try:
            response = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e).lower()
            # If rate limited, wait and retry
            if "429" in error_str or "quota" in error_str or "too_many_requests" in error_str:
                wait_time = (2 ** attempt) * 15  # 15s, 30s, 60s
                if attempt < max_retries - 1:
                    time.sleep(wait_time)
                    continue
            # Last attempt or non-rate-limit error: raise
            if attempt == max_retries - 1:
                raise
            time.sleep(2)


def generate_event_package(event_title: str, event_type: str, date: str,
                            time: str, venue: str, audience: str,
                            speaker_name: str = "", extra_context: str = "") -> dict:
    """
    Generates a full event content package from a rough idea.
    Runs 4 Gemini prompts concurrently in parallel to reduce waiting time from ~30s to ~5s.
    Returns a dict with: description, captions (dict), speaker_email, reminders (dict)
    """

    base_context = f"""
Event Title: {event_title}
Event Type: {event_type}
Date: {date}
Time: {time}
Venue: {venue}
Target Audience: {audience}
Speaker (if any): {speaker_name or "TBD"}
Extra Context: {extra_context or "None"}

This event is organized by GDG MCET (Google Developer Group, MCET college chapter),
a student-run tech community.
"""

    desc_prompt = f"""{base_context}
Write a compelling event description (120-160 words) suitable for a college tech
community event page. Tone: energetic, student-friendly, clear on value/takeaways.
Include what attendees will learn or gain. Do not use markdown headers, just plain
paragraph text ready to paste."""

    captions_prompt = f"""{base_context}
Write 3 short social media captions to promote this event, each for a different platform:
1. Instagram (casual, emoji-friendly, punchy, under 60 words, include 3-4 relevant hashtags)
2. LinkedIn (slightly more professional tone, under 70 words, no excessive emojis)
3. WhatsApp broadcast/group announcement (very short, direct, under 40 words, include a clear CTA)

Return ONLY valid JSON in this exact format, no markdown fences, no extra text:
{{"instagram": "...", "linkedin": "...", "whatsapp": "..."}}"""

    email_prompt = f"""{base_context}
Write a warm, professional but concise speaker outreach/invitation email (150-200 words)
inviting {speaker_name or "a potential speaker"} to speak at this event. Include:
- A brief, genuine intro of who GDG MCET is
- Why they specifically are a great fit (keep this generic/adaptable if name unknown)
- What's expected (session length, format)
- A clear next step / call to action
Sign off as 'GDG MCET Organizing Team'. Return plain email text with a subject line
on the first line prefixed with 'Subject: '."""

    reminders_prompt = f"""{base_context}
Create a WhatsApp reminder schedule of exactly 3 messages to be sent to registered
attendees at different times before the event:
1. "1 week before" reminder - build excitement, share what to expect
2. "1 day before" reminder - practical details (time, venue, what to bring)
3. "2 hours before" reminder - final nudge, urgency, live now soon

Each message should be under 50 words, friendly, with relevant emojis.

Return ONLY valid JSON in this exact format, no markdown fences, no extra text:
{{"week_before": "...", "day_before": "...", "hours_before": "..."}}"""

    # Run prompts sequentially — gemini-2.0-flash has generous limits (1500 RPM)
    # but sequential is safer and still fast (~10s total)
    description = _call_gemini(desc_prompt)
    captions_raw = _call_gemini(captions_prompt)
    speaker_email = _call_gemini(email_prompt)
    reminders_raw = _call_gemini(reminders_prompt)

    captions = _safe_json_parse(captions_raw, fallback_keys=["instagram", "linkedin", "whatsapp"])
    reminders = _safe_json_parse(reminders_raw, fallback_keys=["week_before", "day_before", "hours_before"])

    return {
        "description": description,
        "captions": captions,
        "speaker_email": speaker_email,
        "reminders": reminders,
    }


def _safe_json_parse(raw: str, fallback_keys: list) -> dict:
    """Gemini sometimes wraps JSON in markdown fences - strip and parse safely."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: split raw text into N chunks if JSON parsing fails
        return {k: raw for k in fallback_keys}
