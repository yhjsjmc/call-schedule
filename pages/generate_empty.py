import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, timedelta

st.set_page_config(layout="wide")
st.title("📅 Weekday Call Scheduler")

people = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
shifts = ["", "CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]

# --- Inputs ---
col1, col2 = st.columns(2)
month = col1.number_input("Month (1–12)", 1, 12, datetime.now().month)
year = col2.number_input("Year", 2000, 2100, datetime.now().year)

# --- Build weekday calendar ---
first_day = datetime(year, month, 1)
_, days_in_month = calendar.monthrange(year, month)
last_day = datetime(year, month, days_in_month)
first_monday = first_day - timedelta(days=(first_day.weekday() % 7))
# Only weekdays
all_days = [first_monday + timedelta(days=i) for i in range((last_day - first_monday).days + 1)]
all_days = [d for d in all_days if d.weekday() < 5]  # Mon–Fri only

weeks = []
week = []
for d in all_days:
    if d.weekday() == 0 and week:
        weeks.append(week)
        week = []
    week.append(d)
if week:
    weeks.append(week)

# --- Initialize schedule ---
if "schedule" not in st.session_state:
    st.session_state.schedule = {
        date.strftime("%Y-%m-%d"): {"Person": "", "Shift": ""}
        for date in all_days
    }

def update_post_call(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    next_day = date + timedelta(days=1)
    if date.weekday() == 4:  # Friday -> next Monday
        next_day += timedelta(days=2)
    next_key = next_day.strftime("%Y-%m-%d")
    if next_key not in st.session_state.schedule:
        return

    current = st.session_state.schedule[date_str]
    next_entry = st.session_state.schedule[next_key]
    if current["Shift"] == "CALL" and current["Person"]:
        next_entry["Person"] = current["Person"]
        next_entry["Shift"] = "POST"
    else:
        if next_entry["Shift"] == "POST":
            next_entry["Person"] = ""
            next_entry["Shift"] = ""

# --- Display weeks ---
for idx, week in enumerate(weeks, start=1):
    st.markdown(f"#### Week {idx}")
    cols = st.columns(5)
    for i, date in enumerate(week):
        dkey = date.strftime("%Y-%m-%d")
        label = date.strftime("%a %d")
        with cols[i]:
            st.markdown(f"**{label}**")
            s = st.session_state.schedule[dkey]
            p_idx = people.index(s["Person"]) if s["Person"] in people else 0
            sh_idx = shifts.index(s["Shift"]) if s["Shift"] in shifts else 0
            person = st.selectbox("Person", people, index=p_idx, key=f"person_{dkey}", label_visibility="collapsed")
            shift = st.selectbox("Shift", shifts, index=sh_idx, key=f"shift_{dkey}", label_visibility="collapsed")
            st.session_state.schedule[dkey]["Person"] = person
            st.session_state.schedule[dkey]["Shift"] = shift
            update_post_call(dkey)

# --- Output table ---
df = pd.DataFrame.from_dict(st.session_state.schedule, orient="index")
df.index.name = "Date"
st.dataframe(df, use_container_width=True)
