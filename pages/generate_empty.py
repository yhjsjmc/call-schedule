import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📅 Weekday Call Scheduler")

people = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

# --- Inputs ---
col1, col2 = st.columns(2)
month = col1.number_input("Month (1–12)", 1, 12, datetime.now().month)
year = col2.number_input("Year", 2000, 2100, datetime.now().year)

# --- Build weekday calendar ---
first_day = datetime(year, month, 1)
_, days_in_month = calendar.monthrange(year, month)
last_day = datetime(year, month, days_in_month)

# Get all weekdays for this month only
all_dates = [datetime(year, month, d) for d in range(1, days_in_month + 1)]
weekday_dates = [d for d in all_dates if d.weekday() < 5]  # 0=Mon, 4=Fri

# Split into weeks (Mon–Fri chunks)
weeks = []
week = []
for date in weekday_dates:
    if date.weekday() == 0 and week:  # New week when Monday appears
        weeks.append(week)
        week = []
    week.append(date)
if week:
    weeks.append(week)

# --- Initialize session state ---
if "schedule" not in st.session_state:
    st.session_state.schedule = {
        date.strftime("%Y-%m-%d"): {shift: "" for shift in shifts}
        for date in weekday_dates
    }

def update_post_call():
    """If a day is CALL, next weekday is POST for the same person."""
    for date_str, shift_map in st.session_state.schedule.items():
        date = datetime.strptime(date_str, "%Y-%m-%d")
        next_day = date + timedelta(days=1)
        # Skip to Monday if next day is weekend
        while next_day.weekday() > 4:
            next_day += timedelta(days=1)
        next_str = next_day.strftime("%Y-%m-%d")
        if next_str not in st.session_state.schedule:
            continue
        if shift_map["CALL"]:
            st.session_state.schedule[next_str]["POST"] = shift_map["CALL"]
        else:
            # Clear POST if no CALL assigned
            if st.session_state.schedule[next_str]["POST"]:
                st.session_state.schedule[next_str]["POST"] = ""

# --- Display schedule ---
for w_idx, week in enumerate(weeks, start=1):
    st.markdown(f"### Week {w_idx}")
    cols = st.columns([2, 2, 2, 2, 2])  # widen columns
    week_dates = {wd.strftime("%A").upper(): wd for wd in week}

    for shift in shifts:
        st.markdown(f"**{shift}**")
        row_cols = st.columns([2, 2, 2, 2, 2])
        for i, wd in enumerate(weekdays):
            if wd in week_dates:
                date = week_dates[wd]
                dkey = date.strftime("%Y-%m-%d")
                val = st.session_state.schedule[dkey][shift]
                idx = people.index(val) if val in people else 0
                chosen = row_cols[i].selectbox(
                    wd[:3],
                    people,
                    index=idx,
                    key=f"{dkey}_{shift}",
                    label_visibility="collapsed",
                )
                st.session_state.schedule[dkey][shift] = chosen
            else:
                row_cols[i].markdown("")  # blank cell for missing day
    update_post_call()

# --- Output dataframe ---
st.markdown("### Summary Table")
flat = []
for date_str, shifts_map in st.session_state.schedule.items():
    for s, p in shifts_map.items():
        if p:
            flat.append({"Date": date_str, "Shift": s, "Person": p})
st.dataframe(pd.DataFrame(flat), use_container_width=True)
