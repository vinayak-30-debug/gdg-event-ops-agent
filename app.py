"""
GDG MCET Event Platform
A user-friendly event operations system for GDG MCET organizers.
"""
import streamlit as st
from datetime import datetime, date
import agent
import sheets
import whatsapp
import forms

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GDG MCET | Event Platform",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom Clean CSS (User-friendly, Google style, no tacky AI aesthetics) ────
st.markdown("""
<style>
    /* Google / GDG Color Accents & Clean Typography */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header Styling */
    .gdg-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 1.2rem;
        background: #1e232d;
        border-radius: 12px;
        border-left: 5px solid #4285F4;
        margin-bottom: 1.5rem;
    }
    .gdg-title-box h1 {
        font-size: 1.4rem !important;
        font-weight: 700;
        margin: 0;
        color: #ffffff;
    }
    .gdg-title-box p {
        font-size: 0.85rem;
        color: #9aa0a6;
        margin: 0.2rem 0 0 0;
    }
    .gdg-badge {
        background: rgba(66, 133, 244, 0.15);
        color: #8ab4f8;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(66, 133, 244, 0.3);
    }
    
    /* Navigation Bar Styling */
    div[data-testid="stRadio"] > div {
        display: flex;
        gap: 0.5rem;
        background: #171b22;
        padding: 0.4rem;
        border-radius: 10px;
        border: 1px solid #2d333b;
        margin-bottom: 1.5rem;
    }
    div[data-testid="stRadio"] label {
        flex: 1;
        text-align: center;
        background: transparent;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    div[data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #252b36;
        border-color: #4285F4;
        font-weight: 600;
    }
    
    /* Clean Content Cards */
    .clean-card {
        background: #1a1f29;
        border: 1px solid #2d333b;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    .clean-card-title {
        font-size: 1rem;
        font-weight: 600;
        color: #e6edf3;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .clean-card-sub {
        font-size: 0.82rem;
        color: #8b949e;
        margin-bottom: 0.8rem;
    }
    
    /* Metrics box */
    div[data-testid="stMetric"] {
        background: #1a1f29;
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 0.75rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Session State Initialization ─────────────────────────────────────────────
if "package" not in st.session_state:
    st.session_state.package = None
if "event_meta" not in st.session_state:
    st.session_state.event_meta = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "⚡ Event Setup"

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gdg-header">
    <div class="gdg-title-box">
        <h1>GDG MCET Event Platform</h1>
        <p>Google Developer Groups on Campus • MCET</p>
    </div>
    <div class="gdg-badge">Organizer Dashboard</div>
</div>
""", unsafe_allow_html=True)

# ─── Top Navigation Tabs (Changes current page in-place, not opening a new tab) ──
nav_options = [
    "⚡ Event Setup",
    "📄 Event Content",
    "📝 Attendee Registration",
    "📊 RSVPs & Broadcast",
]

# Ensure current page in options
if st.session_state.current_page not in nav_options:
    st.session_state.current_page = nav_options[0]

selected_page = st.radio(
    "Navigation",
    nav_options,
    index=nav_options.index(st.session_state.current_page),
    horizontal=True,
    label_visibility="collapsed",
    key="nav_selection",
)
st.session_state.current_page = selected_page

