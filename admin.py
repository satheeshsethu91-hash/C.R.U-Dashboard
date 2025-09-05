import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Admin - Excel Uploader", layout="wide")
st.title("👨‍💻 Admin Panel - Upload Excel File")

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, "dashboard_data.xlsx")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ File saved to `{file_path}`. Viewer app will now use the latest data.")
