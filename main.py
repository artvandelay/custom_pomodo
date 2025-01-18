import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Initialize session state
if 'timers' not in st.session_state:
    st.session_state['timers'] = {'Coding': 0, 'Writing': 0, 'Learning': 0, 'Comms': 0}
    st.session_state['start_time'] = None
    st.session_state['active_timer'] = None
if 'weekly' not in st.session_state:
    st.session_state['weekly'] = {'Coding': 0, 'Writing': 0, 'Learning': 0, 'Comms': 0}

# Timer functions
def start_timer(activity):
    st.session_state['start_time'] = datetime.now()
    st.session_state['active_timer'] = activity

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

# Streamlit UI
st.title("Simple Productivity and Time Tracker")

# Display clocks
for activity in st.session_state['timers']:
    st.subheader(activity)
    st.text(f"Today: {timedelta(seconds=st.session_state['timers'][activity])}")
    st.text(f"This Week: {timedelta(seconds=st.session_state['weekly'][activity])}")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.session_state['active_timer'] == activity:
            st.button(f"Stop {activity}", on_click=stop_timer)
        else:
            st.button(f"Start {activity}", on_click=lambda a=activity: start_timer(a))
    with col2:
        if st.session_state['active_timer'] == activity:
            st.write("**Running**")

# Reset day button
st.button("Start Next Day", on_click=reset_day)

# Export CSV
st.download_button(
    label="Download Weekly Data as CSV",
    data=export_csv(),
    file_name="weekly_time_data.csv",
    mime="text/csv"
)

# Footer
st.write("---")
st.write("Track your productivity with a simple and efficient interface.")
