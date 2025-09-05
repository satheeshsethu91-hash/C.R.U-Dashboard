import subprocess, sys

# --- Force install packages at runtime if missing ---
for pkg in ["streamlit", "pandas", "openpyxl", "plotly"]:
    try:
        __import__(pkg.split("-")[0])  # "plotly" -> import plotly
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Excel Dashboard", layout="wide")

st.title("📊 Excel Dashboard")

# --- Load Excel file ---
@st.cache_data
def load_excel(file):
    xls = pd.ExcelFile(file)
    sheets = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
        # Ensure merged headers are handled properly
        df.columns = [str(c) for c in df.columns]
        sheets[sheet_name] = df
    return sheets


# --- Session state to hold uploaded file ---
if "sheets" not in st.session_state:
    st.session_state.sheets = None


# --- Tabs for Admin & Viewer ---
tab1, tab2 = st.tabs(["👨‍💻 Admin", "👥 Viewer"])

# --- Admin tab (upload Excel file) ---
with tab1:
    st.subheader("🔑 Admin Panel - Upload Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file:
        st.session_state.sheets = load_excel(uploaded_file)
        st.success("✅ Excel file uploaded successfully! Switch to Viewer tab to explore data.")


# --- Viewer tab (see dashboard) ---
with tab2:
    if st.session_state.sheets is None:
        st.warning("⚠️ No Excel file loaded. Please ask Admin to upload one.")
    else:
        sheets = st.session_state.sheets

        # Sidebar navigation
        st.sidebar.header("📑 Sheets")
        selected_sheet = st.sidebar.radio("Select a sheet", list(sheets.keys()))

        df = sheets[selected_sheet]
        st.subheader(f"📋 Data Preview: {selected_sheet}")

        # --- Search ---
        search_term = st.text_input("🔍 Search text")
        if search_term:
            mask = df.apply(
                lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(),
                axis=1
            )
            df = df[mask]

        # --- Column filters ---
        with st.expander("⚙️ Column Filters"):
            for col in df.columns:
                if df[col].dtype == "object":
                    options = st.multiselect(f"Filter {col}", df[col].dropna().unique())
                    if options:
                        df = df[df[col].isin(options)]

        st.dataframe(df, use_container_width=True)

        # --- Insights ---
        st.subheader("📈 Insights & Charts")
        if df.shape[1] >= 2:  # at least 2 columns
            col_x = st.selectbox("Choose X-axis", df.columns)
            col_y = st.selectbox("Choose Y-axis (numeric)", df.select_dtypes(include="number").columns)

            if col_x and col_y:
                fig = px.bar(df, x=col_x, y=col_y, title=f"{col_y} by {col_x}")
                st.plotly_chart(fig, use_container_width=True)

        # --- Pivot-like summary ---
        st.subheader("📊 Quick Pivot Summary")
        group_col = st.selectbox("Group by column", df.columns)
        agg_col = st.selectbox("Aggregate numeric column", df.select_dtypes(include="number").columns)

        if group_col and agg_col:
            pivot_df = df.groupby(group_col)[agg_col].agg(["count", "mean", "sum"]).reset_index()
            st.dataframe(pivot_df, use_container_width=True)
