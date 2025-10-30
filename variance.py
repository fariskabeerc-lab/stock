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
        "data": stock_df, # Store DF directly for easier use later
        "date": files["warehouse_stock"]["date"]
    },
    "new_arrival": {
        "data": arrival_df, # Store DF directly for easier use later
        "date": files["new_arrival"]["date"]
    }
}

# ==========================================
# CONFIGURATION CONSTANTS FOR DISPLAY/FILTERING
# ==========================================
CATEGORY_COLUMN = "Category" # Column used for sidebar filtering
COST_COLUMN = "cost"         # The sensitive column to be hidden
SELLING_COLUMN = "selling"   # New column name for 'cost' for display


# ==========================================
# HELPER FUNCTION FOR DISPLAY FORMATTING
# ==========================================
def create_overview_df(df):
    """
    Creates a copy of the DataFrame for the main table overview.
    It drops the Category column and renames 'cost' to 'selling' for presentation
    *before* dropping the sensitive 'cost' data from the overview.
    """
    if df.empty:
        return pd.DataFrame()
        
    df_display = df.copy()

    # 1. Rename Cost Column to Selling for a clean presentation
    if COST_COLUMN in df_display.columns:
        df_display = df_display.rename(columns={COST_COLUMN: SELLING_COLUMN})

    # 2. Drop the sensitive 'selling' (original 'cost') column from the OVERVIEW
    if SELLING_COLUMN in df_display.columns:
        # Note: We are dropping the *renamed* column from the overview
        df_display = df_display.drop(columns=[SELLING_COLUMN])

    # 3. Drop Category Column (Requested by user)
    if CATEGORY_COLUMN in df_display.columns:
        df_display = df_display.drop(columns=[CATEGORY_COLUMN])
        
    return df_display


# ==========================================
# SIDEBAR FILTERING
# (UNMODIFIED)
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
# (UNMODIFIED)
# ==========================================
st.title("📦 Inventory Dashboard")
st.markdown("---")

# Global CSS (UNMODIFIED)
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
# (MODIFIED to use the new overview DF)
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
        
        # Display Stock results if found, applying display formatting
        if not results_stock.empty:
            st.markdown("### 🏬 Found in Warehouse Stock")
            # --- MODIFICATION: Use the overview DF for display ---
            st.dataframe(create_overview_df(results_stock), use_container_width=True)
        
        # Display Arrival results if found, applying display formatting
        if not results_arrival.empty:
            st.markdown("### 🆕 Found in New Arrivals")
            # --- MODIFICATION: Use the overview DF for display ---
            st.dataframe(create_overview_df(results_arrival), use_container_width=True)
    else:
        st.warning(f"❌ No matching items found for **'{query}'** in either dataset.")
        
# ==========================================
# TABBED PAGE VIEWS (If no search query is active)
# ==========================================
else:
    # Determine the status text based on category selection
    filter_status = f"({f'Filtered by **{selected_category}**' if selected_category != 'All Categories' else 'All Stock'})"

    # Use st.tabs to create the two main pages below the search bar
    tab1, tab2 = st.tabs(["🏬 Warehouse Stock", "🆕 New Arrival"])

    selected_data = None
    selected_index = None
    is_stock_tab = False
    is_arrival_tab = False

    with tab1:
        st.subheader("🏬 Warehouse Stock")
        st.write(f"📅 Last Updated: **{data['stock']['date']}** {filter_status}")

        if not filtered_stock_df.empty:
            # --- MODIFICATION: Use st.data_editor to enable row selection ---
            st_data_editor_key = "stock_editor"
            stock_overview_df = create_overview_df(filtered_stock_df)
            edited_df = st.data_editor(
                stock_overview_df,
                use_container_width=True,
                hide_index=True,
                key=st_data_editor_key,
                disabled=True, # Prevent actual editing
                column_config={"__index_label": st.column_config.Column(disabled=True)}
            )
            
            # Check for a selected row
            if edited_df["__streamlit_index"].iloc[0] != -1: # The selected index is stored in the hidden '__streamlit_index' column
                # The index refers to the filtered_stock_df's index, not the overall DataFrame
                selected_index = edited_df["__streamlit_index"].iloc[0]
                # Get the actual row from the *filtered_stock_df*
                selected_data = filtered_stock_df.loc[selected_index]
                is_stock_tab = True
                
        elif not stock_df.empty:
            st.info(f"No items found in Warehouse Stock for category: **{selected_category}**.")
        else:
            st.warning(f"⚠️ Could not display data from **{files['warehouse_stock']['path']}**.")

    with tab2:
        st.subheader("🆕 New Arrival")
        st.write(f"📅 Last Updated: **{data['new_arrival']['date']}** {filter_status}")

        if not filtered_arrival_df.empty:
            # --- MODIFICATION: Use st.data_editor to enable row selection ---
            st_data_editor_key = "arrival_editor"
            arrival_overview_df = create_overview_df(filtered_arrival_df)
            edited_df = st.data_editor(
                arrival_overview_df,
                use_container_width=True,
                hide_index=True,
                key=st_data_editor_key,
                disabled=True, # Prevent actual editing
                column_config={"__index_label": st.column_config.Column(disabled=True)}
            )
            
            # Check for a selected row
            if edited_df["__streamlit_index"].iloc[0] != -1:
                # The index refers to the filtered_arrival_df's index, not the overall DataFrame
                selected_index = edited_df["__streamlit_index"].iloc[0]
                # Get the actual row from the *filtered_arrival_df*
                selected_data = filtered_arrival_df.loc[selected_index]
                is_arrival_tab = True
                
        elif not arrival_df.empty:
            st.info(f"No items found in New Arrivals for category: **{selected_category}**.")
        else:
            st.warning(f"⚠️ Could not display data from **{files['new_arrival']['path']}**.")


    # ==========================================
    # SELECTED ITEM DETAIL VIEW (Cost Revelation)
    # ==========================================
    if selected_data is not None and not selected_data.empty:
        st.markdown("---")
        st.subheader("💰 Selected Item Details (Cost Disclosure)")
        
        # Check if the 'cost' column exists in the selected row data
        if COST_COLUMN in selected_data:
            item_name = selected_data.get('description', 'N/A')
            item_barcode = selected_data.get('itembarcode', 'N/A')
            item_cost = selected_data[COST_COLUMN]
            
            col1, col2, col3 = st.columns(3)
            
            # Display item name and barcode
            with col1:
                st.metric(label="Item Name", value=item_name)
            with col2:
                st.metric(label="Barcode", value=item_barcode)
            
            # Display the sensitive cost information
            with col3:
                # Assuming cost is a currency value, you can format it nicely
                if pd.api.types.is_numeric_dtype(type(item_cost)):
                    formatted_cost = f"{item_cost:,.2f}"
                else:
                    formatted_cost = str(item_cost)
                    
                st.metric(label=f"Confidential: {SELLING_COLUMN} Price", value=f"**{formatted_cost}**")
                
            st.success(f"You are viewing the confidential cost for **{item_name}**.")
        else:
            st.warning("Cost information (`cost` column) is not available for this item in the source data.")
