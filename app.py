"""
GDG Event Ops Agent - Streamlit UI
Run with: streamlit run app.py
"""
import streamlit as st
from datetime import datetime
import agent
import sheets
import whatsapp

st.set_page_config(page_title="GDG Event Ops Agent", page_icon="🤖", layout="wide")

st.title("🤖 GDG Event Ops Agent")
st.caption("Feed it a rough event idea → get description, captions, speaker email, "
           "and RSVP-aware WhatsApp reminders. Built for GDG MCET.")

if "package" not in st.session_state:
    st.session_state.package = None
if "event_meta" not in st.session_state:
    st.session_state.event_meta = None

# ---------------- INPUT FORM ----------------
with st.form("event_form"):
    st.subheader("1. Tell the agent about your event")
    col1, col2 = st.columns(2)
    with col1:
        event_title = st.text_input("Event Title*", placeholder="e.g. Intro to Android Dev with Jetpack Compose")
        event_type = st.selectbox("Event Type*", ["Workshop", "Tech Talk", "Hackathon", "Info Session", "Study Jam", "Other"])
        date = st.date_input("Date*")
        time = st.text_input("Time*", placeholder="e.g. 4:00 PM - 6:00 PM")
    with col2:
        venue = st.text_input("Venue*", placeholder="e.g. MCET Seminar Hall / Google Meet")
        audience = st.text_input("Target Audience*", placeholder="e.g. 2nd/3rd year CSE students interested in mobile dev")
        speaker_name = st.text_input("Speaker Name (optional)", placeholder="Leave blank if TBD")
    extra_context = st.text_area("Any extra context? (optional)", placeholder="e.g. This is a beginner-friendly session, part of our Android study jam series")

    submitted = st.form_submit_button("⚡ Generate Event Package", use_container_width=True)

if submitted:
    if not all([event_title, event_type, date, time, venue, audience]):
        st.error("Please fill in all required (*) fields.")
    else:
        with st.spinner("Agent is drafting your event package..."):
            try:
                package = agent.generate_event_package(
                    event_title=event_title, event_type=event_type,
                    date=str(date), time=time, venue=venue,
                    audience=audience, speaker_name=speaker_name,
                    extra_context=extra_context,
                )
                st.session_state.package = package
                st.session_state.event_meta = {"title": event_title, "date": str(date)}
                st.success("Event package generated!")
            except Exception as e:
                st.error(f"Generation failed: {e}")

# ---------------- OUTPUT TABS ----------------
if st.session_state.package:
    pkg = st.session_state.package
    tabs = st.tabs(["📝 Description", "📱 Social Captions", "✉️ Speaker Email", "⏰ Reminders", "📊 RSVP Tracker"])

    with tabs[0]:
        st.subheader("Event Description")
        st.text_area("Ready to paste", pkg["description"], height=200, key="desc_out")

    with tabs[1]:
        st.subheader("Social Media Captions")
        captions = pkg["captions"]
        st.markdown("**Instagram**")
        st.text_area("ig", captions.get("instagram", ""), height=100, key="ig_out", label_visibility="collapsed")
        st.markdown("**LinkedIn**")
        st.text_area("li", captions.get("linkedin", ""), height=100, key="li_out", label_visibility="collapsed")
        st.markdown("**WhatsApp Announcement**")
        st.text_area("wa", captions.get("whatsapp", ""), height=80, key="wa_out", label_visibility="collapsed")

    with tabs[2]:
        st.subheader("Speaker Outreach Email")
        st.text_area("Ready to send", pkg["speaker_email"], height=250, key="email_out")

    with tabs[3]:
        st.subheader("WhatsApp Reminder Schedule")
        reminders = pkg["reminders"]
        st.markdown("**📅 1 Week Before**")
        st.info(reminders.get("week_before", ""))
        st.markdown("**📅 1 Day Before**")
        st.info(reminders.get("day_before", ""))
        st.markdown("**📅 2 Hours Before**")
        st.info(reminders.get("hours_before", ""))

        st.divider()
        st.markdown("#### Send Reminders Now (demo)")
        st.caption("In production this would be triggered by a scheduler at the right time. "
                   "For demo purposes, pick a reminder and send it now to confirmed RSVPs.")

        reminder_choice = st.selectbox("Which reminder to send?",
                                        ["week_before", "day_before", "hours_before"])

        if st.button("📤 Send to confirmed attendees"):
            if not sheets.is_configured():
                st.warning("Google Sheets not configured — showing simulated flow. "
                           "Add service_account.json to enable live RSVP pulling.")
                demo_phones = ["+91XXXXXXXXX1", "+91XXXXXXXXX2"]  # simulated
                results = whatsapp.send_bulk_reminders(demo_phones, reminders.get(reminder_choice, ""))
            else:
                _, summary = sheets.get_rsvp_data()
                phones = summary["confirmed_phones"]
                if not phones:
                    st.warning("No confirmed RSVPs found in the sheet.")
                    results = []
                else:
                    results = whatsapp.send_bulk_reminders(phones, reminders.get(reminder_choice, ""))

            for r in results:
                st.write(f"→ {r['to']}: **{r['status']}**")
            if results:
                st.success(f"Processed {len(results)} reminder(s). Check sent_messages_log.txt for full log.")

    with tabs[4]:
        st.subheader("RSVP Tracker (Live from Google Sheet)")
        if not sheets.is_configured():
            st.warning("Google Sheets isn't connected yet. Add `service_account.json` "
                       "(see README) to pull live RSVP counts here.")
        else:
            try:
                records, summary = sheets.get_rsvp_data()
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Responses", summary["total_rows"])
                c2.metric("Confirmed", summary["confirmed_count"])
                c3.metric("Status Breakdown", ", ".join(f"{k}:{v}" for k, v in summary["status_counts"].items()))
                st.dataframe(records, use_container_width=True)
            except Exception as e:
                st.error(f"Couldn't fetch sheet data: {e}")

st.divider()
st.caption("Built as a GDG MCET Organizer challenge submission — an AI agent GDG MCET could actually use to run events.")
