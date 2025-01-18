import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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

# Local CSV file path
CSV_FILE_PATH = "time_tracker_log.csv"

# Ensure the CSV file exists
def initialize_csv():
    if not os.path.exists(CSV_FILE_PATH):
        df = pd.DataFrame(columns=["Timestamp", "Activity", "Event", "Elapsed Time"])
        df.to_csv(CSV_FILE_PATH, index=False)
    logger.info("CSV initialized or already exists.")

initialize_csv()

# Log an event to the CSV file
def log_event(activity, event, elapsed_time):
    timestamp = datetime.now().strftime("%d %b %Y, %I:%M %p")
    new_entry = {
        "Timestamp": timestamp,
        "Activity": activity,
        "Event": event,
        "Elapsed Time": format_time(elapsed_time) if elapsed_time else "N/A"
    }
    df = pd.read_csv(CSV_FILE_PATH)
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(CSV_FILE_PATH, index=False)
    logger.info(f"Event logged: {new_entry}")

# Function to check and stop timer if the day has changed
def check_and_stop_timer():
    if st.session_state['last_active_date'] != datetime.now().date():
        st.session_state['start_time'] = None
        st.session_state['active_timer'] = None
        st.session_state['last_active_date'] = datetime.now().date()
        logger.info("Date changed. Timer stopped and reset.")

# Timer functions
def start_timer(activity):
    st.session_state['start_time'] = datetime.now()
    st.session_state['active_timer'] = activity
    st.session_state['last_active_date'] = datetime.now().date()
    log_event(activity, "Start", None)
    logger.info(f"Timer started for: {activity}")

def stop_timer():
    if st.session_state['start_time']:
        elapsed_time = (datetime.now() - st.session_state['start_time']).seconds
        activity = st.session_state['active_timer']
        st.session_state['timers'][activity] += elapsed_time
        st.session_state['start_time'] = None
        st.session_state['active_timer'] = None
        log_event(activity, "Stop", elapsed_time)
        logger.info(f"Timer stopped for: {activity}. Elapsed time: {elapsed_time} seconds.")

def reset_day():
    for activity in st.session_state['timers']:
        st.session_state['timers'][activity] = 0
    log_event("All Activities", "Reset Day", None)
    logger.info("Day reset. All timers cleared.")

def erase_csv():
    if os.path.exists(CSV_FILE_PATH):
        os.remove(CSV_FILE_PATH)
        initialize_csv()
        log_event("All Activities", "Erase CSV", None)
        logger.info("CSV file erased and reinitialized.")

# Export lifetime data as CSV
def export_csv():
    df = pd.read_csv(CSV_FILE_PATH)
    logger.info("Exporting CSV data.")
    return df.to_csv(index=False).encode('utf-8')

# Format elapsed time in a readable way
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

# Check and stop timer if the day has changed
check_and_stop_timer()

# Streamlit UI with custom theme
st.markdown(
    """
    <style>
    /* Button hover effects */
    .stButton button:hover {
        color: #ffb6c1; /* Baby pink */
        border: none; /* Remove borders */
    }

    /* Minimal aesthetic fonts */
    body, .stButton button, .stMarkdown, .stHeader, .stSubheader {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 300;
    }

    /* Background and text color adjustments for a VS Code-like theme */
    body {
        background-color: #000000; /* Totally black background */
        color: #d4d4d4; /* VS Code light text */
    }

    .stButton button {
        background-color: #2d2d2d; /* VS Code button background */
        color: #d4d4d4; /* VS Code button text */
    }

    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #d4d4d4; /* VS Code header text */
    }

    .stTable {
        background-color: #252526; /* VS Code table background */
        color: #d4d4d4; /* VS Code table text */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Time Tracker")
# Combine Reset Day and Erase CSV buttons in one row
col1, col2 = st.columns(2)
with col1:
    st.button("Reset Day", on_click=reset_day)
with col2:
    if not st.session_state['confirm_erase']:
        if st.button("Erase CSV"):
            st.session_state['confirm_erase'] = True
    else:
        st.warning("Are you sure you want to erase the CSV file?")
        if st.button("Confirm Erase CSV"):
            erase_csv()
            st.session_state['confirm_erase'] = False
        if st.button("Cancel"):
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
            st.button("Stop", on_click=stop_timer, key=f"stop_{activity}")
        else:
            st.write("Elapsed Time: 0s")
            st.button("Start", on_click=lambda a=activity: start_timer(a), key=f"start_{activity}")

# Show recent activity logged in csv
st.header("Recent Activity Log")
df = pd.read_csv(CSV_FILE_PATH)
if not df.empty:
    recent_entries = df.tail(4)
    st.table(recent_entries[["Timestamp", "Activity", "Event"]])
    logger.info("Displaying recent activity log.")
else:
    st.write("No activity logged yet.")
    logger.info("No activity found in the log.")

# Display cumulative time in one row
st.markdown("---")
st.header("Cumulative Time")
cols = st.columns(len(activities))
for idx, activity in enumerate(activities):
    with cols[idx]:
        st.subheader(activity)
        st.write(f"**Today**: {format_time(st.session_state['timers'][activity])}")
        logger.info(f"{activity} - Today: {st.session_state['timers'][activity]} seconds")

# Export CSV
st.download_button(
    label="Download Lifetime Data as CSV",
    data=export_csv(),
    file_name="lifetime_time_data.csv",
    mime="text/csv"
)

st.write("---")
st.markdown("> Track your productivity with a clean and efficient interface. Make the most of your time!")
