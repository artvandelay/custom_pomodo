import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from datetime import datetime, timedelta

# Auto-refresh every second
st_autorefresh(interval=1000, key="timer_refresh")

# Initialize session state
if 'timers' not in st.session_state:
    st.session_state['timers'] = {'Coding': 0, 'Writing': 0, 'Learning': 0, 'Comms': 0}
    st.session_state['start_time'] = None
    st.session_state['active_timer'] = None
    st.session_state['last_active_date'] = datetime.now().date()
if 'weekly' not in st.session_state:
    st.session_state['weekly'] = {'Coding': 0, 'Writing': 0, 'Learning': 0, 'Comms': 0}

# Function to check and stop timer if the day has changed
def check_and_stop_timer():
    if st.session_state['last_active_date'] != datetime.now().date():
        st.session_state['start_time'] = None
        st.session_state['active_timer'] = None
        st.session_state['last_active_date'] = datetime.now().date()

# Timer functions
def start_timer(activity):
    st.session_state['start_time'] = datetime.now()
    st.session_state['active_timer'] = activity
    st.session_state['last_active_date'] = datetime.now().date()

def stop_timer():
    if st.session_state['start_time']:
        elapsed_time = (datetime.now() - st.session_state['start_time']).seconds
        activity = st.session_state['active_timer']
        st.session_state['timers'][activity] += elapsed_time
        st.session_state['weekly'][activity] += elapsed_time
        st.session_state['start_time'] = None
        st.session_state['active_timer'] = None

def reset_day():
    for activity in st.session_state['timers']:
        st.session_state['timers'][activity] = 0

def export_csv():
    data = []
    for activity in st.session_state['weekly']:
        data.append({
            'Activity': activity,
            'Weekly Total (seconds)': st.session_state['weekly'][activity]
        })
    df = pd.DataFrame(data)
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

# Streamlit UI
st.title("Jigar Time Tracker")
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

# Display cumulative time in one row
st.markdown("---")
st.header("Cumulative Time")
cols = st.columns(len(activities))
for idx, activity in enumerate(activities):
    with cols[idx]:
        st.subheader(activity)
        st.write(f"**Today**: {format_time(st.session_state['timers'][activity])}")
        st.write(f"**This Week**: {format_time(st.session_state['weekly'][activity])}")

# Reset Day Button
st.markdown("---")
st.button("Start Next Day", on_click=reset_day)

# Export CSV
st.download_button(
    label="Download Weekly Data as CSV",
    data=export_csv(),
    file_name="weekly_time_data.csv",
    mime="text/csv"
)

st.write("---")
st.markdown("> Track your productivity with a clean and efficient interface. Make the most of your time!")