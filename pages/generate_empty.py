import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

st.title("🗓️ Generate Empty Monthly Schedule")

# -----------------------------
# Input month/year
# -----------------------------
input_MMYY = st.text_input("Enter month/year (MMYY)", value=datetime.today().strftime("%m%y"))

# -----------------------------
# Constants
# -----------------------------
weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
names_all = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
names_off = ["", "JUNG", "HOLIDAY"]

# -----------------------------
# Generate calendar-like schedule
# -----------------------------
def create_month_calendar(input_MMYY):
    start_date = datetime.strptime(input_MMYY, "%m%y")
    month = start_date.month
    year = start_date.year

    num_days = calendar.monthrange(year, month)[1]

    # Build weeks (Monday to Friday only)
    weeks = []
    week = []
    for day in range(1, num_days + 1):
        date = datetime(year, month, day)
        if date.strftime("%A").upper() in weekdays:
            week.append(date)
        if len(week) == 5:  # full week
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)  # last partial week

    return weeks

weeks = create_month_calendar(input_MMYY)

# -----------------------------
# Interactive calendar table
# -----------------------------
st.subheader("Assign Shifts (Dropdowns)")

schedule_data = []

for w, week in enumerate(weeks):
    st.markdown(f"### Week {w+1}")
    
    # Header row
    header_cols = st.columns(len(week) + 1)
    header_cols[0].markdown("**Shift / Day**")
    for i, date in enumerate(week):
        header_cols[i+1].markdown(f"**{date.strftime('%a %d')}**")
    
    # Rows for each shift
    for shift in shifts:
        row_cols = st.columns(len(week) + 1)
        row_cols[0].markdown(f"**{shift}**")
        for i, date in enumerate(week):
            options = names_off if shift == "OFF" else names_all
            selected = row_cols[i+1].selectbox(
                "", options, key=f"week{w}_day{date.day}_{shift}"
            )
            schedule_data.append({
                "Week": w+1,
                "Date": date.strftime("%Y-%m-%d"),
                "Day": date.strftime("%A"),
                "Shift": shift,
                "Person": selected
            })

# Convert to DataFrame for display
df_schedule = pd.DataFrame(schedule_data)

st.subheader("Schedule DataFrame")
st.dataframe(df_schedule)

# -----------------------------
# Save to Excel
# -----------------------------
if st.button("Save Schedule to Excel"):
    os.makedirs("schedules", exist_ok=True)
    filename = f"schedules/{input_MMYY}_schedule.xlsx"
    df_schedule.to_excel(filename, index=False)
    st.success(f"Saved schedule to {filename}")
