import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

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
    - Customer Parent_Branch (Branch)
    - Item Description (Product)
    - Monthly Sales & Returns columns
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
            st.dataframe(df.head(10))
            
            st.subheader("Column Names")
            st.write(df.columns.tolist())
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            if 'Customer Parent Name' in df.columns:
                col3.metric("Unique Stores", df['Customer Parent Name'].nunique())
            
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
        
        if 'Customer Parent Name' not in df.columns:
            st.error("❌ 'Customer Parent Name' column not found")
        else:
            stores = df['Customer Parent Name'].dropna().unique()
            selected_store = st.selectbox("Select Store", stores)
            
            store_data = df[df['Customer Parent Name'] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"Analysis for {selected_store}")
                
                # Find numeric columns (Sales and Returns)
                numeric_cols = store_data.select_dtypes(include=['number']).columns.tolist()
                sales_cols = [col for col in numeric_cols if 'Sales' in col or 'sales' in col]
                returns_cols = [col for col in numeric_cols if 'Returns' in col or 'returns' in col]
                
                if sales_cols and returns_cols:
                    # Convert to numeric, handling errors
                    for col in sales_cols + returns_cols:
                        store_data[col] = pd.to_numeric(store_data[col], errors='coerce')
                    
                    total_sales = store_data[sales_cols].sum().sum()
                    total_returns = store_data[returns_cols].sum().sum()
                    return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Total Sales", f"{total_sales:.0f}")
                    col2.metric("Total Returns", f"{total_returns:.0f}")
                    col3.metric("Return Rate", f"{return_rate:.1f}%")
                    col4.metric("Products", len(store_data))
                    col5.metric("Net Sales", f"{total_sales - total_returns:.0f}")
                    
                    # Monthly breakdown
                    st.subheader("📊 Monthly Breakdown")
                    
                    months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                    monthly_data = []
                    
                    for month in months:
                        sales_col = [col for col in sales_cols if month in col]
                        returns_col = [col for col in returns_cols if month in col]
                        
                        if sales_col and returns_col:
                            m_sales = pd.to_numeric(store_data[sales_col[0]], errors='coerce').sum()
                            m_returns = pd.to_numeric(store_data[returns_col[0]], errors='coerce').sum()
                            monthly_data.append({
                                'Month': month,
                                'Sales': m_sales,
                                'Returns': m_returns,
                                'Net': m_sales - m_returns
                            })
                    
                    if monthly_data:
                        monthly_df = pd.DataFrame(monthly_data)
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['Sales'], name='Sales'))
                        fig.add_trace(go.Bar(x=monthly_df['Month'], y=monthly_df['Returns'], name='Returns'))
                        fig.update_layout(title="Monthly Sales vs Returns", barmode='group')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.dataframe(monthly_df)
                
                st.subheader("📋 Product Details")
                st.dataframe(store_data)

# ============================================================================
# PAGE 3: AI INSIGHTS
# ============================================================================
elif page == "🤖 AI Insights":
    st.header("AI-Powered Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        if 'Customer Parent Name' not in df.columns:
            st.error("❌ 'Customer Parent Name' column not found")
        else:
            stores = df['Customer Parent Name'].dropna().unique()
            selected_store = st.selectbox("Select Store for AI Analysis", stores)
            
            store_data = df[df['Customer Parent Name'] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"AI Analysis for {selected_store}")
                
                numeric_cols = store_data.select_dtypes(include=['number']).columns.tolist()
                sales_cols = [col for col in numeric_cols if 'Sales' in col or 'sales' in col]
                returns_cols = [col for col in numeric_cols if 'Returns' in col or 'returns' in col]
                
                if sales_cols and returns_cols:
                    for col in sales_cols + returns_cols:
                        store_data[col] = pd.to_numeric(store_data[col], errors='coerce')
                    
                    total_sales = store_data[sales_cols].sum().sum()
                    total_returns = store_data[returns_cols].sum().sum()
                    return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                    
                    st.info(f"""
                    ### 📊 Key Findings:
                    
                    **Sales Pattern:**
                    - Total sales: **{total_sales:.0f} bales**
                    - Number of products: **{len(store_data)}**
                    
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
        
        if 'Customer Parent Name' not in df.columns:
            st.error("❌ 'Customer Parent Name' column not found")
        else:
            stores = df['Customer Parent Name'].dropna().unique()
            selected_store = st.selectbox("Select Store for Recommendations", stores)
            
            store_data = df[df['Customer Parent Name'] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"Recommendations for {selected_store}")
                
                numeric_cols = store_data.select_dtypes(include=['number']).columns.tolist()
                sales_cols = [col for col in numeric_cols if 'Sales' in col or 'sales' in col]
                returns_cols = [col for col in numeric_cols if 'Returns' in col or 'returns' in col]
                
                if sales_cols and returns_cols:
                    for col in sales_cols + returns_cols:
                        store_data[col] = pd.to_numeric(store_data[col], errors='coerce')
                    
                    total_sales = store_data[sales_cols].sum().sum()
                    total_returns = store_data[returns_cols].sum().sum()
                    return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                    
                    st.subheader("📋 Current Pattern")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Current Sales", f"{total_sales:.0f}")
                    col2.metric("Current Returns", f"{total_returns:.0f}")
                    col3.metric("Return Rate", f"{return_rate:.1f}%")
                    
                    st.subheader("✅ Recommended Pattern")
                    
                    recommended_sales = total_sales * (1 + (1 - return_rate/100) * 0.15)
                    expected_return_reduction = return_rate * 0.3
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Recommended Sales", f"{recommended_sales:.0f}", f"+{((recommended_sales/total_sales - 1) * 100):.1f}%")
                    col2.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
                    col3.metric("Confidence", "High" if len(store_data) > 5 else "Medium")
                    
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
st.sidebar.info("🍞 **Chapati Analytics Agent** v2.0")
