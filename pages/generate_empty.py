import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(page_title="Generate Empty Schedule")
st.title("🗓️ Generate Empty Monthly Schedule (Calendar Style)")

# -----------------------------
# Inputs
# -----------------------------
input_MMYY = st.text_input("Enter month/year (MMYY)", value=datetime.today().strftime("%m%y"))

weekdays = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
shifts = ["CALL", "LATE", "EARLY", "4TH", "5TH", "POST", "VACATION", "OFF"]
names_all = ["", "BOSS", "BUSH", "JUNG", "KASS", "LYMAR", "VITA"]
names_off = ["", "JUNG", "HOLIDAY"]

# -----------------------------
# Generate calendar weeks
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
        week = all_days[i:i+7]
        # keep only Mon–Fri, fill None for non-month days
        week_days = [d if d.month == month and d.weekday() < 5 else None for d in week[:5]]
        if any(week_days):
            weeks.append(week_days)
    return weeks

weeks = generate_calendar_weeks(input_MMYY)

# -----------------------------
# Build schedule DataFrame
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
    return pd.DataFrame(data)

if "schedule_df" not in st.session_state or st.session_state.get("loaded_month") != input_MMYY:
    st.session_state.schedule_df = create_calendar_schedule_df(weeks)
    st.session_state.loaded_month = input_MMYY

df = st.session_state.schedule_df.copy()

# -----------------------------
# Configure AgGrid
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)
gb.configure_grid_options(domLayout='normal')
gb.configure_grid_options(suppressHorizontalScroll=False)

# Set dropdown options per column
for col in df.columns[2:]:
    gb.configure_column(
        col,
        cellEditor='agSelectCellEditor',
        cellEditorParams={'values': names_all + names_off}  # simpler: allow all, can filter dynamically later
    )

grid_options = gb.build()

st.subheader("Assign Shifts (Editable Calendar)")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    width='100%',
    update_mode=GridUpdateMode.VALUE_CHANGED,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=False
)

# Save updated values back to session_state
st.session_state.schedule_df = pd.DataFrame(grid_response['data'])

st.subheader("Schedule DataFrame")
st.dataframe(st.session_state.schedule_df, use_container_width=True)

if st.button("Save Schedule to Excel"):
    os.makedirs("schedules", exist_ok=True)
    filename = f"schedules/{input_MMYY}_schedule.xlsx"
    st.session_state.schedule_df.to_excel(filename, index=False)
    st.success(f"Saved schedule to {filename}")
