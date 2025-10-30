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
data = {
    "stock": {
        "data": stock_df,
        "date": files["warehouse_stock"]["date"]
    },
    "new_arrival": {
        "data": arrival_df,
        "date": files["new_arrival"]["date"]
    }
}

# ==========================================
# CONFIGURATION CONSTANTS FOR DISPLAY/FILTERING
# ==========================================
CATEGORY_COLUMN = "Category" # Column used for sidebar filtering
COST_COLUMN = "cost"         # The sensitive column
SELLING_COLUMN = "selling"   # New column name for 'cost' for display
MAX_ITEMS_TO_SHOW_COST = 4   # THE NEW THRESHOLD


# ==========================================
# HELPER FUNCTION FOR DISPLAY FORMATTING
# ==========================================
def create_overview_df(df, show_cost=False):
    """
    Creates a copy of the DataFrame for the main table overview.
    Conditionally includes the cost column based on the show_cost flag.
    """
    if df.empty:
        return pd.DataFrame()
        
    df_display = df.copy()

    # 1. Rename Cost Column to Selling for a clean presentation (if it exists)
    if COST_COLUMN in df_display.columns:
        df_display = df_display.rename(columns={COST_COLUMN: SELLING_COLUMN})

    # 2. Drop the sensitive column if we are NOT showing cost (and it exists)
    if not show_cost and SELLING_COLUMN in df_display.columns:
        df_display = df_display.drop(columns=[SELLING_COLUMN])

    # 3. Drop Category Column (Requested by user)
    if CATEGORY_COLUMN in df_display.columns:
        df_display = df_display.drop(columns=[CATEGORY_COLUMN])
        
    return df_display


# ==========================================
# SIDEBAR FILTERING
# ==========================================
st.sidebar.title("Filter Options")

# --- Category Filter Logic ---
if CATEGORY_COLUMN in stock_df.columns and CATEGORY_COLUMN in arrival_df.columns:
    all_categories = pd.concat([
        stock_df[CATEGORY_COLUMN].dropna().astype(str),
        arrival_df[CATEGORY_COLUMN].dropna().astype(str)
    ]).str.strip().unique().tolist()
    all_categories.sort()
    all_categories.insert(0, "All Categories")

    selected_category = st.sidebar.selectbox(
        "Select Inventory Category", 
        all_categories,
        index=0
    )
    
    if selected_category != "All Categories":
        filtered_stock_df = stock_df[stock_df[CATEGORY_COLUMN].astype(str).str.strip() == selected_category]
        filtered_arrival_df = arrival_df[arrival_df[CATEGORY_COLUMN].astype(str).str.strip() == selected_category]
    else:
        filtered_stock_df = stock_df
        filtered_arrival_df = arrival_df

else:
    st.sidebar.warning(f"⚠️ Cannot find '{CATEGORY_COLUMN}' column. Displaying unfiltered data.")
    selected_category = "All Categories"
    filtered_stock_df = stock_df
    filtered_arrival_df = arrival_df


# ==========================================
# COMMON SEARCH BAR (TOP)
# ==========================================
st.title("📦 Inventory Dashboard")
st.markdown("---")

