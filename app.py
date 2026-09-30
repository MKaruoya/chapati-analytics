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
if 'month_headers' not in st.session_state:
    st.session_state.month_headers = None

# ============================================================================
# PAGE 1: UPLOAD DATA
# ============================================================================
if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data")
    
    st.info("""
    📋 **Expected Format:**
    - Row 4: Month headers (March, April, May, etc.)
    - Row 6: Column headers (Customer Parent Name, Branch, Item Description, Sales/Returns)
    - Row 7+: Data rows
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, header=5)
                month_row = pd.read_csv(uploaded_file, header=None, nrows=4).iloc[3]
            else:
                df = pd.read_excel(uploaded_file, header=5)
                month_row = pd.read_excel(uploaded_file, header=None, nrows=4).iloc[3]
            
            df.columns = df.columns.str.strip()
            st.session_state.data = df
            st.session_state.month_headers = month_row
            
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(20))
            
            st.subheader("Month Headers (Row 4)")
            st.write(month_row.tolist())
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            if 'Customer Parent_Branch' in df.columns:
                col3.metric("Unique Branches", df['Customer Parent_Branch'].nunique())
            
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
        month_headers = st.session_state.month_headers
        
        if 'Customer Parent_Branch' not in df.columns:
            st.error("❌ 'Customer Parent_Branch' column not found")
        else:
            all_branches = df[df['Customer Parent_Branch'].notna()]['Customer Parent_Branch'].unique()
            branches = [b for b in all_branches if isinstance(b, str) and b.strip() != '' and 'Total' not in b]
            
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            branch_total_name = selected_branch + " Total"
            branch_total_row = df[df['Customer Parent_Branch'] == branch_total_name]
            
            if len(branch_total_row) > 0:
                st.subheader(f"Analysis for {selected_branch}")
                
                # Extract month names from row 4
                months = []
                for val in month_headers:
                    if isinstance(val, str) and val.strip() and val not in ['', 'nan']:
                        if any(month in val for month in ['March', 'April', 'May', 'June', 'July', 'August', 'September']):
                            months.append(val.strip())
                
                st.write(f"DEBUG: Found months: {months}")
                st.write(f"DEBUG: Branch total row columns: {branch_total_row.columns.tolist()}")
                st.write(f"DEBUG: Branch total row data: {branch_total_row.values}")
                
                # Get all numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                st.write(f"DEBUG: Numeric columns: {numeric_cols}")
                
                # Extract sales and returns columns (alternating pattern)
                # Columns 3-20 are: Sales, Returns, Sales, Returns, ...
                sales_cols = [df.columns[i] for i in range(3, len(df.columns), 2)]  # columns 3, 5, 7, 9, 11, 13, 15, 17, 19
                returns_cols = [df.columns[i] for i in range(4, len(df.columns), 2)]  # columns 4, 6, 8, 10, 12, 14, 16, 18, 20
                
                st.write(f"DEBUG: Sales columns: {sales_cols}")
                st.write(f"DEBUG: Returns columns: {returns_cols}")
                
                month_data = {}
                
                for idx, month in enumerate(months):
                    if idx < len(sales_cols) and idx < len(returns_cols):
                        sales_col = sales_cols[idx]
                        returns_col = returns_cols[idx]
                        
                        m_sales = pd.to_numeric(branch_total_row[sales_col], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_total_row[returns_col], errors='coerce').sum()
                        
                        st.write(f"DEBUG: {month} - Sales col: {sales_col} = {m_sales}, Returns col: {returns_col} = {m_returns}")
                        
                        month_data[month] = {'sales': m_sales, 'returns': m_returns}
                
                total_sales = sum([v['sales'] for v in month_data.values()])
                total_returns = sum([v['returns'] for v in month_data.values()])
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Net Sales", f"{total_sales - total_returns:.0f} bales")
                col5.metric("Months", len(months))
                
                st.subheader("📊 Monthly Breakdown")
                
                if month_data:
                    months_list = list(month_data.keys())
                    sales_list = [month_data[m]['sales'] for m in months_list]
                    returns_list = [month_data[m]['returns'] for m in months_list]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=months_list, y=sales_list, name='Sales', marker_color='green'))
                    fig.add_trace(go.Bar(x=months_list, y=returns_list, name='Returns', marker_color='red'))
                    fig.update_layout(title="Monthly Sales vs Returns", barmode='group', height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    monthly_table = []
                    for month in months_list:
                        monthly_table.append({
                            'Month': month,
                            'Sales': f"{month_data[month]['sales']:.0f}",
                            'Returns': f"{month_data[month]['returns']:.0f}",
                            'Net': f"{month_data[month]['sales'] - month_data[month]['returns']:.0f}",
                            'Return %': f"{(month_data[month]['returns']/month_data[month]['sales']*100 if month_data[month]['sales'] > 0 else 0):.1f}%"
                        })
                    
                    st.dataframe(pd.DataFrame(monthly_table), use_container_width=True)
            else:
                st.error(f"❌ No data found for {selected_branch}")

# ============================================================================
# PAGE 3: AI RELATIONSHIP ANALYSIS
# ============================================================================
elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis - Quantity, Interval & Returns")
    st.info("Coming soon - Upload data first")

# ============================================================================
# PAGE 4: OPTIMAL ORDER RECOMMENDATIONS
# ============================================================================
elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Pattern Recommendations")
    st.info("Coming soon - Upload data first")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v8.0\n\nDebugging data parsing.")
