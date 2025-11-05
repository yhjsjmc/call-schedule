import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime, timedelta

# -------------------------------
# Tidy conversion function
# -------------------------------
def convert_schedule_to_tidy(df, base_year=None, base_month=None):
    # ... your existing function ...
    pass

# -------------------------------
# Load all schedules
# -------------------------------
def load_all_schedules():
    # ... your existing function ...
    pass

# -------------------------------
# Streamlit Page
# -------------------------------
st.title("📅 Call Schedule Viewer")

full_schedule = load_all_schedules()

if not full_schedule.empty:
    today = datetime.today().date()
    chosen_date = st.date_input("Pick a date", value=today)
    day_schedule = full_schedule[full_schedule["Date"] == chosen_date]

    if not day_schedule.empty:
        st.subheader(f"Schedule for {chosen_date}")
        rows = []
        for _, r in day_schedule.iterrows():
            shift = r["Shift"]
            person = r["Person"]
            if shift == "CALL":
                rows.append(f"<tr><td><b>{shift}</b></td><td><b>{person}</b></td></tr>")
            else:
                rows.append(f"<tr><td>{shift}</td><td>{person}</td></tr>")
        html = f"<table style='width:50%; border-collapse:collapse; font-size:16px;'>{''.join(rows)}</table>"
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.warning(f"No schedule found for {chosen_date}")
else:
    st.error("No valid schedule data could be loaded from schedules/")
