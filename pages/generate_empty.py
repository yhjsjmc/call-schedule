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
# Generate Monday-aligned weeks
# -----------------------------
def generate_calendar_weeks(input_MMYY):
    start_date = datetime.strptime(input_MMYY, "%m%y")
    month = start_date.month
    year = start_date.year
    num_days = calendar.monthrange(year, month)[1]

    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, num_days)
    start_of_calendar = first_day - timedelta(days=first_day.weekday())
    end_of_calendar = last_day + timedelta(days=(4 - last_day.weekday()) % 7)
    all_days = [start_of_calendar + timedelta(days=i) for i in range((end_of_calendar - start_of_calendar).days + 1)]

    weeks = []
    for i in range(0, len(all_days), 7):
        week = [d if d.month == month and d.weekday() < 5 else None for d in all_days[i:i+7]]
        if any(d for d in week):
            weeks.append(week[:5])  # Monday–Friday only
    return weeks

weeks = generate_calendar_weeks(input_MMYY)

# -----------------------------
# Initialize schedule
# -----------------------------
if "schedule_df" not in st.session_state or st.session_state.get("loaded_month") != input_MMYY:
    data = []
    for w, week in enumerate(weeks):
        for shift in shifts:
            for i, date in enumerate(week):
                data.append({
                    "Week": w + 1,
                    "Date": date.strftime("%Y-%m-%d") if date else "",
                    "Day": date.strftime("%A") if date else "",
                    "Shift": shift,
                    "Person": ""
                })
    st.session_state.schedule_df = pd.DataFrame(data)
    st.session_state.loaded_month = input_MMYY

df = st.session_state.schedule_df.copy()

# -----------------------------
# Helper functions
# -----------------------------
def find_next_workday(date_str):
    """Return next weekday (skip weekends)."""
    if not date_str:
        return None
    date = datetime.strptime(date_str, "%Y-%m-%d")
    next_day = date + timedelta(days=1)
    while next_day.weekday() >= 5:  # skip Sat/Sun
        next_day += timedelta(days=1)
    next_str = next_day.strftime("%Y-%m-%d")
    if next_str in df["Date"].values:
        return next_str
    return None

def update_post_call_logic(changed_date, new_person):
    """When CALL changes, update the corresponding POST day."""
    next_date = find_next_workday(changed_date)
    if not next_date:
        return
    idx_post = df[(df["Date"] == next_date) & (df["Shift"] == "POST")].index
    if len(idx_post):
        if new_person == "":
            df.at[idx_post[0], "Person"] = ""
        else:
            df.at[idx_post[0], "Person"] = new_person

# -----------------------------
# Display table with dropdowns
# -----------------------------
st.subheader("Assign Shifts")

for w, week in enumerate(weeks):
    st.markdown(f"### Week {w+1}")

    # Header row with wider columns
    header_cols = st.columns([1.2] + [2]*len(week))
    header_cols[0].markdown("**Shift / Day**")
    for i, date in enumerate(week):
        header_cols[i+1].markdown(f"**{date.strftime('%a %d') if date else ''}**")

    # Rows for each shift
    for shift in shifts:
        row_cols = st.columns([1.2] + [2]*len(week))
        row_cols[0].markdown(f"**{shift}**")

        for i, date in enumerate(week):
            if date is None:
                continue
            idx = df[
                (df["Date"] == date.strftime("%Y-%m-%d")) &
                (df["Shift"] == shift)
            ].index[0]
            options = names_off if shift == "OFF" else names_all
            selected = row_cols[i+1].selectbox(
                "",
                options,
                index=options.index(df.at[idx, "Person"]) if df.at[idx, "Person"] in options else 0,
                key=f"{w}_{i}_{shift}"
            )

            # If CALL changed, update POST
            prev_person = df.at[idx, "Person"]
            if shift == "CALL" and selected != prev_person:
                update_post_call_logic(date.strftime("%Y-%m-%d"), selected)

            df.at[idx, "Person"] = selected

st.session_state.schedule_df = df.copy()

# -----------------------------
# Display final dataframe
# -----------------------------
st.subheader("Schedule DataFrame")
st.dataframe(df, use_container_width=True)

# -----------------------------
# Save button
# -----------------------------
if st.button("Save Schedule to Excel"):
    os.makedirs("schedules", exist_ok=True)
    filename = f"schedules/{input_MMYY}_schedule.xlsx"
    df.to_excel(filename, index=False)
    st.success(f"Saved schedule to {filename}")
