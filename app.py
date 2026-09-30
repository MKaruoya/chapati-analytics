import streamlit as st
import pandas as pd
import plotly.express as px
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
if 'analysis' not in st.session_state:
    st.session_state.analysis = {}

# ============================================================================
# PAGE 1: UPLOAD DATA
# ============================================================================
if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data")
    
    st.info("""
    📋 **Your data should have columns like:**
    - Store identifier (store_id, Store, Store ID, etc.)
    - Order date (order_date, Date, etc.)
    - Order quantity (order_quantity, Quantity, etc.)
    - Return quantity (return_quantity, Returns, etc.)
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
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
            col3.metric("Data Types", len(df.dtypes.unique()))
            
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# ============================================================================
# PAGE 2: STORE ANALYSIS
# ============================================================================
elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        # Auto-detect column names
        store_col = None
        date_col = None
        qty_col = None
        return_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'store' in col_lower and store_col is None:
                store_col = col
            if 'date' in col_lower and date_col is None:
                date_col = col
            if 'quantity' in col_lower or 'qty' in col_lower or 'order' in col_lower:
                if qty_col is None and 'return' not in col_lower:
                    qty_col = col
            if 'return' in col_lower and return_col is None:
                return_col = col
        
        if store_col is None or qty_col is None:
            st.error("❌ Could not find store or quantity columns. Please check your data format.")
            st.write(f"Available columns: {df.columns.tolist()}")
        else:
            # Convert date if found
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            
            stores = df[store_col].unique()
            selected_store = st.selectbox("Select Store", stores)
            
            store_data = df[df[store_col] == selected_store]
            if date_col:
                store_data = store_data.sort_values(date_col)
            
            if len(store_data) > 0:
                st.subheader(f"Analysis for {selected_store}")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                avg_qty = store_data[qty_col].mean()
                total_orders = len(store_data)
                total_returns = store_data[return_col].sum() if return_col else 0
                return_rate = (total_returns / store_data[qty_col].sum() * 100) if return_col else 0
                
                if date_col and len(store_data) > 1:
                    intervals = store_data[date_col].diff().dt.days
                    avg_interval = intervals.mean()
                else:
                    avg_interval = 0
                
                col1.metric("Avg Order Qty", f"{avg_qty:.0f}")
                col2.metric("Total Orders", total_orders)
                col3.metric("Avg Interval", f"{avg_interval:.1f} days")
                col4.metric("Total Returns", f"{total_returns:.0f}")
                col5.metric("Return Rate", f"{return_rate:.1f}%")
                
                # Visualizations
                st.subheader("📊 Order Trends")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if date_col:
                        fig1 = px.line(
                            store_data,
                            x=date_col,
                            y=qty_col,
                            title="Order Quantity Over Time",
                            labels={qty_col: 'Quantity', date_col: 'Date'}
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    if return_col:
                        fig2 = px.scatter(
                            store_data,
                            x=qty_col,
                            y=return_col,
                            title="Order Quantity vs Returns",
                            labels={qty_col: 'Order Qty', return_col: 'Return Qty'},
                            trendline="ols"
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                
                st.subheader("📋 Order Details")
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
        
        # Auto-detect columns
        store_col = None
        qty_col = None
        return_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'store' in col_lower and store_col is None:
                store_col = col
            if 'quantity' in col_lower or 'qty' in col_lower or 'order' in col_lower:
                if qty_col is None and 'return' not in col_lower:
                    qty_col = col
            if 'return' in col_lower and return_col is None:
                return_col = col
        
        if store_col and qty_col:
            stores = df[store_col].unique()
            selected_store = st.selectbox("Select Store for AI Analysis", stores)
            
            store_data = df[df[store_col] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"AI Analysis for {selected_store}")
                
                avg_qty = store_data[qty_col].mean()
                total_returns = store_data[return_col].sum() if return_col else 0
                return_rate = (total_returns / store_data[qty_col].sum() * 100) if return_col else 0
                
                st.info(f"""
                ### 📊 Key Findings:
                
                **Order Pattern:**
                - Average order quantity: **{avg_qty:.0f} units**
                - Total orders: **{len(store_data)}**
                
                **Returns Analysis:**
                - Total returns: **{total_returns:.0f} units**
                - Return rate: **{return_rate:.1f}%**
                """)
                
                if return_col:
                    correlation = store_data[qty_col].corr(store_data[return_col])
                    st.write(f"**Quantity-Returns Correlation: {correlation:.2f}**")
                    
                    if correlation > 0.5:
                        st.warning("⚠️ Higher orders correlate with higher returns")
                    elif correlation < -0.3:
                        st.success("✅ Higher orders correlate with lower returns")
                    else:
                        st.info("ℹ️ Weak correlation between quantity and returns")

# ============================================================================
# PAGE 4: RECOMMENDATIONS
# ============================================================================
elif page == "💡 Recommendations":
    st.header("Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        # Auto-detect columns
        store_col = None
        qty_col = None
        return_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if 'store' in col_lower and store_col is None:
                store_col = col
            if 'quantity' in col_lower or 'qty' in col_lower or 'order' in col_lower:
                if qty_col is None and 'return' not in col_lower:
                    qty_col = col
            if 'return' in col_lower and return_col is None:
                return_col = col
        
        if store_col and qty_col:
            stores = df[store_col].unique()
            selected_store = st.selectbox("Select Store for Recommendations", stores)
            
            store_data = df[df[store_col] == selected_store]
            
            if len(store_data) > 0:
                st.subheader(f"Recommendations for {selected_store}")
                
                avg_qty = store_data[qty_col].mean()
                total_returns = store_data[return_col].sum() if return_col else 0
                return_rate = (total_returns / store_data[qty_col].sum() * 100) if return_col else 0
                
                st.subheader("📋 Current Pattern")
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Avg Order", f"{avg_qty:.0f} units")
                col2.metric("Total Orders", len(store_data))
                col3.metric("Current Return Rate", f"{return_rate:.1f}%")
                
                st.subheader("✅ Recommended Pattern")
                
                recommended_qty = avg_qty * (1 - (return_rate / 100) * 0.5)
                expected_return_reduction = return_rate * 0.3
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Recommended Order Qty", f"{recommended_qty:.0f} units", f"{((recommended_qty/avg_qty - 1) * 100):.1f}%")
                col2.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
                col3.metric("Confidence", "High" if len(store_data) > 10 else "Medium")
                
                st.subheader("💡 Action Items")
                
                if return_rate > 15:
                    st.error("🔴 HIGH RETURN RATE - Investigate quality issues")
                    st.write("→ Reduce order quantity by 20%")
                    st.write("→ Increase order frequency")
                elif return_rate > 10:
                    st.warning("🟡 MODERATE RETURN RATE - Monitor closely")
                    st.write("→ Reduce order quantity by 10%")
                else:
                    st.success("🟢 GOOD PERFORMANCE - Maintain pattern")
                    st.write("→ Consider slight quantity increase")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics** v1.0")
