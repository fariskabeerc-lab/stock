import streamlit as st
import pandas as pd

# ==========================================
# CUSTOM CSS FOR AESTHETICS & ACTIVE TAB SHADE
# ==========================================
# Removed custom CSS block to revert to default Streamlit tab styling.


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
        "path": "stock ware.xlsx", # UPDATED PATH
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
# COMMON SEARCH BAR (TOP)
# ==========================================
st.title("📦 Inventory Dashboard")
st.markdown("---")

# Input for search query is now global/common
query = st.text_input(
    "🔍 Search for Item Name or Barcode across all inventory:", 
    placeholder="Enter Barcode or Item Description here...",
    label_visibility="visible"
).strip().lower()

# ==========================================
# SEARCH LOGIC AND DISPLAY
# ==========================================
if query:
    st.subheader(f"Search Results for: **'{query}'**")
    
    # 1. Search warehouse stock
    # We ensure that 'itembarcode' and 'description' columns exist before trying to access them
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
            st.markdown("### 🏬 Found in Warehouse Stock")
            st.dataframe(results_stock, use_container_width=True)
        
        # Display Arrival results if found
        if not results_arrival.empty:
            st.markdown("### 🆕 Found in New Arrivals")
            st.dataframe(results_arrival, use_container_width=True)
    else:
        st.warning(f"❌ No matching items found for **'{query}'** in either dataset.")
        
# ==========================================
# TABBED PAGE VIEWS (If no search query is active)
# ==========================================
else:
    # Use st.tabs to create the two main pages below the search bar
    # Using a container here to help enforce standard spacing since custom CSS was removed
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True) # Keeping a small style block to center the tabs.

    tab1, tab2 = st.tabs(["🏬 Warehouse Stock", "🆕 New Arrival"])

    with tab1:
        st.subheader("Current Warehouse Inventory")
        st.write(f"📅 Last Updated: **{data['stock']['date']}**")

        if not stock_df.empty:
            st.dataframe(stock_df, use_container_width=True)
        else:
            st.warning(f"⚠️ Could not display data from **{files['warehouse_stock']['path']}**.")

    with tab2:
        st.subheader("Incoming Inventory (New Shipments)")
        st.write(f"📅 Last Updated: **{data['new_arrival']['date']}**")

        if not arrival_df.empty:
            st.dataframe(arrival_df, use_container_width=True)
        else:
            st.warning(f"⚠️ Could not display data from **{files['new_arrival']['path']}**.")