# Global CSS (Download button hiding remains)
st.markdown("""
<style>
/* Center the tabs for better mobile viewing */
.stTabs [data-baseweb="tab-list"] {
    justify-content: center;
    margin-bottom: 20px;
}
/* 🎯 AGGRESSIVE DOWNLOAD BUTTON HIDING 🎯 */
[data-testid="stDownloadButton"],
[data-testid^="stDataFrameToolbar"] > div:nth-child(2) {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

query = st.text_input(
    "🔍 Search for Item Name or Barcode across all inventory:", 
    placeholder="Enter Barcode or Item Description here...",
    label_visibility="visible"
).strip().lower()

# ==========================================
# SEARCH LOGIC AND DISPLAY
# NOTE: Search results always hide the cost for safety, regardless of size.
# ==========================================
if query:
    st.subheader(f"Search Results for: **'{query}'**")
    
    # 1. Search warehouse stock (using original, unfiltered DF)
    results_stock = stock_df[
        stock_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                                 query in str(row.get("description", "")).lower(), axis=1)
    ] if not stock_df.empty else pd.DataFrame()

    # 2. Search new arrivals (using original, unfiltered DF)
    results_arrival = arrival_df[
        arrival_df.apply(lambda row: query in str(row.get("itembarcode", "")).lower() or
                                     query in str(row.get("description", "")).lower(), axis=1)
    ] if not arrival_df.empty else pd.DataFrame()

    if not results_stock.empty or not results_arrival.empty:
        
        # Display Stock results (Cost is hidden for search results)
        if not results_stock.empty:
            st.markdown("### 🏬 Found in Warehouse Stock")
            st.dataframe(create_overview_df(results_stock, show_cost=False), use_container_width=True)
        
        # Display Arrival results (Cost is hidden for search results)
        if not results_arrival.empty:
            st.markdown("### 🆕 Found in New Arrivals")
            st.dataframe(create_overview_df(results_arrival, show_cost=False), use_container_width=True)
    else:
        st.warning(f"❌ No matching items found for **'{query}'** in either dataset.")
        
# ==========================================
# TABBED PAGE VIEWS (If no search query is active)
# ==========================================
else:
    # Determine the status text based on category selection
    filter_status = f"({f'Filtered by **{selected_category}**' if selected_category != 'All Categories' else 'All Stock'})"

    tab1, tab2 = st.tabs(["🏬 Warehouse Stock", "🆕 New Arrival"])

    with tab1:
        st.subheader("🏬 Warehouse Stock")
        st.write(f"📅 Last Updated: **{data['stock']['date']}** {filter_status}")

        if not filtered_stock_df.empty:
            # Check the new condition: Show cost if item count is below threshold
            show_stock_cost = len(filtered_stock_df) < MAX_ITEMS_TO_SHOW_COST
            
            if show_stock_cost:
                st.success(f"✅ Showing **{SELLING_COLUMN}** price (Item count: {len(filtered_stock_df)})")
            else:
                st.warning(f"⚠️ Hiding **{SELLING_COLUMN}** price (Item count: {len(filtered_stock_df)}). Threshold is {MAX_ITEMS_TO_SHOW_COST} items.")

            # Display filtered stock, applying display formatting and conditional cost visibility
            stock_overview_df = create_overview_df(filtered_stock_df, show_cost=show_stock_cost)
            st.dataframe(stock_overview_df, use_container_width=True)
            
        elif not stock_df.empty:
            st.info(f"No items found in Warehouse Stock for category: **{selected_category}**.")
        else:
            st.warning(f"⚠️ Could not display data from **{files['warehouse_stock']['path']}**.")

    with tab2:
        st.subheader("🆕 New Arrival")
        st.write(f"📅 Last Updated: **{data['new_arrival']['date']}** {filter_status}")

        if not filtered_arrival_df.empty:
            # Check the new condition: Show cost if item count is below threshold
            show_arrival_cost = len(filtered_arrival_df) < MAX_ITEMS_TO_SHOW_COST
            
            if show_arrival_cost:
                st.success(f"✅ Showing **{SELLING_COLUMN}** price (Item count: {len(filtered_arrival_df)})")
            else:
                st.warning(f"⚠️ Hiding **{SELLING_COLUMN}** price (Item count: {len(filtered_arrival_df)}). Threshold is {MAX_ITEMS_TO_SHOW_COST} items.")

            # Display filtered arrival, applying display formatting and conditional cost visibility
            arrival_overview_df = create_overview_df(filtered_arrival_df, show_cost=show_arrival_cost)
            st.dataframe(arrival_overview_df, use_container_width=True)
            
        elif not arrival_df.empty:
            st.info(f"No items found in New Arrivals for category: **{selected_category}**.")
        else:
            st.warning(f"⚠️ Could not display data from **{files['new_arrival']['path']}**.")
