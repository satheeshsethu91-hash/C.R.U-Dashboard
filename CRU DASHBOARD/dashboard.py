import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px
import os

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="Excel Dashboard", layout="wide")
EXCEL_FILE = "data.xlsx"   # default Excel file for clients

# ----------------------------
# Role Selection
# ----------------------------
role = st.sidebar.radio("Select Mode", ["👨‍💼 Admin", "👥 Client Viewer"])

# ----------------------------
# Admin Mode
# ----------------------------
if role == "👨‍💼 Admin":
    st.title("🔐 Admin Dashboard")
    st.write("Upload/replace the Excel file here. This data will be used in the client view.")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file:
        # Save uploaded file to local repo
        with open(EXCEL_FILE, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("✅ Excel file updated successfully!")
    
    if os.path.exists(EXCEL_FILE):
        st.write("Currently loaded file:")
        st.dataframe(pd.read_excel(EXCEL_FILE, header=0, engine="openpyxl"))

# ----------------------------
# Client Viewer Mode
# ----------------------------
elif role == "👥 Client Viewer":
    st.title("📊 Client Dashboard")
    st.caption("This is a read-only dashboard for clients. Data is pre-loaded from the admin import.")

    if not os.path.exists(EXCEL_FILE):
        st.error("⚠️ No data file found. Please ask admin to upload one.")
    else:
        # ---- Load Excel ----
        df = pd.read_excel(EXCEL_FILE, header=0, engine="openpyxl")

        # ---- Search & Filter ----
        with st.expander("🔎 Search & Filter Data", expanded=True):
            search_term = st.text_input("Search in data")
            filtered_df = df.copy()

            if search_term:
                filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

            gb = GridOptionsBuilder.from_dataframe(filtered_df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            gb.configure_default_column(filter=True, sortable=True, editable=False, resizable=True)
            grid_options = gb.build()

            st.subheader("📋 Data Table")
            AgGrid(
                filtered_df,
                gridOptions=grid_options,
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                theme="streamlit",
                height=400,
                fit_columns_on_grid_load=True
            )

        # ---- Pivot Table ----
        st.subheader("📊 Interactive Pivot Table")

        pivot_col = st.selectbox("Select Column for Pivot (X-axis)", options=df.columns)
        pivot_val = st.selectbox("Select Column for Values (Y-axis)", options=df.columns)
        agg_func = st.selectbox("Aggregation Function", ["count", "sum", "mean", "max", "min"])

        try:
            pivot_df = df.groupby(pivot_col)[pivot_val].agg(agg_func).reset_index()
            fig = px.bar(pivot_df, x=pivot_col, y=pivot_val, title=f"Pivot: {agg_func} of {pivot_val} by {pivot_col}")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(pivot_df, use_container_width=True)
        except Exception as e:
            st.warning(f"Unable to generate pivot: {e}")

        # ---- Insights ----
        st.subheader("📈 Data Insights")
        st.write(f"✅ Total Rows: {len(df)}")
        st.write(f"✅ Total Columns: {len(df.columns)}")

        with st.expander("📌 Column Insights"):
            for col in df.columns:
                st.markdown(f"**{col}**")
                st.write(f"- Unique Values: {df[col].nunique()}")
                st.write(f"- Sample Values: {df[col].dropna().unique()[:5]}")

