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
        # Clean column names by stripping whitespace
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"❌ Error loading {file_path}. Please ensure the file exists and is readable: {e}")
        return pd.DataFrame()

# ==========================================
# READ BOTH FILES
# ==========================================
# Load the dataframes. They will be empty if the file loading fails.
stock_df = load_excel(files["warehouse_stock"]["path"])
arrival_df = load_excel(files["new_arrival"]["path"])

# ==========================================
# DATA STRUCTURE (for internal use)
# ==========================================
# This structure isn't strictly necessary for the app but is good for debugging/display
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
    st.write(f"📅 Last Updated: **{data['stock']['date']}**")

    if not stock_df.empty:
        # Display the main stock dataframe
        st.dataframe(stock_df, use_container_width=True)
    else:
        st.warning(f"⚠️ Could not display data from **{files['warehouse_stock']['path']}**.")

# ==========================================
# PAGE 2 — NEW ARRIVAL
# ==========================================
elif page == "🆕 New Arrival":
    st.title("🆕 New Arrival")
    st.write(f"📅 Last Updated: **{data['new_arrival']['date']}**")

    if not arrival_df.empty:
        # Display the new arrival dataframe
        st.dataframe(arrival_df, use_container_width=True)
    else:
        st.warning(f"⚠️ Could not display data from **{files['new_arrival']['path']}**.")

# ==========================================
# PAGE 3 — SEARCH ITEM
# ==========================================
elif page == "🔍 Search Item":
    st.title("🔍 Search Item or Barcode")
    st.markdown("Search across both **Warehouse Stock** and **New Arrivals** datasets.")

    # Input for search query
    query = st.text_input("Enter Item Name or Barcode", placeholder="e.g., 87654321 or Blue T-Shirt").strip().lower()

    if query:
        # Search function logic (using 'itembarcode' and 'description' columns)
        
        # 1. Search warehouse stock
        results_stock = stock_df[
            stock_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                                       query in str(row.get("description", "")).lower(), axis=1)
        ] if not stock_df.empty else pd.DataFrame()

        # 2. Search new arrivals
        results_arrival = arrival_df[
            arrival_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                                         query in str(row.get("description", "")).lower(), axis=1)
        ] if not arrival_df.empty else pd.DataFrame()

        if not results_stock.empty or not results_arrival.empty:
            
            # Display Stock results if found
            if not results_stock.empty:
                st.subheader("🏬 Results in Warehouse Stock")
                st.dataframe(results_stock, use_container_width=True)
            
            # Display Arrival results if found
            if not results_arrival.empty:
                st.subheader("🆕 Results in New Arrivals")
                st.dataframe(results_arrival, use_container_width=True)
        else:
            st.warning(f"❌ No matching items found for **'{query}'** in either dataset.")
    else:
        st.info("Type an item name or barcode into the search box above to begin.")

# ==========================================
# OPTIONAL: SHOW JSON STRUCTURE
# ==========================================
with st.expander("🧾 View JSON Data Structure (Debugging Only)"):
    st.json(data)
