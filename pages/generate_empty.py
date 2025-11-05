import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.title("🆕 Generate Empty Schedule")

# Input for month/year
year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.today().year)
month = st.number_input("Month", min_value=1, max_value=12, value=datetime.today().month)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

if st.button("Generate Empty Schedule"):
    # Create empty DataFrame template
    df = pd.DataFrame(columns=["Shift"] + days)
    
    # Example: 9 rows per week (first row can be date numbers)
    df.loc[0] = ["Date"] + [f"{i+1}" for i in range(7)]  # placeholder day numbers
    for i in range(1, 9):
        df.loc[i] = [""] * (len(days)+1)  # empty shifts
    
    st.success(f"Empty schedule for {month}/{year} generated!")
    st.dataframe(df)

    # Optional: Save to Excel
    save_path = f"schedules/{year}-{month:02d}_empty.xlsx"
    os.makedirs("schedules", exist_ok=True)
    df.to_excel(save_path, index=False)
    st.info(f"Saved empty schedule as {save_path}")
