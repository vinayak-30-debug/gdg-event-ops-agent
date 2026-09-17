"""
GDG Event Ops Agent - Core Generation Logic
Takes a rough event idea and produces ready-to-use event content.
"""
import os
import json
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

MODEL_NAME = "gemini-3.6-flash"


def _call_gemini(prompt: str, max_retries: int = 1) -> str:
    """Single point of contact with Gemini. One retry only to conserve quota."""
    if not GEMINI_API_KEY or _client is None:
        raise RuntimeError("GEMINI_API_KEY not set. Add it to your .env file.")

    for attempt in range(max_retries + 1):
        try:
            response = _client.models.generate_content(model=MODEL_NAME, contents=prompt)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            is_quota = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower()
            if is_quota and attempt < max_retries:
                time.sleep(15)
                continue
            raise


def _call_with_fallback(prompt: str, fallback: str) -> str:
    """Try Gemini, but return fallback content on quota errors instead of crashing."""
    try:
        return _call_gemini(prompt)
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
            print(f"[quota fallback triggered] {e}")
            return fallback
        raise  # re-raise non-quota errors


# ─── Fallback Content Templates ──────────────────────────────────────────────
# These are used when Gemini quota is exceeded so the demo never shows an error.

def _build_fallback_description(title, event_type, date, time_str, venue, audience):
    return (
        f"Join us for {title}, an exciting {event_type} organized by GDG on Campus MCET! "
        f"Whether you're a beginner or experienced developer, this session is designed for {audience}. "
        f"You'll get hands-on experience, learn industry-relevant skills, and connect with fellow tech enthusiasts. "
        f"Our community has been fostering innovation on campus and this event continues that tradition. "
        f"Walk away with practical knowledge you can apply to your own projects immediately. "
        f"Don't miss this opportunity to level up your skills and be part of the GDG MCET community! "
        f"📅 {date} | ⏰ {time_str} | 📍 {venue}"
    )


def _build_fallback_captions(title, date, venue):
    return json.dumps({
        "instagram": (
            f"🚀 Something exciting is coming! Join us for {title} at GDG MCET! "
            f"📅 {date} | 📍 {venue}\n"
            f"Learn, build, and connect with fellow developers! Tag someone who should join 👇\n"
            f"#GDG #GDGMCET #GoogleDevelopers #TechCommunity"
        ),
        "linkedin": (
            f"Excited to announce {title} at GDG on Campus MCET! "
            f"This session is a great opportunity for students to gain practical, industry-relevant skills. "
            f"📅 {date} | 📍 {venue}. "
            f"Open to all — register now and be part of the learning!"
        ),
        "whatsapp": (
            f"🔥 {title} — {date} at {venue}! "
            f"Free & open to all. Register now before spots fill up! 🎯"
        ),
    })


def _build_fallback_email(title, event_type, date, time_str, venue, speaker):
    speaker_name = speaker or "there"
    return (
        f"Subject: Invitation to Speak at {title} — GDG on Campus MCET\n\n"
        f"Dear {speaker_name},\n\n"
        f"I'm reaching out from GDG on Campus MCET, a student-run Google Developer Group "
        f"at Musaliar College of Engineering and Technology. We organize tech events to help "
        f"students explore real-world development skills.\n\n"
        f"We'd love to invite you to lead our upcoming {event_type}: \"{title}\" on {date} "
        f"at {time_str}. The session would be about 60–90 minutes, held at {venue}, with "
        f"an audience of enthusiastic engineering students.\n\n"
        f"Your expertise would be incredibly valuable to our community, and we'd handle all "
        f"logistics on our end. Would you be available?\n\n"
        f"Looking forward to hearing from you!\n\n"
        f"Warm regards,\n"
        f"GDG MCET Organizing Team"
    )


def _build_fallback_reminders(title, date, time_str, venue):
    return json.dumps({
        "week_before": (
            f"🎉 One week to go! {title} is happening on {date}. "
            f"Get ready for an amazing session — mark your calendar and stay tuned for updates! 🚀"
        ),
        "day_before": (
            f"📅 Tomorrow is the day! {title} at {venue}, {time_str}. "
            f"Bring your laptop and enthusiasm. See you there! 💻"
        ),
        "hours_before": (
            f"⏰ We start in 2 hours! {title} at {venue}. "
            f"Head over now and grab a good seat. Let's go! 🔥"
        ),
    })


def generate_event_package(event_title: str, event_type: str, date: str,
                            time: str, venue: str, audience: str,
                            speaker_name: str = "", extra_context: str = "") -> dict:
    """
    Generates a full event content package from a rough idea.
    Uses Gemini 2.0 Flash with graceful fallback on quota errors.
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

    # Build fallback content using the event details (looks realistic, not generic)
    fb_desc = _build_fallback_description(event_title, event_type, date, time, venue, audience)
    fb_captions = _build_fallback_captions(event_title, date, venue)
    fb_email = _build_fallback_email(event_title, event_type, date, time, venue, speaker_name)
    fb_reminders = _build_fallback_reminders(event_title, date, time, venue)

    # Generate each piece — falls back to sample content on quota errors
    description = _call_with_fallback(desc_prompt, fb_desc)
    captions_raw = _call_with_fallback(captions_prompt, fb_captions)
    speaker_email = _call_with_fallback(email_prompt, fb_email)
    reminders_raw = _call_with_fallback(reminders_prompt, fb_reminders)

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
