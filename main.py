import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import logging
from utils import initialize_csv, log_event, check_and_stop_timer, start_timer, stop_timer, reset_day, erase_csv, export_csv, format_time
import openai

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

STATE_CSV_FILE = "state_tracker.csv"

# Helper function to save persistent state to CSV
def save_persistent_state():
    state_data = {
        "start_time": [st.session_state.get("start_time").isoformat() if st.session_state.get("start_time") else None],
        "active_timer": [st.session_state.get("active_timer")]
    }
    pd.DataFrame(state_data).to_csv(STATE_CSV_FILE, index=False)

# Helper function to load persistent state from CSV
def load_persistent_state():
    if os.path.exists(STATE_CSV_FILE):
        state_df = pd.read_csv(STATE_CSV_FILE)
        if not state_df.empty:
            start_time_str = state_df.iloc[0]["start_time"]
            st.session_state["start_time"] = datetime.fromisoformat(start_time_str) if pd.notna(start_time_str) else None
            st.session_state["active_timer"] = state_df.iloc[0]["active_timer"]

# Auto-refresh every second
st_autorefresh(interval=1000, key="timer_refresh")

# Initialize session state
if 'timers' not in st.session_state:
    st.session_state['timers'] = {'Coding': 0, 'Writing': 0, 'Learning': 0, 'Comms': 0}
    st.session_state['start_time'] = None
    st.session_state['active_timer'] = None
    st.session_state['last_active_date'] = datetime.now().date()
if 'confirm_erase' not in st.session_state:
    st.session_state['confirm_erase'] = False

# Load persistent state
load_persistent_state()

initialize_csv()

if st.session_state['last_active_date'] != datetime.now().date():
    check_and_stop_timer(st)

# Streamlit UI with custom theme
st.markdown(
    """
    <style>
    .main { background-color: #f3f6f9; color: #2C3E50; }
    .block-container { padding: 2rem; max-width: 800px; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; color: #2C3E50; }
    .stButton button { background-color: #e0e0e0; color: black; border-radius: 8px; padding: 0.5rem 1rem; font-size: 16px; border: 1px solid #cfd8dc; }
    .stButton button:hover { background-color: #d6d6d6; }
    .stTable { font-family: 'Helvetica Neue', sans-serif; color: #2C3E50; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Jigar Time Tracker")

# Combine Reset Day and Erase CSV buttons in one row
col1, col2 = st.columns(2)
with col1:
    st.button("Reset Day", on_click=lambda: reset_day(st))
with col2:
    if not st.session_state['confirm_erase']:
        if st.button("Erase CSV"):
            st.session_state['confirm_erase'] = True
    else:
        st.warning("Are you sure you want to erase the CSV file?")
        if st.button("Confirm Erase CSV"):
            erase_csv()
            st.session_state['confirm_erase'] = False
        elif st.button("Cancel"):
            st.session_state['confirm_erase'] = False

st.markdown("---")

# Timer Controls
st.header("Timers")

# Display all timers in one row
activities = ["Coding", "Writing", "Learning", "Comms"]
cols = st.columns(len(activities))

for idx, activity in enumerate(activities):
    with cols[idx]:
        st.subheader(activity)
        if st.session_state['active_timer'] == activity:
            elapsed_time = (datetime.now() - st.session_state['start_time']).seconds
            st.write(f"Elapsed Time: {format_time(elapsed_time)}")
            if st.button("Stop", key=f"stop_{activity}"):
                stop_timer(st)
                st.session_state['active_timer'] = None
                st.session_state['start_time'] = None
        else:
            if st.button("Start", key=f"start_{activity}"):
                start_timer(st, activity)
                st.session_state['active_timer'] = activity
                st.session_state['start_time'] = datetime.now()

# Save state after actions
save_persistent_state()

# Show recent activity logged in csv
st.header("Recent Activity Log")
df = pd.read_csv("time_tracker_log.csv")
if not df.empty:
    recent_entries = df.tail(4)
    st.table(recent_entries[["Timestamp", "Activity", "Event"]])
else:
    st.write("No activity logged yet.")

# Daily Motivational Quote
st.markdown("---")
st.write("The agony of procrastination is wastage, just do it.")

# Display cumulative time in one row
st.markdown("---")
st.header("Cumulative Time")
cols = st.columns(len(activities))
for idx, activity in enumerate(activities):
    with cols[idx]:
        st.subheader(activity)
        st.write(f"**Today**: {format_time(st.session_state['timers'][activity])}")

# Export CSV
st.download_button(
    label="Download Lifetime Data as CSV",
    data=export_csv(),
    file_name="lifetime_time_data.csv",
    mime="text/csv"
)

st.write("---")
st.markdown("> Track your productivity with a clean and efficient interface. Make the most of your time!")
