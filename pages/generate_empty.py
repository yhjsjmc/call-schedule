import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(layout="wide")
st.title("📅 Weekday Call Scheduler")

# --- Constants ---
people = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

# --- Inputs ---
mm_input = st.text_input("Enter month and year (MMYY or MMYYYY)", value=datetime.now().strftime("%m%Y"))

try:
    if len(mm_input) == 4:  # MMYY
        month = int(mm_input[:2])
        year = 2000 + int(mm_input[2:])
    elif len(mm_input) == 6:  # MMYYYY
        month = int(mm_input[:2])
        year = int(mm_input[2:])
    else:
        raise ValueError
except:
    month = datetime.now().month
    year = datetime.now().year
    st.warning("Invalid input, defaulting to current month/year.")

# --- Build weekdays of the month ---
_, days_in_month = calendar.monthrange(year, month)
all_dates = [datetime(year, month, d) for d in range(1, days_in_month + 1)]
weekday_dates = [d for d in all_dates if d.weekday() < 5]  # Mon–Fri only

# --- Split into weeks with 5 columns, None for missing days ---
weeks = []
week = [None]*5
for d in weekday_dates:
    idx = d.weekday()  # 0=Mon
    week[idx] = d
    if idx == 4:  # Friday -> push week
        weeks.append(week)
        week = [None]*5
if any(day is not None for day in week):
    weeks.append(week)

# --- Initialize session state ---
if "schedule" not in st.session_state:
    st.session_state.schedule = {
        d.strftime("%Y-%m-%d"): {shift: "" for shift in shifts} for d in weekday_dates
    }

def update_post_call():
    """If CALL is assigned, next weekday becomes POST for same person."""
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

# --- Render weeks ---
for w_idx, week in enumerate(weeks, start=1):
    st.markdown(f"### Week {w_idx}")
    
    # Header row: weekday + date
    header_cols = st.columns([2]*5)
    for i, d in enumerate(week):
        if d:
            header_cols[i].markdown(f"**{d.strftime('%a %d')}**")
        else:
            header_cols[i].markdown("")
    
    # Shift rows
    for shift in shifts:
        row_cols = st.columns([2]*5)
        for i, d in enumerate(week):
            if d:
                dkey = d.strftime("%Y-%m-%d")
                val = st.session_state.schedule[dkey][shift]
                idx = people.index(val) if val in people else 0
                choice = row_cols[i].selectbox(
                    "", people, index=idx, key=f"{dkey}_{shift}", label_visibility="collapsed"
                )
                st.session_state.schedule[dkey][shift] = choice
            else:
                row_cols[i].markdown("")  # blank cell
    update_post_call()

# --- Summary table ---
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
