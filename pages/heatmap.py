import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
from PIL import Image
import os

st.set_page_config(page_title="Heatmap")
st.title("Heatmap based on FTE")

# Input month/year
st.subheader("Most recent until MMYY; Earliest version is 1225")

input_MMYY = st.text_input("Enter month/year (MMYY)", value=datetime.today().strftime("%m%y"))

# Construct filename
heatmap_folder = "heatmaps"  # your folder in repo
filename = f"heatmap{input_MMYY}.png"
filepath = os.path.join(heatmap_folder, filename)

# Check if file exists and display
if os.path.exists(filepath):
    img = Image.open(filepath)
    st.image(img, caption=f"Heatmap for {input_MMYY}", use_column_width=True)
else:
    st.warning(f"No heatmap found for {input_MMYY}. Expected file: {filename}")



