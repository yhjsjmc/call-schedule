import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Generate Empty Schedule")
st.title("🗓️ Generate Empty Monthly Schedule (AgGrid)")

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
# Generate month calendar as DataFrame
# -----------------------------
def generate_schedule_df(input_MMYY):
    start_date = datetime.strptime(input_MMYY, "%m%y")
    month = start_date.month
    year = start_date.year
    num_days = calendar.monthrange(year, month)[1]

    # Only weekdays
    all_days = [datetime(year, month, d) for d in range(1, num_days + 1)
                if datetime(year, month, d).weekday() < 5]

    # Create a DataFrame: shifts as rows, weekdays as columns
    data = []
    for shift in shifts:
        row = {"Shift": shift}
        for day in all_days:
            col_name = day.strftime("%a %d")
            row[col_name] = ""
        data.append(row)

    df = pd.DataFrame(data)
    return df

# Initialize schedule
if "schedule_df" not in st.session_state or st.session_state.get("loaded_month") != input_MMYY:
    st.session_state.schedule_df = generate_schedule_df(input_MMYY)
    st.session_state.loaded_month = input_MMYY

df = st.session_state.schedule_df.copy()

# -----------------------------
# Configure AgGrid
# -----------------------------
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_default_column(editable=True, resizable=True)

# Set dropdown options per column
for col in df.columns[1:]:
    gb.configure_column(
        col,
        cellEditor='agSelectCellEditor',
        cellEditorParams={'values': names_off if col.startswith("OFF") else names_all}
    )

grid_options = gb.build()

st.subheader("Assign Shifts (Editable Table)")
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=400,
    width='100%',
    fit_columns_on_grid_load=True,
    update_mode='MODEL_CHANGED'
)

# Save back to session_state
st.session_state.schedule_df = pd.DataFrame(grid_response['data'])

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
