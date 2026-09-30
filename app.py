import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📈 Store Analysis"
])

if 'data' not in st.session_state:
    st.session_state.data = None

# ============================================================================
# PAGE 1: UPLOAD DATA
# ============================================================================
if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data")
    
    st.info("""
    📋 **Expected Format:**
    - Excel file with data starting from row 7
    - Columns: Customer Parent Name, Customer Parent_Branch, Item Description, Sales/Returns
    """)
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, header=5)
            df.columns = df.columns.str.strip()
            st.session_state.data = df
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(20))
            
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
        
        if 'Customer Parent_Branch' not in df.columns:
            st.error("❌ 'Customer Parent_Branch' column not found")
            st.write(f"Available columns: {df.columns.tolist()}")
        else:
            # Get unique branches - EXCLUDE the "Total" rows
            all_branches = df[df['Customer Parent_Branch'].notna()]['Customer Parent_Branch'].unique()
            branches = [b for b in all_branches if isinstance(b, str) and b.strip() != '' and 'Total' not in b]
            
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            # Get the BRANCH TOTAL row - look for the matching branch name + " Total"
            branch_total_name = selected_branch + " Total"
            branch_total_row = df[df['Customer Parent_Branch'] == branch_total_name]
            
            if len(branch_total_row) > 0:
                st.subheader(f"Analysis for {selected_branch}")
                
                # Get all numeric columns (columns 3 onwards are Sales/Returns)
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                # Columns alternate: Sales, Returns, Sales, Returns...
                # Starting from column index 3 (after Customer Parent Name, Branch, Item Description)
                sales_cols = numeric_cols[0::2]  # Every other column starting from 0
                returns_cols = numeric_cols[1::2]  # Every other column starting from 1
                
                # Extract month names from column names if available
                months = []
                for col in sales_cols:
                    # Try to extract month from column name
                    for month in ['March', 'April', 'May', 'June', 'July', 'August', 'September']:
                        if month in str(col):
                            months.append(month)
                            break
                    else:
                        # If no month found, use generic name
                        months.append(f"Period {len(months)+1}")
                
                month_data = {}
                
                for idx, (sales_col, returns_col) in enumerate(zip(sales_cols, returns_cols)):
                    month = months[idx] if idx < len(months) else f"Period {idx+1}"
                    
                    m_sales = pd.to_numeric(branch_total_row[sales_col], errors='coerce').sum()
                    m_returns = pd.to_numeric(branch_total_row[returns_col], errors='coerce').sum()
                    
                    month_data[month] = {'sales': m_sales, 'returns': m_returns}
                
                total_sales = sum([v['sales'] for v in month_data.values()])
                total_returns = sum([v['returns'] for v in month_data.values()])
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Net Sales", f"{total_sales - total_returns:.0f} bales")
                col5.metric("Periods", len(months))
                
                st.subheader("📊 Monthly Breakdown")
                
                if month_data:
                    months_list = list(month_data.keys())
                    sales_list = [month_data[m]['sales'] for m in months_list]
                    returns_list = [month_data[m]['returns'] for m in months_list]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=months_list, y=sales_list, name='Sales', marker_color='green'))
                    fig.add_trace(go.Bar(x=months_list, y=returns_list, name='Returns', marker_color='red'))
                    fig.update_layout(title="Sales vs Returns", barmode='group', height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    monthly_table = []
                    for month in months_list:
                        monthly_table.append({
                            'Period': month,
                            'Sales': f"{month_data[month]['sales']:.0f}",
                            'Returns': f"{month_data[month]['returns']:.0f}",
                            'Net': f"{month_data[month]['sales'] - month_data[month]['returns']:.0f}",
                            'Return %': f"{(month_data[month]['returns']/month_data[month]['sales']*100 if month_data[month]['sales'] > 0 else 0):.1f}%"
                        })
                    
                    st.dataframe(pd.DataFrame(monthly_table), use_container_width=True)
                
                st.subheader("📋 All Products in This Branch")
                all_products = df[(df['Customer Parent_Branch'] == selected_branch) & 
                                 (df['Item Description'].notna())]
                st.dataframe(all_products, use_container_width=True)
            else:
                st.error(f"❌ No data found for {selected_branch}")
                st.write(f"Looking for: '{branch_total_name}'")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v9.0\n\nSimplified data parsing.")
