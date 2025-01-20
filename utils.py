# Refactor initialize_csv, log_event, check_and_stop_timer, start_timer, stop_timer, reset_day, erase_csv, export_csv, format_time

import os
import pandas as pd
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Local CSV file path
CSV_FILE_PATH = "time_tracker_log.csv"

# Ensure the CSV file exists
def initialize_csv():
    if not os.path.exists(CSV_FILE_PATH):
        df = pd.DataFrame(columns=["Timestamp", "Activity", "Event", "Elapsed Time"])
        df.to_csv(CSV_FILE_PATH, index=False)
    logger.info("CSV initialized or already exists.")

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
def check_and_stop_timer(st):
    if st.session_state['last_active_date'] != datetime.now().date():
        st.session_state['start_time'] = None
        st.session_state['active_timer'] = None
        st.session_state['last_active_date'] = datetime.now().date()
        logger.info("Date changed. Timer stopped and reset.")

# Timer functions
def start_timer(st, activity):
    st.session_state['start_time'] = datetime.now()
    st.session_state['active_timer'] = activity
    st.session_state['last_active_date'] = datetime.now().date()
    log_event(activity, "Start", None)
    logger.info(f"Timer started for: {activity}")

def stop_timer(st):
    if st.session_state['start_time']:
        elapsed_time = (datetime.now() - st.session_state['start_time']).seconds
        activity = st.session_state['active_timer']
        st.session_state['timers'][activity] += elapsed_time
        st.session_state['start_time'] = None
        st.session_state['active_timer'] = None
        log_event(activity, "Stop", elapsed_time)
        logger.info(f"Timer stopped for: {activity}. Elapsed time: {elapsed_time} seconds.")

def reset_day(st):
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
def export_csv(FILE_PATH):
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

# Helper function to remove the last entry from the log
def remove_last_entry():
    log_file = "time_tracker_log.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        if not df.empty:
            df = df[:-1]  # Remove the last row
            df.to_csv(log_file, index=False)

