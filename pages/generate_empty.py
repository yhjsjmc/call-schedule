import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(page_title="Generate Empty Schedule")
st.title("🗓️ Generate Empty Monthly Schedule (Calendar Style)")

# -----------------------------
# Inputs
# -----------------------------
input_MMYY = st.text_input(
    "Enter month/year (MMYY)",
    value=datetime.today().strftime("%m%y")
)

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

    # Monday of first week
    start_of_calendar = first_day - timedelta(days=first_day.weekday())
    # Friday of last week
    end_of_calendar = last_day + timedelta(days=(4 - last_day.weekday()) % 7)

    all_days = [start_of_calendar + timedelta(days=i) for i in range((end_of_calendar - start_of_calendar).days + 1)]

    weeks = []
    for i in range(0, len(all_days), 7):
        week = [d if d.month == month and d.weekday() < 5 else None for d in all_days[i:i+7]]
        if any(d for d in week):
            weeks.append(week[:5])  # keep only Mon–Fri
    return weeks

weeks = generate_calendar_weeks(input_MMYY)

# -----------------------------
# Initialize schedule DataFrame
# -----------------------------
def create_calendar_schedule_df(weeks):
    data = []
    for w_idx, week in enumerate(weeks):
        for shift in shifts:
            row = {"Week": w_idx + 1, "Shift": shift}
            for day in week:
                col_name = day.strftime("%a %d") if day else ""
                row[col_name] = ""
            data.append(row)
    df = pd.DataFrame(data)
    return df

if "schedule_df" not in st.session_state or st.session_state.get("loaded_month") != input_MMYY:
    st.session_state.schedule_df = create_calendar_schedule_df(weeks)
    st.session_state.loaded_month = input_MMYY

df = st.session_state.schedule_df.copy()

# -----------------------------
# Configure AgGrid
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)

# Dropdown options per cell
for col in df.columns[2:]:  # skip Week and Shift columns
    gb.configure_column(
        col,
        cellEditor='agSelectCellEditor',
        cellEditorParams={'values': names_off}  # will adjust OFF later
    )

# Optional: you can dynamically choose OFF per row if needed
# e.g., detect shift column and assign names_off

grid_options = gb.build()

st.subheader("Assign Shifts (Editable Calendar)")
AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    width='100%',
    fit_columns_on_grid_load=True,
    update_mode='MODEL_CHANGED'
)

st.session_state.schedule_df = df.copy()

# -----------------------------
# Display final dataframe
# -----------------------------
st.subheader("Schedule DataFrame")
st.dataframe(st.session_state.schedule_df, use_container_width=True)

# -----------------------------
# Save button
# -----------------------------
if st.button("Save Schedule to Excel"):
    os.makedirs("schedules", exist_ok=True)
    filename = f"schedules/{input_MMYY}_schedule.xlsx"
    st.session_state.schedule_df.to_excel(filename, index=False)
    st.success(f"Saved schedule to {filename}")
