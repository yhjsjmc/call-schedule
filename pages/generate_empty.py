import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

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

    # Monday of first week
    start_of_calendar = first_day - timedelta(days=first_day.weekday())
    # Friday of last week
    end_of_calendar = last_day + timedelta(days=(4 - last_day.weekday()) % 7)

    all_days = [start_of_calendar + timedelta(days=i) for i in range((end_of_calendar - start_of_calendar).days + 1)]

    weeks = []
    for i in range(0, len(all_days), 7):
        week = all_days[i:i+7]
        week_days = [d if d.month == month and d.weekday() < 5 else None for d in week[:5]]  # Mon–Fri
        if any(week_days):
            weeks.append(week_days)
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
# Assign shifts (same as before)
# -----------------------------
st.subheader("Assign Shifts")

for w, week in enumerate(weeks):
    st.markdown(f"### Week {w+1}")
    header_cols = st.columns(len(week) + 1)
    header_cols[0].markdown("**Shift / Day**")
    for i, date in enumerate(week):
        header_cols[i + 1].markdown(f"**{date.strftime('%a %d') if date else ''}**")

    for shift in shifts:
        row_cols = st.columns(len(week) + 1)
        row_cols[0].markdown(f"**{shift}**")
        for i, date in enumerate(week):
            if date is None:
                continue
            idx = df[
                (df["Date"] == date.strftime("%Y-%m-%d")) &
                (df["Shift"] == shift)
            ].index[0]
            options = names_off if shift == "OFF" else names_all
            selected = row_cols[i + 1].selectbox(
                "",
                options,
                index=options.index(df.at[idx, "Person"]) if df.at[idx, "Person"] in options else 0,
                key=f"{w}_{i}_{shift}"
            )
            df.at[idx, "Person"] = selected

st.session_state.schedule_df = df.copy()

# -----------------------------
# Generate Excel file
# -----------------------------
try:
    excel_bytes = df.to_excel(index=False, engine="openpyxl")
except Exception as e:
    st.error(f"Error generating Excel file: {e}")

# -----------------------------
# Download button
# -----------------------------
if excel_bytes:
    st.download_button(
        "Download Schedule",
        data=excel_bytes,
        file_name=f"{input_MMYY}_schedule.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -----------------------------
# Add minimal CSS for wider dropdowns
# -----------------------------
st.markdown("""
<style>
div.stSelectbox > div > div > div > select {
    min-width: 130px;
}
</style>
""", unsafe_allow_html=True)
