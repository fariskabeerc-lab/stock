import streamlit as st
import pandas as pd

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(page_title="Stock & New Arrival Dashboard", layout="wide")

# ==========================================
# MANUAL FILE NAMES AND DATES
# ==========================================
# ⚠️ Make sure both Excel files are in the same folder as this script.
files = {
    "warehouse_stock": {
        "path": "logistic stock-29-10-2025.xlsx",
        "date": "2025-10-29"
    },
    "new_arrival": {
        "path": "NEW ARRAIVAL-27-OCT-25 (1).xlsx",
        "date": "2025-10-29"
    }
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
        st.error(f"❌ Error loading {file_path}: {e}")
        return pd.DataFrame()

# ==========================================
# READ BOTH FILES
# ==========================================
stock_df = load_excel(files["warehouse_stock"]["path"])
arrival_df = load_excel(files["new_arrival"]["path"])

# ==========================================
# DATA STRUCTURE (for internal use)
# ==========================================
data = {
    "stock": {
        "data": stock_df.to_dict(orient="records"),
        "date": files["warehouse_stock"]["date"]
    },
    "new_arrival": {
        "data": arrival_df.to_dict(orient="records"),
        "date": files["new_arrival"]["date"]
    }
}

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
page = st.sidebar.radio("📊 Select View", ["🏬 Warehouse Stock", "🆕 New Arrival", "🔍 Search Item"])

# ==========================================
# PAGE 1 — WAREHOUSE STOCK
# ==========================================
if page == "🏬 Warehouse Stock":
    st.title("🏬 Warehouse Stock")
    st.write(f"📅 Date: **{data['stock']['date']}**")

    if not stock_df.empty:
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.warning("⚠️ No data found in warehouse_stock.xlsx")

# ==========================================
# PAGE 2 — NEW ARRIVAL
# ==========================================
elif page == "🆕 New Arrival":
    st.title("🆕 New Arrival")
    st.write(f"📅 Date: **{data['new_arrival']['date']}**")

    if not arrival_df.empty:
        st.dataframe(arrival_df, use_container_width=True)
    else:
        st.warning("⚠️ No data found in new_arrival.xlsx")

# ==========================================
# PAGE 3 — SEARCH ITEM
# ==========================================
elif page == "🔍 Search Item":
    st.title("🔍 Search for Item or Barcode")

    query = st.text_input("Enter Item Name or Barcode").strip().lower()

    if query:
        # Search warehouse stock
        results_stock = stock_df[
            stock_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                           query in str(row.get("description", "")).lower(), axis=1)
        ] if not stock_df.empty else pd.DataFrame()

        # Search new arrivals
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
            st.warning("❌ No matching items found.")
    else:
        st.info("Type an item name or barcode to search.")

# ==========================================
# OPTIONAL: SHOW JSON STRUCTURE
# ==========================================
with st.expander("🧾 View JSON Data Structure"):
    st.json(data)
