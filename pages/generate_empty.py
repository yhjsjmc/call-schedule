import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("🆕 Generate Empty Monthly Schedule")

# -----------------------------
# Input month/year
# -----------------------------
input_MMYY = st.text_input("Enter month/year (MMYY)", value=datetime.today().strftime("%m%y"))

# -----------------------------
# Constants
# -----------------------------
weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
names_all = ["BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
names_off = ["JUNG", "HOLIDAY"]

# -----------------------------
# Generate empty month schedule
# -----------------------------
def create_empty_month_schedule(input_MMYY):
    start_date = datetime.strptime(input_MMYY, "%m%y")
    month = start_date.month
    year = start_date.year

    next_month = datetime(year + (month // 12), (month % 12) + 1, 1)
    num_days = (next_month - timedelta(days=1)).day
    all_dates = [datetime(year, month, day) for day in range(1, num_days + 1)]
    weekday_dates = [d for d in all_dates if d.strftime("%A").upper() in weekdays]

    # Build schedule dict
    schedule = []
    for date in weekday_dates:
        day_name = date.strftime("%A").upper()
        day_entry = {"Date": date.strftime("%Y-%m-%d"), "Day": day_name}
        for shift in shifts:
            day_entry[shift] = ""  # empty, will be dropdown
        schedule.append(day_entry)
    return pd.DataFrame(schedule)

schedule_df = create_empty_month_schedule(input_MMYY)

st.subheader("Assign Shifts")

# -----------------------------
# Interactive dropdowns
# -----------------------------
for i, row in schedule_df.iterrows():
    st.markdown(f"### {row['Date']} ({row['Day']})")
    cols = st.columns(len(shifts))
    for j, shift in enumerate(shifts):
        if shift == "OFF":
            options = names_off
        else:
            options = names_all
        selected = cols[j].selectbox(shift, options, key=f"{i}_{shift}")
        schedule_df.at[i, shift] = selected

# -----------------------------
# Display schedule
# -----------------------------
st.subheader("Current Schedule Data")
st.dataframe(schedule_df)

# -----------------------------
# Optionally save to Excel
# -----------------------------
if st.button("Save Schedule to Excel"):
    filename = f"schedules/{input_MMYY}_schedule.xlsx"
    schedule_df.to_excel(filename, index=False)
    st.success(f"Saved schedule to {filename}")
