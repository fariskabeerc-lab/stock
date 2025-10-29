import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Stock & New Arrival Dashboard", layout="wide")

# ==========================================
# MANUAL FILES AND DATES (EDIT HERE)
# ==========================================
files = {
    "logistic stock-29-10-2025.xlsx": "2025-10-29",
    "NEW ARRAIVAL-27-OCT-25 (1).xlsx": "2025-10-29"
}

# ==========================================
# LOAD DATA FUNCTION
# ==========================================
@st.cache_data
def load_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

# ==========================================
# LOAD FILES INTO STRUCTURE
# ==========================================
stock_df = load_excel("warehouse_stock.xlsx")
arrival_df = load_excel("new_arrival.xlsx")

data = {
    "stock": {
        "data": stock_df.to_dict(orient="records"),
        "date": files["warehouse_stock.xlsx"]
    },
    "new_arrival": {
        "data": arrival_df.to_dict(orient="records"),
        "date": files["new_arrival.xlsx"]
    }
}

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
page = st.sidebar.radio("📊 Select View", ["🏬 Warehouse Stock", "📦 New Arrival", "🔍 Search Item"])

# ==========================================
# PAGE 1 — WAREHOUSE STOCK
# ==========================================
if page == "🏬 Warehouse Stock":
    st.title("🏬 Warehouse Stock")
    st.write(f"📅 Date: **{data['stock']['date']}**")

    if not stock_df.empty:
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.warning("No warehouse stock data found.")

# ==========================================
# PAGE 2 — NEW ARRIVAL
# ==========================================
elif page == "📦 New Arrival":
    st.title("📦 New Arrival")
    st.write(f"📅 Date: **{data['new_arrival']['date']}**")

    if not arrival_df.empty:
        st.dataframe(arrival_df, use_container_width=True)
    else:
        st.warning("No new arrival data found.")

# ==========================================
# PAGE 3 — SEARCH ITEM
# ==========================================
elif page == "🔍 Search Item":
    st.title("🔍 Search for Item or Barcode")

    # Search input
    query = st.text_input("Enter Item Name or Barcode").strip().lower()

    if query:
        # Search both datasets
        stock_results = stock_df[
            stock_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                           query in str(row.get("description", "")).lower(), axis=1)
        ]
        arrival_results = arrival_df[
            arrival_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                             query in str(row.get("description", "")).lower(), axis=1)
        ]

        # Display results
        if not stock_results.empty or not arrival_results.empty:
            if not stock_results.empty:
                st.subheader("📦 Found in Warehouse Stock")
                st.dataframe(stock_results, use_container_width=True)
            if not arrival_results.empty:
                st.subheader("🆕 Found in New Arrivals")
                st.dataframe(arrival_results, use_container_width=True)
        else:
            st.warning("No matching items found in either stock or new arrival data.")
    else:
        st.info("Type an item name or barcode to search.")

# ==========================================
# OPTIONAL: SHOW JSON STRUCTURE
# ==========================================
with st.expander("🧾 View JSON Data Structure"):
    st.json(data)
