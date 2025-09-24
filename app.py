import streamlit as st
import pandas as pd
import glob
import os
from datetime import datetime, timedelta

# -------------------------------
# Tidy conversion function
# -------------------------------
def convert_schedule_to_tidy(df, base_year=None, base_month=None):
    if base_year is None or base_month is None:
        raise ValueError("Must provide base_year and base_month")

    base_date = datetime(base_year, base_month, 1)
    tidy_data = []
    holiday_dates = set()
    days = df.columns[1:]  # skip first column (shift names)

    # Skip row 0 (weekday headers), then process in 9-row blocks
    for i in range(1, len(df), 9):  # every 9 rows = 1 week
        week = df.iloc[i:i+9].reset_index(drop=True)
        if week.shape[0] < 2:
            continue

        # First row of the block = dates
        date_row = week.iloc[0, 1:].values

        # Skip if blank week
        if all(pd.isna(x) for x in date_row):
            continue

        # Shifts = rows 1–8 of the block
        for row in range(1, week.shape[0]):
            shift_type = str(week.iloc[row, 0]).strip().upper()
            if pd.isna(shift_type):
                continue

            for col_idx, day in enumerate(days):
                date_val = date_row[col_idx]
                cell_val = week.iloc[row, col_idx + 1]

                if pd.notna(cell_val) and pd.notna(date_val):
                    try:
                        day_num = int(date_val)
                        date_obj = base_date + timedelta(days=day_num - 1)
                    except:
                        continue

                    people = [p.strip().upper() for p in str(cell_val).split(',') if p.strip()]

                    if shift_type == "OFF" and any(p.lower() == "holiday" for p in people):
                        holiday_dates.add(date_obj.date())
                        continue

                    for person in people:
                        tidy_data.append({
                            'Date': date_obj.date(),
                            'Day': day,
                            'Shift': shift_type,
                            'Person': person,
                            'IsHoliday': date_obj.date() in holiday_dates
                        })

    tidy_df = pd.DataFrame(tidy_data)

    # Ensure Date is plain date, not Timestamp
    if not tidy_df.empty:
        tidy_df["Date"] = pd.to_datetime(tidy_df["Date"]).dt.date

    return tidy_df


# -------------------------------
# Streamlit App
# -------------------------------
st.title("📅 Call Schedule Viewer")

all_files = glob.glob("schedules/*.xlsx")

if not all_files:
    st.error("No schedules found. Developer: please add Excel files in the 'schedules/' folder.")
else:
    tidy_list = []
    for file in all_files:
        try:
            fname = os.path.basename(file).replace(".xlsx", "")
            year, month = map(int, fname.split("-"))
            df_raw = pd.read_excel(file, header=None)
            tidy = convert_schedule_to_tidy(df_raw, base_year=year, base_month=month)
            if not tidy.empty:
                tidy_list.append(tidy)
        except Exception as e:
            st.error(f"Error reading {file}: {e}")

    if tidy_list:
        full_schedule = pd.concat(tidy_list, ignore_index=True)

        today = datetime.today().date()
        chosen_date = st.date_input("Pick a date", value=today)

        day_schedule = full_schedule[full_schedule["Date"] == chosen_date]

        if not day_schedule.empty:
            st.subheader(f"Schedule for {chosen_date}")

            display_df = day_schedule[["Shift", "Person"]].copy()

            # Build custom HTML table (no headers, no index)
            rows = []
            for _, r in display_df.iterrows():
                shift = r["Shift"]
                person = r["Person"]
                if shift == "CALL":
                    rows.append(f"<tr><td><b>{shift}</b></td><td><b>{person}</b></td></tr>")
                else:
                    rows.append(f"<tr><td>{shift}</td><td>{person}</td></tr>")

            html = f"""
            <table style="width:50%; border-collapse:collapse; font-size:16px;">
                {''.join(rows)}
            </table>
            """

            st.markdown(html, unsafe_allow_html=True)
        else:
            st.warning(f"No schedule found for {chosen_date}")
    else:
        st.error("No valid schedule data could be loaded.")
