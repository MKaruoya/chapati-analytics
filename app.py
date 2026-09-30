import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

# ============================================================================
# PAGE 1: UPLOAD DATA
# ============================================================================
if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data (CSV)")
    
    st.info("""
    📋 **Expected Format:**
    - CSV file with multi-row headers (rows 1-3)
    - Data starts from row 4
    - Column A: Customer/Product names
    - Columns B onwards: Monthly Sales & Returns data
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read the CSV with data starting at row 3 (0-indexed)
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            st.session_state.data = df
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(30))
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            col3.metric("Data Shape", f"{len(df)} x {len(df.columns)}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.write(traceback.format_exc())

# ============================================================================
# PAGE 2: STORE ANALYSIS
# ============================================================================
elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        # Get first column name (contains customer/product names)
        first_col = df.columns[0]
        
        # Get unique customer/branch names
        all_names = df[first_col].dropna().unique()
        
        # Filter for branch-level entries (typically contain "-" and are not product names)
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            # Get all rows for this branch (including products under it)
            branch_rows = df[df[first_col].str.contains(selected_branch, case=False, na=False)]
            
            if len(branch_rows) > 0:
                st.subheader(f"Analysis for {selected_branch}")
                
                # Get numeric columns (skip first column which has names)
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                # Sum all numeric data for this branch
                total_sales = 0
                total_returns = 0
                
                for col in numeric_cols:
                    col_sum = pd.to_numeric(branch_rows[col], errors='coerce').sum()
                    if 'Returns' in col or 'returns' in col:
                        total_returns += col_sum
                    else:
                        total_sales += col_sum
                
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Net Sales", f"{total_sales - total_returns:.0f} bales")
                col5.metric("Products", len(branch_rows) - 1)  # Exclude branch total row
                
                st.subheader("📋 Branch Data")
                st.dataframe(branch_rows, use_container_width=True)
            else:
                st.error(f"❌ No data found for {selected_branch}")

# ============================================================================
# PAGE 3: AI RELATIONSHIP ANALYSIS
# ============================================================================
elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis - Quantity, Interval & Returns")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("📊 Analysis features coming soon. Please upload data and explore Store Analysis first.")

# ============================================================================
# PAGE 4: OPTIMAL ORDER RECOMMENDATIONS
# ============================================================================
elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("💡 Recommendation features coming soon. Please upload data and explore Store Analysis first.")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v8.0\n\nOptimized for CSV pivot table format.")
