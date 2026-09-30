import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
    - Customer Parent_Branch (Branch)
    - Item Description (Product)
    - Monthly Sales & Returns columns (March-September)
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file, header=5)  # Skip to row 6 (0-indexed)
            else:
                df = pd.read_excel(uploaded_file, header=5)  # Skip to row 6
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            st.session_state.data = df
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(10))
            
            st.subheader("Column Names Detected")
            st.write(f"**Columns:** {', '.join(df.columns.tolist())}")
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Records", len(df))
            col2.metric("Columns", len(df.columns))
            col3.metric("Stores", df['Customer Parent Name'].nunique() if 'Customer Parent Name' in df.columns else 0)
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.write("Make sure the file has the correct format with headers in row 6")

# ============================================================================
# PAGE 2: STORE ANALYSIS
# ============================================================================
elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        # Get unique stores
        if 'Customer Parent Name' in df.columns:
            stores = df['Customer Parent Name'].dropna().unique()
            selected_store = st.selectbox("Select Store", stores)
            
            store_data = df[df['Customer Parent Name'] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"Analysis for {selected_store}")
                
                # Extract sales and returns columns
                sales_cols = [col for col in df.columns if 'Sales' in col and 'Grand Total' not in col]
                returns_cols = [col for col in df.columns if 'Returns' in col and 'Grand Total' not in col]
                
                # Calculate metrics
                total_sales = store_data[sales_cols].sum().sum()
                total_returns = store_data[returns_cols].sum().sum()
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                avg_sales_per_order = total_sales / len(store_data) if len(store_data) > 0 else 0
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Avg Sales/Item", f"{avg_sales_per_order:.0f}")
                col5.metric("Products", len(store_data))
                
                # Monthly trend
                st.subheader("📊 Monthly Trends")
                
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                monthly_sales = []
                monthly_returns = []
                
                for month in months:
                    sales_col = [col for col in sales_cols if month in col]
                    returns_col = [col for col in returns_cols if month in col]
                    
                    if sales_col:
                        monthly_sales.append(store_data[sales_col[0]].sum())
                    if returns_col:
                        monthly_returns.append(store_data[returns_col[0]].sum())
                
                # Create trend chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=monthly_sales, name='Sales', mode='lines+markers'))
                fig.add_trace(go.Scatter(x=months, y=monthly_returns, name='Returns', mode='lines+markers'))
                fig.update_layout(title="Monthly Sales vs Returns", xaxis_title="Month", yaxis_title="Bales")
                st.plotly_chart(fig, use_container_width=True)
                
                # Product breakdown
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
        
        if 'Customer Parent Name' in df.columns:
            stores = df['Customer Parent Name'].dropna().unique()
            selected_store = st.selectbox("Select Store for AI Analysis", stores)
            
            store_data = df[df['Customer Parent Name'] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"AI Analysis for {selected_store}")
                
                # Extract metrics
                sales_cols = [col for col in df.columns if 'Sales' in col and 'Grand Total' not in col]
                returns_cols = [col for col in df.columns if 'Returns' in col and 'Grand Total' not in col]
                
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
                
                # Analyze correlation between sales and returns
                if len(store_data) > 1:
                    store_data['total_sales'] = store_data[sales_cols].sum(axis=1)
                    store_data['total_returns'] = store_data[returns_cols].sum(axis=1)
                    
                    correlation = store_data['total_sales'].corr(store_data['total_returns'])
                    st.write(f"- **Sales-Returns Correlation: {correlation:.2f}**")
                    
                    if correlation > 0.5:
                        st.warning("⚠️ Higher sales correlate with higher returns - quality issue?")
                    elif correlation < -0.3:
                        st.success("✅ Higher sales correlate with lower returns - good pattern!")
                    else:
                        st.info("ℹ️ Weak correlation between sales and returns")

# ============================================================================
# PAGE 4: RECOMMENDATIONS
# ============================================================================
elif page == "💡 Recommendations":
    st.header("Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        if 'Customer Parent Name' in df.columns:
            stores = df['Customer Parent Name'].dropna().unique()
            selected_store = st.selectbox("Select Store for Recommendations", stores)
            
            store_data = df[df['Customer Parent Name'] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"Recommendations for {selected_store}")
                
                # Extract metrics
                sales_cols = [col for col in df.columns if 'Sales' in col and 'Grand Total' not in col]
                returns_cols = [col for col in df.columns if 'Returns' in col and 'Grand Total' not in col]
                
                total_sales = store_data[sales_cols].sum().sum()
                total_returns = store_data[returns_cols].sum().sum()
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                
                st.subheader("📋 Current Pattern")
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Current Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Current Return Rate", f"{return_rate:.1f}%")
                
                st.subheader("✅ Recommended Pattern")
                
                # Calculate recommendations
                recommended_sales = total_sales * (1 + (1 - return_rate/100) * 0.15)  # 15% increase if low returns
                expected_return_reduction = return_rate * 0.3
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Recommended Sales Target", f"{recommended_sales:.0f} bales", f"+{((recommended_sales/total_sales - 1) * 100):.1f}%")
                col2.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
                col3.metric("Confidence", "High" if len(store_data) > 5 else "Medium")
                
                st.subheader("💡 Action Items")
                
                if return_rate > 20:
                    st.error("🔴 CRITICAL - HIGH RETURN RATE")
                    st.write("→ Investigate product quality issues")
                    st.write("→ Review storage and handling conditions")
                    st.write("→ Reduce order quantities by 25%")
                elif return_rate > 15:
                    st.warning("🟡 HIGH RETURN RATE - Needs attention")
                    st.write("→ Reduce order quantities by 15%")
                    st.write("→ Increase order frequency")
                elif return_rate > 10:
                    st.warning("🟡 MODERATE RETURN RATE")
                    st.write("→ Monitor closely")
                    st.write("→ Slight reduction in quantities")
                else:
                    st.success("🟢 EXCELLENT PERFORMANCE")
                    st.write("→ Maintain current pattern")
                    st.write("→ Consider increasing order quantities by 10-15%")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v2.0\n\nAnalyze store order patterns and get AI-powered recommendations.")
