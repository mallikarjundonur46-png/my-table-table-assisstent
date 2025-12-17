import streamlit as st
from datetime import datetime
import pandas as pd
from database import (
    create_users_table,
    add_user,
    verify_user,
    create_timetable_table,
    add_timetable_entry,
    get_user_timetable,
    clear_day_timetable
)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="College Timetable App", layout="centered")
st.title("📚 College Timetable App")

# ---------------- INITIALIZE DATABASE ----------------
create_users_table()
create_timetable_table()

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# =====================================================
# 🔐 AUTH SECTION (ONLY WHEN NOT LOGGED IN)
# =====================================================
if not st.session_state.logged_in:

    auth_choice = st.sidebar.selectbox("Login / Register", ["Login", "Register"])

    # -------- REGISTER --------
    if auth_choice == "Register":
        st.subheader("📝 Register")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Register"):
            if new_user and new_pass:
                success = add_user(new_user, new_pass)
                if success:
                    st.success("✅ Registered successfully! Please login.")
                else:
                    st.error("❌ Username already exists!")
            else:
                st.warning("⚠️ Enter username and password")

    # -------- LOGIN --------
    elif auth_choice == "Login":
        st.subheader("🔐 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()   # 🔥 THIS FIXES PAGE NAVIGATION
            else:
                st.error("❌ Incorrect username or password")

# =====================================================
# 🏠 MAIN APP (ONLY AFTER LOGIN)
# =====================================================
else:
    # -------- LOGOUT --------
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    username = st.session_state.username

    # Sidebar menu AFTER login
    menu = st.sidebar.selectbox(
        "Menu",
        ["Home", "Add / Edit Timetable", "Full Week Timetable"]
    )

    user_timetable = get_user_timetable(username)

    # ---------------- HOME ----------------
    if menu == "Home":
        st.subheader(f"👋 Welcome, {username}")
        st.subheader("📅 Today")

        today = datetime.now().strftime("%A").lower()

        if today not in user_timetable:
            st.warning("No timetable for today!")
        else:
            now = datetime.now().strftime("%H:%M")
            current = "No class now"
            next_class = "No more classes today"

            for i, cls in enumerate(user_timetable[today]):
                if cls["start"] <= now <= cls["end"]:
                    current = "🛑 Break" if cls["subject"].lower() == "break" else cls["subject"]
                    if i + 1 < len(user_timetable[today]):
                        next_class = user_timetable[today][i + 1]["subject"]
                    break
                if cls["start"] > now and next_class == "No more classes today":
                    next_class = cls["subject"]

            st.info(f"🕒 Current: **{current}**")
            st.info(f"➡️ Next: **{next_class}**")

    # ---------------- ADD / EDIT ----------------
    elif menu == "Add / Edit Timetable":
        st.subheader("➕ Add / Edit Timetable")

        day = st.selectbox(
            "Select Day",
            ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
        )

        count = st.number_input(
            "Number of periods (including breaks)",
            min_value=1,
            max_value=12,
            step=1
        )

        period_data = []

        for i in range(int(count)):
            st.markdown(f"### Period {i + 1}")
            start = st.text_input("Start Time (HH:MM)", key=f"s{i}")
            end = st.text_input("End Time (HH:MM)", key=f"e{i}")
            subject = st.text_input("Subject (Use 'Break' for breaks)", key=f"sub{i}")

            if start and end and subject:
                period_data.append((start, end, subject))

        if st.button("💾 Save Timetable"):
            clear_day_timetable(username, day)
            for start, end, subject in period_data:
                add_timetable_entry(username, day, start, end, subject)
            st.success("✅ Timetable saved successfully!")

    # ---------------- FULL WEEK ----------------
    elif menu == "Full Week Timetable":
        st.subheader("📅 Full Week Timetable")

        if not user_timetable:
            st.warning("No timetable data available.")
        else:
            for day, periods in user_timetable.items():
                st.markdown(f"## {day.capitalize()}")
                df = pd.DataFrame(periods)
                df.columns = ["Start", "End", "Subject"]
                st.table(df)