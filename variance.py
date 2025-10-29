import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Stock & New Arrival Dashboard", layout="wide")

st.title("📦 Warehouse & New Arrival Dashboard")

# ==========================================
# MANUAL FILE DATES (EDIT HERE)
# ==========================================
files = {
    "logistic stock-29-10-2025.xlsx": "2025-10-29",
    "NEW ARRAIVAL-27-OCT-25 (1).xlsx": "2025-10-29"
}

# ==========================================
# FILE UPLOAD SECTION
# ==========================================
st.sidebar.header("📤 Upload Excel Files")

uploaded_stock = st.sidebar.file_uploader("Upload Warehouse Stock File", type=["xlsx"])
uploaded_arrival = st.sidebar.file_uploader("Upload New Arrival File", type=["xlsx"])

# ==========================================
# LOAD EXCEL FUNCTION
# ==========================================
def read_excel(uploaded_file):
    try:
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip()
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return pd.DataFrame()

# ==========================================
# READ BOTH FILES
# ==========================================
stock_df = read_excel(uploaded_stock)
arrival_df = read_excel(uploaded_arrival)

# ==========================================
# DATA STRUCTURE
# ==========================================
data = {
    "stock": {
        "data": stock_df.to_dict(orient="records") if not stock_df.empty else [],
        "date": files["warehouse_stock.xlsx"]
    },
    "new_arrival": {
        "data": arrival_df.to_dict(orient="records") if not arrival_df.empty else [],
        "date": files["new_arrival.xlsx"]
    }
}

# ==========================================
# PAGE NAVIGATION
# ==========================================
page = st.sidebar.radio("📊 Select View", ["🏬 Warehouse Stock", "🆕 New Arrival", "🔍 Search Item"])

# ==========================================
# PAGE 1 — WAREHOUSE STOCK
# ==========================================
if page == "🏬 Warehouse Stock":
    st.header("🏬 Warehouse Stock Data")
    st.write(f"📅 Date: **{data['stock']['date']}**")

    if not stock_df.empty:
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.info("Please upload the warehouse_stock.xlsx file.")

# ==========================================
# PAGE 2 — NEW ARRIVAL
# ==========================================
elif page == "🆕 New Arrival":
    st.header("🆕 New Arrival Data")
    st.write(f"📅 Date: **{data['new_arrival']['date']}**")

    if not arrival_df.empty:
        st.dataframe(arrival_df, use_container_width=True)
    else:
        st.info("Please upload the new_arrival.xlsx file.")

# ==========================================
# PAGE 3 — SEARCH ITEM
# ==========================================
elif page == "🔍 Search Item":
    st.header("🔍 Search by Item Name or Barcode")

    query = st.text_input("Enter Item Name or Barcode").strip().lower()

    if query:
        results_stock = stock_df[
            stock_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                           query in str(row.get("description", "")).lower(), axis=1)
        ] if not stock_df.empty else pd.DataFrame()

        results_arrival = arrival_df[
            arrival_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                             query in str(row.get("description", "")).lower(), axis=1)
        ] if not arrival_df.empty else pd.DataFrame()

        if not results_stock.empty or not results_arrival.empty:
            if not results_stock.empty:
                st.subheader("🏬 Found in Warehouse Stock")
                st.dataframe(results_stock, use_container_width=True)
            if not results_arrival.empty:
                st.subheader("🆕 Found in New Arrivals")
                st.dataframe(results_arrival, use_container_width=True)
        else:
            st.warning("No matching items found in either file.")
    else:
        st.info("Type something to search.")

# ==========================================
# JSON STRUCTURE PREVIEW
# ==========================================
with st.expander("🧾 View JSON Data Structure"):
    st.json(data)
