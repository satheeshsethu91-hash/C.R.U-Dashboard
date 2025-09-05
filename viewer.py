import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Excel Dashboard", layout="wide")
st.title("📊 Excel Dashboard")

FILE_PATH = "data/dashboard_data.xlsx"

@st.cache_data
def load_excel(file):
    xls = pd.ExcelFile(file)
    sheets = {}
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
        df.columns = [str(c) for c in df.columns]
        sheets[sheet_name] = df
    return sheets

if not os.path.exists(FILE_PATH):
    st.warning("⚠️ No data available. Please ask Admin to upload a file.")
else:
    sheets = load_excel(FILE_PATH)

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
    if df.shape[1] >= 2:
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
