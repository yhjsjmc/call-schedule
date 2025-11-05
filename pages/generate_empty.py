import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

st.set_page_config(page_title="Generate Empty Schedule")
st.title("🗓️ Generate Empty Monthly Schedule")

# -----------------------------
# Inputs
# -----------------------------
input_MMYY = st.text_input("Enter month/year (MMYY)", value=datetime.today().strftime("%m%y"))

weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
names_all = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
names_off = ["", "JUNG", "HOLIDAY"]

# -----------------------------
# Generate weeks aligned to Monday
# -----------------------------
def generate_calendar_weeks(input_MMYY):
    start_date = datetime.strptime(input_MMYY, "%m%y")
    month = start_date.month
    year = start_date.year
    num_days = calendar.monthrange(year, month)[1]

    all_days = [datetime(year, month, day) for day in range(1, num_days + 1)]
    weeks = []
    week = []

    for day in all_days:
        weekday_idx = day.weekday()  # Monday=0
        if len(week) == 0 and weekday_idx != 0:
            week = [None]*weekday_idx  # blank columns until first day
        week.append(day)
        if len(week) == 5:
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)
    return weeks

weeks = generate_calendar_weeks(input_MMYY)

# -----------------------------
# Initialize schedule in session_state
# -----------------------------
if "schedule_df" not in st.session_state:
    data = []
    for w, week in enumerate(weeks):
        for shift in shifts:
            for i, date in enumerate(week):
                data.append({
                    "Week": w+1,
                    "Date": date.strftime("%Y-%m-%d") if date else "",
                    "Day": date.strftime("%A") if date else "",
                    "Shift": shift,
                    "Person": ""
                })
    st.session_state.schedule_df = pd.DataFrame(data)

df = st.session_state.schedule_df.copy()

# -----------------------------
# Display calendar table with selectboxes
# -----------------------------
st.subheader("Assign Shifts")

for w, week in enumerate(weeks):
    st.markdown(f"### Week {w+1}")
    # Header row
    header_cols = st.columns(len(week)+1)
    header_cols[0].markdown("**Shift / Day**")
    for i, date in enumerate(week):
        header_cols[i+1].markdown(f"**{date.strftime('%a %d') if date else ''}**")

    # Rows for each shift
    for shift in shifts:
        row_cols = st.columns(len(week)+1)
        row_cols[0].markdown(f"**{shift}**")
        for i, date in enumerate(week):
            if date is None:
                continue
            idx = df[
                (df["Date"] == date.strftime("%Y-%m-%d")) &
                (df["Shift"] == shift)
            ].index[0]
            options = names_off if shift=="OFF" else names_all
            selected = row_cols[i+1].selectbox(
                "", options,
                index=options.index(df.at[idx, "Person"]) if df.at[idx, "Person"] in options else 0,
                key=f"{date}_{shift}"
            )
            df.at[idx, "Person"] = selected

st.session_state.schedule_df = df.copy()

# -----------------------------
# Display final schedule
# -----------------------------
st.subheader("Schedule DataFrame")
st.dataframe(df)

# -----------------------------
# Save to Excel
# -----------------------------
if st.button("Save Schedule to Excel"):
    os.makedirs("schedules", exist_ok=True)
    filename = f"schedules/{input_MMYY}_schedule.xlsx"
    df.to_excel(filename, index=False)
    st.success(f"Saved schedule to {filename}")
