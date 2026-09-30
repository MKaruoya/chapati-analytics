import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

# Sidebar for navigation
st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📈 Store Analysis",
    "🤖 AI Insights",
    "💡 Recommendations"
])

# Initialize session state
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
    📋 **Expected columns:**
    - store_id - Store identifier
    - store_name - Store name
    - order_date - Date of order (YYYY-MM-DD)
    - order_quantity - Quantity ordered (units)
    - eturn_quantity - Quantity returned
    - product_name - Product name
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
            
            st.subheader("Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Records", len(df))
            col2.metric("Unique Stores", df['store_id'].nunique() if 'store_id' in df.columns else 0)
            col3.metric("Date Range", f"{df['order_date'].min() if 'order_date' in df.columns else 'N/A'}")
            col4.metric("Total Orders", len(df))
            
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
        df = st.session_state.data
        
        # Ensure date column is datetime
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
        
        # Select store
        stores = df['store_id'].unique() if 'store_id' in df.columns else []
        selected_store = st.selectbox("Select Store", stores)
        
        # Filter data for selected store
        store_data = df[df['store_id'] == selected_store].sort_values('order_date')
        
        if len(store_data) > 0:
            st.subheader(f"Analysis for {selected_store}")
            
            # Calculate metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            avg_qty = store_data['order_quantity'].mean() if 'order_quantity' in store_data.columns else 0
            total_orders = len(store_data)
            total_returns = store_data['return_quantity'].sum() if 'return_quantity' in store_data.columns else 0
            return_rate = (total_returns / store_data['order_quantity'].sum() * 100) if 'order_quantity' in store_data.columns else 0
            
            # Calculate order interval
            if len(store_data) > 1:
                store_data_sorted = store_data.sort_values('order_date')
                intervals = store_data_sorted['order_date'].diff().dt.days
                avg_interval = intervals.mean()
            else:
                avg_interval = 0
            
            col1.metric("Avg Order Qty", f"{avg_qty:.0f} units")
            col2.metric("Total Orders", total_orders)
            col3.metric("Avg Interval", f"{avg_interval:.1f} days")
            col4.metric("Total Returns", f"{total_returns:.0f} units")
            col5.metric("Return Rate", f"{return_rate:.1f}%")
            
            # Visualizations
            st.subheader("📊 Order Trends")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Order quantity over time
                fig1 = px.line(
                    store_data,
                    x='order_date',
                    y='order_quantity',
                    title="Order Quantity Over Time",
                    labels={'order_quantity': 'Quantity (units)', 'order_date': 'Date'}
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                # Quantity vs Returns scatter
                fig2 = px.scatter(
                    store_data,
                    x='order_quantity',
                    y='return_quantity',
                    title="Order Quantity vs Returns",
                    labels={'order_quantity': 'Order Qty', 'return_quantity': 'Return Qty'},
                    trendline="ols"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Store data table
            st.subheader("📋 Order Details")
            st.dataframe(store_data[['order_date', 'order_quantity', 'return_quantity', 'product_name']])
            
            # Save analysis
            st.session_state.analysis[selected_store] = {
                'avg_qty': avg_qty,
                'total_orders': total_orders,
                'avg_interval': avg_interval,
                'return_rate': return_rate,
                'total_returns': total_returns,
                'data': store_data
            }

# ============================================================================
# PAGE 3: AI INSIGHTS
# ============================================================================
elif page == "🤖 AI Insights":
    st.header("AI-Powered Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data
        
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
        
        stores = df['store_id'].unique()
        selected_store = st.selectbox("Select Store for AI Analysis", stores)
        
        store_data = df[df['store_id'] == selected_store].sort_values('order_date')
        
        if len(store_data) > 0:
            st.subheader(f"AI Analysis for {selected_store}")
            
            # Get analysis from session state or calculate
            if selected_store in st.session_state.analysis:
                analysis = st.session_state.analysis[selected_store]
            else:
                avg_qty = store_data['order_quantity'].mean()
                total_orders = len(store_data)
                total_returns = store_data['return_quantity'].sum()
                return_rate = (total_returns / store_data['order_quantity'].sum() * 100)
                
                if len(store_data) > 1:
                    intervals = store_data.sort_values('order_date')['order_date'].diff().dt.days
                    avg_interval = intervals.mean()
                else:
                    avg_interval = 0
                
                analysis = {
                    'avg_qty': avg_qty,
                    'total_orders': total_orders,
                    'avg_interval': avg_interval,
                    'return_rate': return_rate,
                    'total_returns': total_returns
                }
            
            # AI Insights (without API for now)
            st.info("""
            ### 📊 Key Findings:
            
            **Order Pattern Analysis:**
            - Average order quantity: **{:.0f} units**
            - Average interval between orders: **{:.1f} days**
            - Total orders placed: **{}**
            
            **Returns Analysis:**
            - Total returns: **{:.0f} units**
            - Return rate: **{:.1f}%**
            
            **Relationship Insights:**
            """.format(
                analysis['avg_qty'],
                analysis['avg_interval'],
                analysis['total_orders'],
                analysis['total_returns'],
                analysis['return_rate']
            ))
            
            # Calculate correlation
            if 'order_quantity' in store_data.columns and 'return_quantity' in store_data.columns:
                correlation = store_data['order_quantity'].corr(store_data['return_quantity'])
                st.write(f"- **Quantity-Returns Correlation: {correlation:.2f}**")
                
                if correlation > 0.5:
                    st.warning("⚠️ Higher orders correlate with higher returns - consider quality issues")
                elif correlation < -0.3:
                    st.success("✅ Higher orders correlate with lower returns - good ordering pattern")
                else:
                    st.info("ℹ️ Weak correlation between order quantity and returns")

# ============================================================================
# PAGE 4: RECOMMENDATIONS
# ============================================================================
elif page == "💡 Recommendations":
    st.header("Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data
        
        if 'order_date' in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'])
        
        stores = df['store_id'].unique()
        selected_store = st.selectbox("Select Store for Recommendations", stores)
        
        store_data = df[df['store_id'] == selected_store].sort_values('order_date')
        
        if len(store_data) > 0:
            st.subheader(f"Recommendations for {selected_store}")
            
            # Calculate current metrics
            avg_qty = store_data['order_quantity'].mean()
            total_returns = store_data['return_quantity'].sum()
            return_rate = (total_returns / store_data['order_quantity'].sum() * 100)
            
            if len(store_data) > 1:
                intervals = store_data.sort_values('order_date')['order_date'].diff().dt.days
                avg_interval = intervals.mean()
            else:
                avg_interval = 0
            
            # Generate recommendations
            st.subheader("📋 Current Pattern")
            col1, col2, col3 = st.columns(3)
            col1.metric("Current Avg Order", f"{avg_qty:.0f} units")
            col2.metric("Current Interval", f"{avg_interval:.1f} days")
            col3.metric("Current Return Rate", f"{return_rate:.1f}%")
            
            st.subheader("✅ Recommended Pattern")
            
            # Calculate recommendations
            recommended_qty = avg_qty * (1 - (return_rate / 100) * 0.5)  # Reduce by half of return rate
            recommended_interval = avg_interval if return_rate < 10 else avg_interval * 0.9  # Increase frequency if high returns
            expected_return_reduction = return_rate * 0.3  # Expect 30% reduction
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Recommended Order Qty", f"{recommended_qty:.0f} units", f"{((recommended_qty/avg_qty - 1) * 100):.1f}%")
            col2.metric("Recommended Interval", f"{recommended_interval:.1f} days", f"{((recommended_interval/avg_interval - 1) * 100):.1f}%")
            col3.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
            
            st.subheader("💡 Action Items")
            
            recommendations = []
            
            if return_rate > 15:
                recommendations.append("🔴 **HIGH RETURN RATE** - Investigate quality issues or storage conditions")
                recommendations.append("   → Reduce order quantity by 20% to test")
                recommendations.append("   → Increase order frequency to ensure freshness")
            
            if avg_interval > 14:
                recommendations.append("🟡 **LONG ORDER INTERVALS** - Risk of stockouts")
                recommendations.append("   → Increase order frequency to every 7-10 days")
                recommendations.append("   → Maintain smaller, more frequent orders")
            
            if return_rate < 5:
                recommendations.append("🟢 **EXCELLENT PERFORMANCE** - Maintain current pattern")
                recommendations.append("   → Consider slight quantity increase to boost sales")
            
            if not recommendations:
                recommendations.append("✅ Current pattern is reasonable - monitor and adjust as needed")
            
            for rec in recommendations:
                st.write(rec)
            
            # Export recommendations
            st.subheader("📥 Export Recommendations")
            
            rec_data = {
                'Store ID': [selected_store],
                'Current Avg Order Qty': [f"{avg_qty:.0f}"],
                'Recommended Order Qty': [f"{recommended_qty:.0f}"],
                'Current Interval (days)': [f"{avg_interval:.1f}"],
                'Recommended Interval (days)': [f"{recommended_interval:.1f}"],
                'Current Return Rate (%)': [f"{return_rate:.1f}"],
                'Expected Return Rate (%)': [f"{max(0, return_rate - expected_return_reduction):.1f}"]
            }
            
            rec_df = pd.DataFrame(rec_data)
            
            csv = rec_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Recommendations (CSV)",
                data=csv,
                file_name=f"recommendations_{selected_store}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v1.0\n\nAnalyze store order patterns and get AI-powered recommendations.")
