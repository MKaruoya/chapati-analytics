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
    "🤖 AI Insights",
    "💡 Recommendations"
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
    - Customer Parent Name (Store)
    - Customer Parent_Branch (Branch - this is the key!)
    - Item Description (Product)
    - Monthly Sales & Returns columns (March-September)
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, header=5)
            else:
                df = pd.read_excel(uploaded_file, header=5)
            
            df.columns = df.columns.str.strip()
            st.session_state.data = df
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(15))
            
            st.subheader("Column Names")
            st.write(df.columns.tolist())
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            if 'Customer Parent_Branch' in df.columns:
                col3.metric("Unique Branches", df['Customer Parent_Branch'].nunique())
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

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
        else:
            # Get unique branches (filter out subtotal rows)
            branches = df[df['Customer Parent_Branch'].notna() & (df['Customer Parent_Branch'].str.contains('Total', case=False, na=False) == False)]['Customer Parent_Branch'].unique()
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            # Filter data for this branch - get all product rows (not subtotal rows)
            branch_data = df[(df['Customer Parent_Branch'] == selected_branch) & 
                            (~df['Customer Parent_Branch'].str.contains('Total', case=False, na=False))]
            
            if len(branch_data) > 0:
                st.subheader(f"Analysis for {selected_branch}")
                
                # Find numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                # Identify sales and returns columns by month
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                month_data = {}
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_data[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_data[returns_col[0]], errors='coerce').sum()
                        month_data[month] = {'sales': m_sales, 'returns': m_returns}
                
                # Calculate totals
                total_sales = sum([v['sales'] for v in month_data.values()])
                total_returns = sum([v['returns'] for v in month_data.values()])
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Products", len(branch_data))
                col5.metric("Net Sales", f"{total_sales - total_returns:.0f} bales")
                
                # Monthly breakdown chart
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
                    
                    # Monthly table
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
                
                st.subheader("📋 Product Details")
                st.dataframe(branch_data, use_container_width=True)

# ============================================================================
# PAGE 3: AI INSIGHTS
# ============================================================================
elif page == "🤖 AI Insights":
    st.header("AI-Powered Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        if 'Customer Parent_Branch' not in df.columns:
            st.error("❌ 'Customer Parent_Branch' column not found")
        else:
            branches = df[df['Customer Parent_Branch'].notna() & (df['Customer Parent_Branch'].str.contains('Total', case=False, na=False) == False)]['Customer Parent_Branch'].unique()
            selected_branch = st.selectbox("Select Branch for AI Analysis", sorted(branches))
            
            branch_data = df[(df['Customer Parent_Branch'] == selected_branch) & 
                            (~df['Customer Parent_Branch'].str.contains('Total', case=False, na=False))]
            
            if len(branch_data) > 0:
                st.subheader(f"AI Analysis for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                month_data = {}
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_data[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_data[returns_col[0]], errors='coerce').sum()
                        month_data[month] = {'sales': m_sales, 'returns': m_returns}
                
                total_sales = sum([v['sales'] for v in month_data.values()])
                total_returns = sum([v['returns'] for v in month_data.values()])
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                
                st.info(f"""
                ### 📊 Key Findings:
                
                **Sales Pattern:**
                - Total sales (7 months): **{total_sales:.0f} bales**
                - Number of products: **{len(branch_data)}**
                - Average monthly sales: **{total_sales/7:.0f} bales**
                
                **Returns Analysis:**
                - Total returns: **{total_returns:.0f} bales**
                - Return rate: **{return_rate:.1f}%**
                
                **Relationship Insights:**
                """)
                
                if return_rate > 20:
                    st.error("🔴 CRITICAL - Very high return rate indicates quality issues")
                elif return_rate > 15:
                    st.warning("🟡 HIGH - Return rate needs attention")
                elif return_rate > 10:
                    st.warning("🟡 MODERATE - Monitor return trends")
                else:
                    st.success("🟢 GOOD - Return rate is acceptable")

# ============================================================================
# PAGE 4: RECOMMENDATIONS
# ============================================================================
elif page == "💡 Recommendations":
    st.header("Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        if 'Customer Parent_Branch' not in df.columns:
            st.error("❌ 'Customer Parent_Branch' column not found")
        else:
            branches = df[df['Customer Parent_Branch'].notna() & (df['Customer Parent_Branch'].str.contains('Total', case=False, na=False) == False)]['Customer Parent_Branch'].unique()
            selected_branch = st.selectbox("Select Branch for Recommendations", sorted(branches))
            
            branch_data = df[(df['Customer Parent_Branch'] == selected_branch) & 
                            (~df['Customer Parent_Branch'].str.contains('Total', case=False, na=False))]
            
            if len(branch_data) > 0:
                st.subheader(f"Recommendations for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                month_data = {}
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_data[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_data[returns_col[0]], errors='coerce').sum()
                        month_data[month] = {'sales': m_sales, 'returns': m_returns}
                
                total_sales = sum([v['sales'] for v in month_data.values()])
                total_returns = sum([v['returns'] for v in month_data.values()])
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                avg_monthly_sales = total_sales / 7
                
                st.subheader("📋 Current Pattern")
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Avg Monthly Sales", f"{avg_monthly_sales:.0f} bales")
                col2.metric("Current Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                
                st.subheader("✅ Recommended Pattern")
                
                recommended_monthly = avg_monthly_sales * (1 + (1 - return_rate/100) * 0.15)
                expected_return_reduction = return_rate * 0.3
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Recommended Monthly Sales", f"{recommended_monthly:.0f} bales", f"+{((recommended_monthly/avg_monthly_sales - 1) * 100):.1f}%")
                col2.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
                col3.metric("Confidence", "High" if len(branch_data) > 5 else "Medium")
                
                st.subheader("💡 Action Items")
                
                if return_rate > 20:
                    st.error("🔴 CRITICAL - HIGH RETURN RATE")
                    st.write("→ Investigate product quality issues immediately")
                    st.write("→ Review storage and handling conditions")
                    st.write("→ Reduce order quantities by 25%")
                    st.write("→ Increase order frequency for fresher stock")
                elif return_rate > 15:
                    st.warning("🟡 HIGH RETURN RATE")
                    st.write("→ Reduce order quantities by 15%")
                    st.write("→ Increase order frequency")
                    st.write("→ Check product quality")
                elif return_rate > 10:
                    st.warning("🟡 MODERATE RETURN RATE")
                    st.write("→ Monitor closely")
                    st.write("→ Slight reduction in quantities")
                else:
                    st.success("🟢 EXCELLENT PERFORMANCE")
                    st.write("→ Maintain current pattern")
                    st.write("→ Consider increasing order quantities by 10-15%")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v3.0\n\nAnalyze store order patterns by branch and get AI-powered recommendations.")
