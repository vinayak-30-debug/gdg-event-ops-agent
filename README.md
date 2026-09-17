# 🤖 GDG Event Ops Agent

An AI-powered event operations agent built for the **GDG MCET Organizer Selection Challenge**. Give it a rough event idea and it generates everything an organizer needs to launch, promote, and manage the event — all from a single dashboard.

🔗 **Live Demo:** [gdg-event-agent.onrender.com](https://gdg-event-agent.onrender.com)

---

## ✨ What It Does

| Feature | Description |
|---------|-------------|
| 📝 **Event Description** | Generates a 120–160 word event description tailored for college tech communities |
| 📱 **Social Media Captions** | Platform-specific captions for Instagram, LinkedIn, and WhatsApp |
| ✉️ **Speaker Outreach Email** | Professional invitation email ready to send to guest speakers |
| ⏰ **WhatsApp Reminders** | 3-stage reminder schedule (1 week / 1 day / 2 hours before) |
| 📝 **Attendee Registration** | Built-in registration form that writes directly to Google Sheets |
| 📊 **Live RSVP Tracking** | Real-time attendee data synced from Google Sheets |
| 📤 **WhatsApp Broadcast** | Send reminders to confirmed attendees via Twilio WhatsApp |
| 📁 **Draft & Past Events** | Persistent event storage — review drafts, publish, or browse past events |

## 🧠 Why This Agent

Organizing a single GDG event usually means:
- Writing a description
- Drafting 3 different captions for 3 platforms
- Emailing a speaker
- Manually nudging people to show up
- Repeating all of this for every event

This agent collapses that entire workflow into **one form submission and a few clicks**, while keeping a human in the loop to review and send.

## 🏗️ Architecture

```
app.py          → Streamlit UI (6-tab dashboard), orchestrates everything
agent.py        → Gemini 2.5 Flash API calls with retry logic for content generation
sheets.py       → Google Sheets integration for live RSVP data
whatsapp.py     → Twilio WhatsApp integration (with safe simulation fallback)
forms.py        → Attendee registration form → writes to Google Sheet
event_store.py  → Persistent JSON storage for draft/upcoming/past events
```

### How Generation Works
The agent runs **4 Gemini prompts in parallel** (description, captions, email, reminders) using `ThreadPoolExecutor`, reducing generation time from ~30s to ~8s. Built-in retry with exponential backoff handles free-tier rate limits gracefully.

## 🚀 Setup

### 1. Clone & Install
```bash
git clone https://github.com/vinayak-30-debug/gdg-event-ops-agent.git
cd gdg-event-ops-agent
pip install -r requirements.txt
```

### 2. Environment Variables
```bash
cp .env.example .env
```

**Gemini API Key** (required):
1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create a key → paste into `.env` as `GEMINI_API_KEY`

**Google Sheets** (optional — for live RSVP tracking):
1. Go to [Google Cloud Console](https://console.cloud.google.com) → Create a project → Enable **Google Sheets API** + **Google Drive API**
2. Create a Service Account → download JSON key → save as `service_account.json`
3. Create a Google Sheet named `GDG Event RSVPs` with columns: `Name | Phone | Email | RSVP Status`
4. Share the sheet with the service account email (Editor access)

**Twilio WhatsApp** (optional — for live reminder sending):
1. Sign up at [console.twilio.com](https://console.twilio.com) (free trial works)
2. Go to Messaging → Try WhatsApp → follow sandbox setup
3. Copy Account SID and Auth Token into `.env`

> **Note:** Without Sheets/Twilio configured, the agent still works fully — it simulates RSVP data and logs reminder sends to `sent_messages_log.txt`.

### 3. Run
```bash
streamlit run app.py
```

## 🎬 Demo Flow

1. **⚡ Event Setup** → Fill in event details → click "Generate Event Package"
2. **📄 Event Content** → View generated description, captions, speaker email, and reminders
3. **📝 Registration** → Register attendees (data goes to Google Sheet)
4. **📊 RSVPs & Broadcast** → See live RSVP data → send WhatsApp reminders to confirmed attendees
5. **📁 Draft Events** → Review saved drafts → publish or delete
6. **🕘 Past Events** → Browse completed events and reuse content

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) — clean dashboard UI with Google-style design
- **AI:** [Gemini 2.5 Flash](https://ai.google.dev/) via `google-genai` SDK — parallel content generation
- **Data:** [Google Sheets API](https://developers.google.com/sheets/api) via `gspread` — live RSVP tracking
- **Messaging:** [Twilio WhatsApp API](https://www.twilio.com/whatsapp) — broadcast reminders to attendees
- **Deployment:** [Render](https://render.com/) — free-tier web service

## 📁 Project Structure

```
├── app.py              # Main Streamlit app (6-tab dashboard)
├── agent.py            # Gemini API integration with retry logic
├── sheets.py           # Google Sheets RSVP reader
├── forms.py            # Registration form → Sheets writer
├── whatsapp.py         # Twilio WhatsApp sender (with simulation fallback)
├── event_store.py      # Persistent event storage (draft/upcoming/past)
├── requirements.txt    # Python dependencies
├── .env.example        # Template for environment variables
├── render.yaml         # Render deployment blueprint
├── build.sh            # Render build script
└── .streamlit/
    └── config.toml     # Streamlit server config for deployment
```

## 🔮 Future Improvements

- **Auto-scheduler** — APScheduler / cron to trigger reminders at the right time automatically
- **Slack/Discord** — Additional messaging channels beyond WhatsApp
- **Post-event feedback** — AI agent that summarizes survey responses
- **Direct social posting** — Publish captions to Instagram/LinkedIn via their APIs
- **Analytics dashboard** — Event attendance trends and engagement metrics

---

Built for the **GDG MCET Organizer Selection — AI Agent Build Challenge**.
