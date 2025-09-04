import streamlit as st
import pandas as pd

st.set_page_config(page_title="Excel Dashboard", layout="wide")

st.title("📊 MERIT - CRU - Interactive Excel Dashboard")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

if uploaded_file:
    # Load all sheets
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # Sidebar for sheet selection
    st.sidebar.title("📑 Sheets")
    selected_sheet = st.sidebar.radio("Select a sheet", sheet_names)

    # Load selected sheet
    df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

    st.subheader(f"📄 Preview of `{selected_sheet}`")
    
    # Search filter
    search_text = st.text_input("🔍 Search in table")
    if search_text:
        df = df[df.astype(str).apply(lambda row: row.str.contains(search_text, case=False, na=False)).any(axis=1)]

    # Column filters
    with st.expander("⚙️ Advanced Filters"):
        for col in df.columns:
            if df[col].dtype == "object":
                options = df[col].dropna().unique().tolist()
                if len(options) < 50:  # avoid too many checkboxes
                    selected_options = st.multiselect(f"Filter {col}", options)
                    if selected_options:
                        df = df[df[col].isin(selected_options)]
            else:
                min_val, max_val = float(df[col].min()), float(df[col].max())
                selected_range = st.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
                df = df[(df[col] >= selected_range[0]) & (df[col] <= selected_range[1])]

    # Show table
    st.dataframe(df, use_container_width=True)

    # Optional: quick chart
    if st.checkbox("📈 Show Chart for Numeric Columns"):
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        if numeric_cols:
            chart_x = st.selectbox("X-axis", numeric_cols)
            chart_y = st.selectbox("Y-axis", numeric_cols)
            st.line_chart(df.set_index(chart_x)[chart_y])
        else:
            st.info("No numeric columns available for charting.")
