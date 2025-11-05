import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(layout="wide")
st.title("📅 Weekday Call Scheduler")

people = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

# --- Inputs ---
col1, col2 = st.columns(2)
mm_yyyy = col1.text_input("Enter month and year (MMYYYY)", value=datetime.now().strftime("%m%Y"))
try:
    month = int(mm_yyyy[:2])
    year = int(mm_yyyy[2:])
except:
    month = datetime.now().month
    year = datetime.now().year
    st.warning("Invalid MMYYYY input, defaulting to current month/year.")

# --- Build weekday calendar ---
_, days_in_month = calendar.monthrange(year, month)
all_dates = [datetime(year, month, d) for d in range(1, days_in_month + 1)]
weekday_dates = [d for d in all_dates if d.weekday() < 5]

# Split into weeks (Mon–Fri chunks)
weeks = []
week = []
for date in weekday_dates:
    if date.weekday() == 0 and week:
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
        while next_day.weekday() > 4:  # skip weekends
            next_day += timedelta(days=1)
        next_str = next_day.strftime("%Y-%m-%d")
        if next_str not in st.session_state.schedule:
            continue
        if shift_map["CALL"]:
            st.session_state.schedule[next_str]["POST"] = shift_map["CALL"]
        else:
            if st.session_state.schedule[next_str]["POST"]:
                st.session_state.schedule[next_str]["POST"] = ""

# --- Display schedule by week ---
for w_idx, week in enumerate(weeks, start=1):
    st.markdown(f"### Week {w_idx}")
    # Header row
    header_cols = st.columns([2]*5)
    for i, wd in enumerate(weekdays):
        day = next((d for d in week if d.strftime("%A").upper() == wd), None)
        if day:
            header_cols[i].markdown(f"**{wd[:3]} {day.day}**")
        else:
            header_cols[i].markdown("")

    # Shifts rows
    for shift in shifts:
        row_cols = st.columns([2]*5)
        for i, wd in enumerate(weekdays):
            day = next((d for d in week if d.strftime("%A").upper() == wd), None)
            if day:
                dkey = day.strftime("%Y-%m-%d")
                if dkey in st.session_state.schedule:
                    val = st.session_state.schedule[dkey][shift]
                    idx = people.index(val) if val in people else 0
                    choice = row_cols[i].selectbox(
                        "",
                        people,
                        index=idx,
                        key=f"{dkey}_{shift}",
                        label_visibility="collapsed",
                    )
                    st.session_state.schedule[dkey][shift] = choice
            else:
                row_cols[i].markdown("")  # blank cell
    update_post_call()

# --- Output tidy summary ---
st.markdown("### Summary Table")
flat = []
for date_str, shifts_map in st.session_state.schedule.items():
    for s, p in shifts_map.items():
        if p:
            flat.append({"Date": date_str, "Shift": s, "Person": p})
if flat:
    df = pd.DataFrame(flat)
    st.dataframe(df, use_container_width=True)
else:
    st.info("No assignments yet.")
