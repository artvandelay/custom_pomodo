import os
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import logging
from utils import remove_last_entry, initialize_csv, log_event, check_and_stop_timer, start_timer, stop_timer, reset_day, erase_csv, export_csv, format_time

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

STATE_CSV_FILE = "state_tracker.csv"
LOG_CSV_FILE = "time_tracker_log.csv"

# Helper function to load or initialize state CSV
def load_or_initialize_csv(file_path, columns):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        if not df.empty:
            return df
    return pd.DataFrame(columns=columns)

# Helper function to save persistent state to CSV
def save_persistent_state(state_df):
    state_data = {
        "start_time": [st.session_state.get("start_time").isoformat() if st.session_state.get("start_time") else None],
        "active_timer": [st.session_state.get("active_timer")]
    }
    current_data_dict = state_df.to_dict(orient='list')
    if current_data_dict != state_data:
        pd.DataFrame(state_data).to_csv(STATE_CSV_FILE, index=False)

# Helper function to load persistent state from CSV
def load_persistent_state(state_df):
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

# Load or initialize state CSV
state_df = load_or_initialize_csv(STATE_CSV_FILE, ["start_time", "active_timer"])
log_df = load_or_initialize_csv(LOG_CSV_FILE, ["Timestamp", "Activity", "Event"])

# Load persistent state
load_persistent_state(state_df)

initialize_csv()

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

    /* Sleek button design */
    .stButton button {
        background-color: #111;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 14px;
        opacity: 0.5; /* Dim buttons by default */
        transition: opacity 0.3s, background-color 0.3s;
    }

    .stButton button:hover {
        opacity: 1; /* Full opacity on hover */
        background-color: #444; /* Slightly brighter on hover */
    }  

    /* Remove the anchor links next to headers */
    .css-1y0tads a {
        display: none;
    }      
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("# Time Tracker")

# Combine Reset Day and Erase CSV buttons in one row
col1, col2 = st.columns(2)
with col1:
    st.button("Start a New Day", on_click=lambda: reset_day(st))

# Daily Motivational Quote
st.markdown(":violet-background[The agony of procrastination is wastage, just do it]")

# Timer Controls
st.markdown("## Tasks")

# Initialize session state for all activities
if 'active_timer' not in st.session_state:
    st.session_state['active_timer'] = None
if 'timers' not in st.session_state:
    st.session_state['timers'] = {activity: 0 for activity in activities}

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
                st.session_state['timers'][activity] += elapsed_time
                st.session_state['active_timer'] = None
                st.session_state['start_time'] = None
                log_event(activity, "Stop", elapsed_time)
        else:
            if st.button("Start", key=f"start_{activity}"):
                st.session_state['active_timer'] = activity
                st.session_state['start_time'] = datetime.now()
                log_event(activity, "Start", None)

        st.write(f"Total Time: {format_time(st.session_state['timers'][activity])}")

# Save state after actions
save_persistent_state(state_df)

# Show recent activity logged in csv
st.markdown("## Activity Log")
if not log_df.empty:
    recent_entries = log_df.tail(8)
    st.table(recent_entries[["Timestamp", "Activity", "Event"]])
else:
    st.write("No activity logged yet.")

# Remove last entry with confirmation
if st.checkbox("Removal of last entry"):
    if st.button("Confirm removal of last Entry"):
        log_df = log_df[:-1]
        log_df.to_csv(LOG_CSV_FILE, index=False)
        st.write("Last entry removed.")

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
