import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# --- Configuration ---
people = ["", "Alice", "Bob", "Charlie", "Dana"]
shifts = ["", "DAY", "CALL", "POST"]
year = datetime.now().year
month = datetime.now().month

# --- Calendar Setup ---
first_day = datetime(year, month, 1)
_, days_in_month = calendar.monthrange(year, month)

# Find Monday before or on the first day
first_monday = first_day - timedelta(days=first_day.weekday())
last_day = datetime(year, month, days_in_month)
# Find Sunday after or on the last day
last_sunday = last_day + timedelta(days=(6 - last_day.weekday()))

# All days covering the displayed grid
all_days = [first_monday + timedelta(days=i) for i in range((last_sunday - first_monday).days + 1)]
weeks = [all_days[i:i+7] for i in range(0, len(all_days), 7)]

# --- Initialize Schedule State ---
if "schedule" not in st.session_state:
    st.session_state.schedule = {
        date.strftime("%Y-%m-%d"): {"Person": "", "Shift": ""}
        for date in all_days
    }

# --- Helper Function ---
def update_post_call(date_str):
    """Automatically assign or clear POST following a CALL."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    # If Friday, skip to Monday
    next_day = date + timedelta(days=3 if date.weekday() == 4 else 1)
    next_day_str = next_day.strftime("%Y-%m-%d")

    if next_day_str not in st.session_state.schedule:
        return

    call_person = st.session_state.schedule[date_str]["Person"]
    call_shift = st.session_state.schedule[date_str]["Shift"]

    if call_shift == "CALL" and call_person:
        st.session_state.schedule[next_day_str]["Person"] = call_person
        st.session_state.schedule[next_day_str]["Shift"] = "POST"
    elif call_shift != "CALL" or not call_person:
        # Clear only if the next day is currently POST for that person
        if st.session_state.schedule[next_day_str]["Shift"] == "POST":
            st.session_state.schedule[next_day_str]["Person"] = ""
            st.session_state.schedule[next_day_str]["Shift"] = ""

# --- Streamlit UI ---
st.title(f"📅 {calendar.month_name[month]} {year} Scheduler")

for w, week in enumerate(weeks, start=1):
    st.markdown(f"### Week {w}")
    cols = st.columns(7, gap="large")  # wider spacing
    for i, date in enumerate(week):
        date_str = date.strftime("%Y-%m-%d")
        if date.month == month:
            with cols[i]:
                st.markdown(f"**{date.strftime('%a %d')}**")
                prev_person = st.session_state.schedule[date_str]["Person"]
                prev_shift = st.session_state.schedule[date_str]["Shift"]

                person = st.selectbox(
                    "Person",
                    people,
                    index=people.index(prev_person) if prev_person in people else 0,
                    key=f"person_{date_str}",
                    label_visibility="collapsed"
                )

                shift = st.selectbox(
                    "Shift",
                    shifts,
                    index=shifts.index(prev_shift) if prev_shift in shifts else 0,
                    key=f"shift_{date_str}",
                    label_visibility="collapsed"
                )

                st.session_state.schedule[date_str]["Person"] = person
                st.session_state.schedule[date_str]["Shift"] = shift

                update_post_call(date_str)
        else:
            with cols[i]:
                st.markdown("&nbsp;")  # blank for days outside the month

# --- Display the Schedule Table ---
df = pd.DataFrame.from_dict(st.session_state.schedule, orient="index")
st.dataframe(df)
