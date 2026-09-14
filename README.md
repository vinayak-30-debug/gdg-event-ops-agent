# 🤖 GDG Event Ops Agent

An AI agent built for the **GDG MCET Organizer Selection Challenge**. Give it a
rough event idea and it drafts everything an organizer needs to launch it:

- 📝 A ready-to-publish event description
- 📱 Social media captions (Instagram, LinkedIn, WhatsApp)
- ✉️ A speaker outreach email
- ⏰ A 3-stage WhatsApp reminder schedule (1 week / 1 day / 2 hours before)
- 📊 Live RSVP tracking pulled from a Google Sheet, used to auto-send
  reminders only to confirmed attendees

This isn't a toy chatbot — it's a working tool GDG MCET could plug in and use
for real events.

## Why this agent

Organizing a single event usually means writing a description, drafting 3
different captions for 3 platforms, emailing a speaker, and manually nudging
people to show up — all repeated for every event. This agent collapses that
into one form submission and a few clicks, while still keeping a human in the
loop to review and send.

## Architecture

```
app.py       → Streamlit UI, orchestrates everything
agent.py     → Gemini API calls that generate all event content
sheets.py    → Google Sheets integration for live RSVP data
whatsapp.py  → Twilio WhatsApp integration for reminders (with safe simulation fallback)
```

## Setup

### 1. Clone & install
```bash
pip install -r requirements.txt
```

### 2. Environment variables
Copy `.env.example` to `.env` and fill in:
```bash
cp .env.example .env
```

**Gemini API key** (required):
1. Go to https://aistudio.google.com/apikey
2. Create a key, paste into `.env` as `GEMINI_API_KEY`

**Google Sheets** (optional — for live RSVP tracking):
1. Go to Google Cloud Console → create a project → enable "Google Sheets API"
   and "Google Drive API"
2. Create a Service Account → generate a JSON key → save as
   `service_account.json` in this folder
3. Create a Google Sheet named `GDG Event RSVPs` (or set your own name in
   `.env`) with columns: `Name | Phone | Email | RSVP Status`
4. Share the sheet with the service account's email (found in the JSON file)
   with Editor access

**Twilio WhatsApp** (optional — for live reminder sending):
1. Sign up at https://console.twilio.com (free trial)
2. Go to Messaging → Try it out → Send a WhatsApp message → follow the
   sandbox join instructions
3. Copy your Account SID and Auth Token into `.env`

> Without Sheets/Twilio configured, the agent still runs fully — it
> simulates RSVP data and logs reminder sends to `sent_messages_log.txt`
> instead of failing.

### 3. Run
```bash
streamlit run app.py
```

## Demo flow (for video)
1. Fill in a rough event idea (title, type, date, venue, audience)
2. Click Generate → show the description, captions, and speaker email tabs
3. Show the WhatsApp reminder schedule tab
4. Show the RSVP tracker pulling live data from the Sheet
5. Click "Send to confirmed attendees" and show the log / Twilio delivery

## What I'd extend with more time
- A scheduler (cron / APScheduler) to auto-trigger reminders at the right
  time instead of manual "send now"
- Slack/Discord integration alongside WhatsApp
- A feedback-form agent that summarizes post-event survey responses
- Auto-posting captions directly to Instagram/LinkedIn via their APIs

---
Built for the GDG MCET Organizer Selection – AI Agent Build Challenge.
