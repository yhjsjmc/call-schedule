import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os

st.set_page_config(page_title="Generate Empty Schedule")
st.title("🗓️ Generate Empty Monthly Schedule with CALL → POST Rule")

# -----------------------------
# Inputs
# -----------------------------
input_MMYY = st.text_input("Enter month/year (MMYY)", value=datetime.today().strftime("%m%y"))

# Constants
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

    # Determine weekday index (Mon=0)
    for day in all_days:
        weekday_idx = day.weekday()  # Monday=0
        if len(week) == 0 and weekday_idx != 0:
            # prepend empty columns until the first Monday
            week = [None]*weekday_idx
        week.append(day)
        if len(week) == 5:  # full Mon-Fri week
            weeks.append(week)
            week = []
    if week:
        weeks.append(week)
    return weeks

weeks = generate_calendar_weeks(input_MMYY)

# -----------------------------
# Initialize schedule in session_state
# -----------------------------
if "schedule_data" not in st.session_state:
    st.session_state.schedule_data = []

    for w, week in enumerate(weeks):
        for shift in shifts:
            for i, date in enumerate(week):
                if date is not None:
                    st.session_state.schedule_data.append({
                        "Week": w+1,
                        "Date": date.strftime("%Y-%m-%d"),
                        "Day": date.strftime("%A"),
                        "Shift": shift,
                        "Person": ""
                    })

# Convert to DataFrame
df_schedule = pd.DataFrame(st.session_state.schedule_data)

# Helper: find next weekday row for POST rule
def find_next_weekday_index(current_idx, df):
    current_row = df.iloc[current_idx]
    current_date = datetime.strptime(current_row["Date"], "%Y-%m-%d")
    next_day = current_date + timedelta(days=1)
    # Skip weekends
    while next_day.strftime("%A").upper() not in weekdays:
        next_day += timedelta(days=1)
    # Find index in df for POST of that next day
    next_idx = df[
        (df["Date"] == next_day.strftime("%Y-%m-%d")) &
        (df["Shift"] == "POST")
    ].index
    if len(next_idx) == 0:
        return None
    return next_idx[0]

# -----------------------------
# Display calendar-like table
# -----------------------------
st.subheader("Assign Shifts (CALL → POST updates automatically)")

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
            idx = df_schedule[
                (df_schedule["Date"] == date.strftime("%Y-%m-%d")) &
                (df_schedule["Shift"] == shift)
            ].index[0]

            options = names_off if shift == "OFF" else names_all

            selected = row_cols[i+1].selectbox(
                "", options, key=f"{date}_{shift}",
                index=options.index(df_schedule.at[idx, "Person"]) if df_schedule.at[idx, "Person"] in options else 0
            )

            # Update session_state
            df_schedule.at[idx, "Person"] = selected
            st.session_state.schedule_data[idx]["Person"] = selected

            # ---- CALL → POST logic ----
            if shift == "CALL":
                next_idx = find_next_weekday_index(idx, df_schedule)
                if next_idx is not None:
                    # Update POST next day
                    df_schedule.at[next_idx, "Person"] = selected
                    st.session_state.schedule_data[next_idx]["Person"] = selected

# -----------------------------
# Display schedule
# -----------------------------
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