# ──────────────────────────────────────────────────────────────────────────────
# PAGE 1: EVENT SETUP & GENERATOR
# ──────────────────────────────────────────────────────────────────────────────
if selected_page == "⚡ Event Setup":
    col_form, col_guide = st.columns([3, 2], gap="large")

    with col_form:
        st.markdown("### 📅 Setup New Event")
        st.caption("Provide key details about your upcoming session. The agent will generate ready-to-use content.")

        with st.form("event_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                title = st.text_input("Event Title *", placeholder="e.g. Hands-on Workshop: Flutter Essentials")
                etype = st.selectbox("Event Format *", ["Workshop", "Tech Talk", "Hands-on Lab", "Hackathon", "Study Jam", "Info Session", "Other"])
                edate = st.date_input("Date *", value=date.today())
                etime = st.text_input("Time *", placeholder="e.g. 2:00 PM – 4:30 PM")
            with col_b:
                venue = st.text_input("Venue *", placeholder="e.g. Seminar Hall 2 / Lab 4 / Google Meet")
                audience = st.text_input("Target Audience *", placeholder="e.g. 2nd & 3rd year CSE / IT students")
                speaker = st.text_input("Speaker Name (Optional)", placeholder="e.g. Jane Doe (or leave blank if TBD)")
                
            extra = st.text_area(
                "Additional Topics / Prerequisites (Optional)",
                placeholder="e.g. Attendees should have VS Code installed. Beginner friendly. Certificates provided.",
                height=90,
            )

            generate_btn = st.form_submit_button("✨ Generate Event Package", use_container_width=True, type="primary")

        if generate_btn:
            if not all([title, etype, edate, etime, venue, audience]):
                st.error("Please fill in all required (*) fields.")
            else:
                with st.spinner("Drafting description, social captions, speaker outreach & reminders in parallel..."):
                    try:
                        pkg = agent.generate_event_package(
                            event_title=title,
                            event_type=etype,
                            date=str(edate),
                            time=etime,
                            venue=venue,
                            audience=audience,
                            speaker_name=speaker,
                            extra_context=extra,
                        )
                        st.session_state.package = pkg
                        st.session_state.event_meta = {
                            "title": title,
                            "date": str(edate),
                            "event_type": etype,
                            "time": etime,
                            "venue": venue,
                            "audience": audience,
                            "speaker": speaker,
                        }
                        st.success("✅ Event package generated in ~8 seconds!")
                        st.info("👉 Click on the **'📄 Event Content'** tab above to view and copy your content.")
                    except Exception as err:
                        st.error(f"Generation error: {err}")

    with col_guide:
        st.markdown("### 💡 What Gets Generated")
        st.markdown("""
        When you submit the form, our parallel agent creates:
        
        - **📝 Event Description**: 120–160 words tailored for college tech event posters and portals.
        - **📱 3 Social Captions**:
          - Instagram (emoji-friendly + hashtags)
          - LinkedIn (polished, professional)
          - WhatsApp (concise with clear CTA)
        - **✉️ Speaker Outreach Email**: Ready-to-send invitation with subject and details.
        - **⏰ 3-Stage WhatsApp Reminders**: 1 week before, 1 day before, and 2 hours before.
        """)

        st.divider()

        if st.session_state.event_meta:
            meta = st.session_state.event_meta
            st.markdown("#### 📌 Current Active Event")
            st.markdown(f"""
            - **Title:** {meta['title']}
            - **Date:** {meta['date']} ({meta['time']})
            - **Venue:** {meta['venue']}
            - **Format:** {meta['event_type']}
            """)
        else:
            st.info("No active event generated yet. Fill out the form to get started.")


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 2: EVENT CONTENT HUB
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "📄 Event Content":
    if not st.session_state.package:
        st.info("No content generated yet. Go to **⚡ Event Setup** to generate your event package first.")
        if st.button("➕ Go to Event Setup"):
            st.session_state.current_page = "⚡ Event Setup"
            st.rerun()
    else:
        pkg = st.session_state.package
        meta = st.session_state.event_meta or {}

        st.markdown(f"### 📄 Generated Content for: *{meta.get('title', 'Event')}*")
        st.caption("Copy and customize each item as needed.")

        subtabs = st.tabs(["📝 Description", "📱 Social Media Captions", "✉️ Speaker Email", "⏰ WhatsApp Reminders"])

        # Subtab 1: Description
        with subtabs[0]:
            st.markdown("#### Event Description")
            st.caption("Paste this directly onto your GDG event page, poster, or email newsletter.")
            st.text_area("Event Description", value=pkg.get("description", ""), height=220, label_visibility="collapsed")

        # Subtab 2: Social Media Captions
        with subtabs[1]:
            st.markdown("#### Platform-Tailored Captions")
            captions = pkg.get("captions", {})

            col_ig, col_li = st.columns(2)
            with col_ig:
                st.markdown("**📸 Instagram (Casual & Hashtags)**")
                st.text_area("Instagram", value=captions.get("instagram", ""), height=180, label_visibility="collapsed")
            with col_li:
                st.markdown("**💼 LinkedIn (Professional)**")
                st.text_area("LinkedIn", value=captions.get("linkedin", ""), height=180, label_visibility="collapsed")

            st.markdown("**💬 WhatsApp Broadcast Announcement**")
            st.text_area("WhatsApp Post", value=captions.get("whatsapp", ""), height=100, label_visibility="collapsed")

        # Subtab 3: Speaker Email
        with subtabs[2]:
            st.markdown("#### Speaker Outreach Email")
            st.caption("Personalized invitation letter ready to send to your guest speaker.")
            st.text_area("Speaker Email", value=pkg.get("speaker_email", ""), height=280, label_visibility="collapsed")

        # Subtab 4: Reminders
        with subtabs[3]:
            st.markdown("#### 3-Stage Reminder Schedule")
            st.caption("Messages formatted for WhatsApp broadcast to confirmed attendees.")
            reminders = pkg.get("reminders", {})

            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.markdown("**📅 1 Week Before**")
                st.info(reminders.get("week_before", "No reminder generated"))
            with col_r2:
                st.markdown("**📅 1 Day Before**")
                st.info(reminders.get("day_before", "No reminder generated"))
            with col_r3:
                st.markdown("**⏰ 2 Hours Before**")
                st.info(reminders.get("hours_before", "No reminder generated"))


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 3: ATTENDEE REGISTRATION (Clean attendee-facing form)
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "📝 Attendee Registration":
    col_reg, col_details = st.columns([3, 2], gap="large")
    meta = st.session_state.event_meta

    with col_reg:
        if meta and meta.get("title"):
            st.markdown(f"### 📝 Register for: {meta['title']}")
        else:
            st.markdown("### 📝 Attendee Registration")
        st.caption("Fill in your details below to secure your spot. You will receive updates on WhatsApp.")

        with st.form("public_registration_form", clear_on_submit=True):
            name = st.text_input("Full Name *", placeholder="e.g. Vinayak Sharma")
            phone = st.text_input("WhatsApp Number *", placeholder="e.g. +919876543210", help="Include country code (+91 for India)")
            email = st.text_input("College Email Address *", placeholder="e.g. student@mcet.edu.in")
            year_branch = st.text_input("Year & Department", placeholder="e.g. 3rd Year CSE")

            submit_reg = st.form_submit_button("✅ Submit Registration", use_container_width=True, type="primary")

        if submit_reg:
            if not all([name, phone, email]):
                st.error("Please fill in all required (*) fields.")
            else:
                with st.spinner("Submitting your registration..."):
                    res = forms.register_attendee(name, phone, email, year_branch)
                if res["status"] == "ok":
                    st.success(f"🎉 Thank you, {name.split()[0]}! You are registered. Your status is pending confirmation.")
                    st.balloons()
                else:
                    st.error(f"Failed to record registration: {res['message']}")

    with col_details:
        st.markdown("### 📅 Event Information")
        if meta and meta.get("title"):
            st.info(f"""
            **{meta['title']}**  
            - **Format:** {meta.get('event_type', 'Event')}  
            - **Date:** {meta.get('date', 'TBD')}  
            - **Time:** {meta.get('time', 'TBD')}  
            - **Venue:** {meta.get('venue', 'TBD')}  
            """)
        else:
            st.info("Registration is currently open for upcoming GDG MCET sessions.")

        st.markdown("#### 📋 Registration Process")
        st.markdown("""
        1. **Submit Form:** Your details are instantly saved to the organizer's verified RSVP Sheet.
        2. **Status:** New registrations start as `pending`.
        3. **Confirmation:** The GDG lead confirms your seat and you receive reminder updates directly on WhatsApp!
        """)

        # Live stats if connected
        try:
            _, summary = sheets.get_rsvp_data()
            st.divider()
            c1, c2 = st.columns(2)
            c1.metric("Registered", summary["total_rows"])
            c2.metric("Confirmed", summary["confirmed_count"])
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 4: RSVPs & WHATSAPP BROADCAST
# ──────────────────────────────────────────────────────────────────────────────
elif selected_page == "📊 RSVPs & Broadcast":
    st.markdown("### 📊 RSVP Tracker & WhatsApp Broadcaster")
    st.caption("Live synchronization with your Google Sheet and Twilio WhatsApp messaging.")

    # Top metrics
    if not sheets.is_configured():
        st.warning("⚠️ Google Sheets is not configured yet. Add `service_account.json` to enable live synchronization.")
    else:
        try:
            records, summary = sheets.get_rsvp_data()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Registrations", summary["total_rows"])
            m2.metric("Confirmed Attendees", summary["confirmed_count"])
            m3.metric("Pending Confirmation", summary["status_counts"].get("pending", 0))
            m4.metric("Eligible for WhatsApp", len(summary["confirmed_phones"]))

            st.divider()

            col_table, col_broadcast = st.columns([3, 2], gap="large")

            with col_table:
                st.markdown("#### 📋 Attendee List (from Google Sheet)")
                st.caption("Tip: Edit the 'RSVP Status' to 'confirmed' in Google Sheet to enable WhatsApp blasts.")
                
                import pandas as pd
                if records:
                    df = pd.DataFrame(records)
                    st.dataframe(df, use_container_width=True, height=320)
                else:
                    st.info("No registrations in the sheet yet.")

            with col_broadcast:
                st.markdown("#### 📤 Send WhatsApp Reminder")
                st.caption("Sends scheduled reminders to confirmed attendees.")

                # Choose reminder source
                reminders_dict = {}
                if st.session_state.package and "reminders" in st.session_state.package:
                    reminders_dict = st.session_state.package["reminders"]

                reminder_options = ["1 Week Before", "1 Day Before", "2 Hours Before", "Custom Announcement"]
                selected_reminder = st.selectbox("Select Message Template", reminder_options)

                if selected_reminder == "1 Week Before":
                    default_msg = reminders_dict.get("week_before", "Reminder: Our GDG event is in 1 week! See you there!")
                elif selected_reminder == "1 Day Before":
                    default_msg = reminders_dict.get("day_before", "Reminder: GDG workshop is tomorrow! Bring your laptop.")
                elif selected_reminder == "2 Hours Before":
                    default_msg = reminders_dict.get("hours_before", "Final call: We are starting in 2 hours! Reach the venue on time.")
                else:
                    default_msg = "Hello from GDG MCET! Quick update regarding our upcoming session."

                broadcast_text = st.text_area("Message Content", value=default_msg, height=120)

                confirmed_count = len(summary["confirmed_phones"])
                st.caption(f"🎯 Target recipients: **{confirmed_count} confirmed attendee(s)**")

                send_button = st.button("🚀 Send WhatsApp Broadcast", use_container_width=True, type="primary")

                if send_button:
                    if confirmed_count == 0:
                        st.warning("No confirmed attendees found with phone numbers. Update attendee status to 'confirmed' first.")
                    else:
                        with st.spinner("Sending WhatsApp messages..."):
                            results = whatsapp.send_bulk_reminders(summary["confirmed_phones"], broadcast_text)

                        st.markdown("##### Delivery Results")
                        for r in results:
                            status_badge = "✅" if r["status"] == "sent" else ("🧪" if r["status"] == "simulated" else "⚠️")
                            st.write(f"{status_badge} **{r['to']}**: {r['status']}")

                        st.success(f"Processed {len(results)} message(s). Full log saved to `sent_messages_log.txt`.")

        except Exception as e:
            st.error(f"Error reading Google Sheet: {e}")

st.divider()
st.caption("GDG MCET • Organizer Operations Agent")
