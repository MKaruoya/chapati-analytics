import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

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
    st.header("Upload Chapati Order Data")
    
    st.info("""
    📋 **Expected Format:**
    - Customer Parent Name (Store)
    - Customer Parent_Branch (Branch - the key identifier)
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
            branches = df[df['Customer Parent_Branch'].notna() & (df['Customer Parent_Branch'].str.contains('Total', case=False, na=False) == False)]['Customer Parent_Branch'].unique()
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            branch_data = df[(df['Customer Parent_Branch'] == selected_branch) & 
                            (~df['Customer Parent_Branch'].str.contains('Total', case=False, na=False))]
            
            if len(branch_data) > 0:
                st.subheader(f"Analysis for {selected_branch}")
                
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
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Sales", f"{total_sales:.0f} bales")
                col2.metric("Total Returns", f"{total_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Products", len(branch_data))
                col5.metric("Net Sales", f"{total_sales - total_returns:.0f} bales")
                
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
                
                st.subheader("📋 Product Details")
                st.dataframe(branch_data, use_container_width=True)

# ============================================================================
# PAGE 3: AI RELATIONSHIP ANALYSIS
# ============================================================================
elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis - Quantity, Interval & Returns")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        if 'Customer Parent_Branch' not in df.columns:
            st.error("❌ 'Customer Parent_Branch' column not found")
        else:
            branches = df[df['Customer Parent_Branch'].notna() & (df['Customer Parent_Branch'].str.contains('Total', case=False, na=False) == False)]['Customer Parent_Branch'].unique()
            selected_branch = st.selectbox("Select Branch for Relationship Analysis", sorted(branches))
            
            branch_data = df[(df['Customer Parent_Branch'] == selected_branch) & 
                            (~df['Customer Parent_Branch'].str.contains('Total', case=False, na=False))]
            
            if len(branch_data) > 0:
                st.subheader(f"Relationship Analysis for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                
                # Extract monthly data
                monthly_sales = []
                monthly_returns = []
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_data[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_data[returns_col[0]], errors='coerce').sum()
                        monthly_sales.append(m_sales)
                        monthly_returns.append(m_returns)
                
                # Calculate metrics
                total_sales = sum(monthly_sales)
                total_returns = sum(monthly_returns)
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                avg_monthly_sales = total_sales / len(months)
                avg_monthly_returns = total_returns / len(months)
                
                # Calculate order interval (assuming orders every month)
                order_interval = 30 / len(months)  # Days between orders
                
                # Analyze trends
                sales_trend = "Increasing" if monthly_sales[-1] > monthly_sales[0] else "Decreasing" if monthly_sales[-1] < monthly_sales[0] else "Stable"
                returns_trend = "Increasing" if monthly_returns[-1] > monthly_returns[0] else "Decreasing" if monthly_returns[-1] < monthly_returns[0] else "Stable"
                
                st.subheader("📊 Key Metrics")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Avg Monthly Sales", f"{avg_monthly_sales:.0f} bales")
                col2.metric("Avg Monthly Returns", f"{avg_monthly_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Order Interval", f"{order_interval:.0f} days")
                col5.metric("Products", len(branch_data))
                
                st.subheader("🔍 Relationship Analysis")
                
                # Create analysis report
                analysis_text = f"""
                ### **1. ORDER QUANTITY vs RETURNS RELATIONSHIP**
                
                - **Average Order Quantity**: {avg_monthly_sales:.0f} bales/month
                - **Average Returns**: {avg_monthly_returns:.0f} bales/month
                - **Return Rate**: {return_rate:.1f}%
                
                **Interpretation:**
                """
                
                if return_rate > 20:
                    analysis_text += """
                    🔴 **CRITICAL**: High return rate indicates potential quality issues or improper handling.
                    - Larger orders may be leading to more waste
                    - Consider reducing order quantities to test if returns decrease
                    """
                elif return_rate > 15:
                    analysis_text += """
                    🟡 **HIGH**: Return rate is above acceptable levels.
                    - There's a strong relationship between order quantity and returns
                    - Recommend reducing order size by 15-20%
                    """
                elif return_rate > 10:
                    analysis_text += """
                    🟡 **MODERATE**: Return rate needs monitoring.
                    - Slight relationship between quantity and returns
                    - Maintain current quantities but monitor closely
                    """
                else:
                    analysis_text += """
                    🟢 **GOOD**: Low return rate indicates healthy ordering pattern.
                    - Orders are appropriately sized
                    - Can consider increasing quantities by 10-15%
                    """
                
                analysis_text += f"""
                
                ### **2. ORDER INTERVAL vs RETURNS RELATIONSHIP**
                
                - **Current Order Interval**: {order_interval:.0f} days
                - **Number of Orders (7 months)**: {len(months)}
                - **Frequency**: Every {order_interval:.0f} days
                
                **Interpretation:**
                """
                
                if order_interval > 30:
                    analysis_text += """
                    🔴 **INFREQUENT ORDERS**: Long intervals between orders may cause:
                    - Product spoilage/expiration
                    - Stockouts between orders
                    - Higher returns due to age
                    
                    **Recommendation**: Increase order frequency to every 7-14 days
                    """
                elif order_interval > 14:
                    analysis_text += """
                    🟡 **MODERATE INTERVAL**: Orders every 2-4 weeks.
                    - Risk of product aging and returns
                    - Some potential for stockouts
                    
                    **Recommendation**: Consider increasing to every 7-10 days
                    """
                else:
                    analysis_text += """
                    🟢 **FREQUENT ORDERS**: Orders every 1-2 weeks.
                    - Good for product freshness
                    - Reduces spoilage and returns
                    - Maintains stock availability
                    
                    **Recommendation**: Maintain current frequency
                    """
                
                analysis_text += f"""
                
                ### **3. SALES TREND vs RETURNS TREND**
                
                - **Sales Trend**: {sales_trend}
                - **Returns Trend**: {returns_trend}
                
                **Interpretation:**
                """
                
                if sales_trend == "Increasing" and returns_trend == "Increasing":
                    analysis_text += """
                    ⚠️ **CONCERN**: Both sales and returns are increasing.
                    - Larger orders are leading to proportionally more returns
                    - Quality or handling issues may be worsening
                    - Action needed: Investigate root cause of returns
                    """
                elif sales_trend == "Increasing" and returns_trend == "Decreasing":
                    analysis_text += """
                    ✅ **POSITIVE**: Sales increasing while returns decreasing.
                    - Excellent trend indicating improved operations
                    - Continue current strategy
                    """
                elif sales_trend == "Decreasing" and returns_trend == "Increasing":
                    analysis_text += """
                    🔴 **CRITICAL**: Sales decreasing but returns increasing.
                    - Serious quality or handling issues
                    - Immediate investigation required
                    """
                else:
                    analysis_text += """
                    ℹ️ **STABLE**: Both metrics are stable.
                    - Consistent performance
                    - Monitor for changes
                    """
                
                st.markdown(analysis_text)
                
                # Visualization
                st.subheader("📈 Monthly Trends")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=months, y=monthly_sales, name='Sales', mode='lines+markers', marker=dict(size=10)))
                fig.add_trace(go.Scatter(x=months, y=monthly_returns, name='Returns', mode='lines+markers', marker=dict(size=10)))
                fig.update_layout(title="Sales vs Returns Trend", xaxis_title="Month", yaxis_title="Bales", height=400)
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 4: OPTIMAL ORDER RECOMMENDATIONS
# ============================================================================
elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Pattern Recommendations")
    
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
                st.subheader(f"Optimal Order Pattern for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                
                monthly_sales = []
                monthly_returns = []
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_data[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_data[returns_col[0]], errors='coerce').sum()
                        monthly_sales.append(m_sales)
                        monthly_returns.append(m_returns)
                
                total_sales = sum(monthly_sales)
                total_returns = sum(monthly_returns)
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                avg_monthly_sales = total_sales / len(months)
                avg_monthly_returns = total_returns / len(months)
                
                st.subheader("📋 Current Pattern")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Avg Order", f"{avg_monthly_sales:.0f} bales")
                col2.metric("Current Avg Returns", f"{avg_monthly_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Order Frequency", "Monthly")
                
                # Calculate recommendations
                if return_rate > 20:
                    recommended_qty = avg_monthly_sales * 0.75  # Reduce by 25%
                    recommended_interval = 14  # Every 2 weeks
                    expected_return_reduction = 25
                    confidence = "High"
                    priority = "🔴 CRITICAL"
                elif return_rate > 15:
                    recommended_qty = avg_monthly_sales * 0.85  # Reduce by 15%
                    recommended_interval = 14  # Every 2 weeks
                    expected_return_reduction = 20
                    confidence = "High"
                    priority = "🟡 HIGH"
                elif return_rate > 10:
                    recommended_qty = avg_monthly_sales * 0.95  # Reduce by 5%
                    recommended_interval = 14  # Every 2 weeks
                    expected_return_reduction = 10
                    confidence = "Medium"
                    priority = "🟡 MODERATE"
                else:
                    recommended_qty = avg_monthly_sales * 1.10  # Increase by 10%
                    recommended_interval = 14  # Every 2 weeks
                    expected_return_reduction = 0
                    confidence = "High"
                    priority = "🟢 GOOD"
                
                st.subheader("✅ Recommended Pattern")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Recommended Order Qty", f"{recommended_qty:.0f} bales", f"{((recommended_qty/avg_monthly_sales - 1) * 100):+.1f}%")
                col2.metric("Recommended Frequency", "Every 14 days", "↑ Increase")
                col3.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
                col4.metric("Confidence Level", confidence)
                
                st.subheader("💡 Detailed Recommendations")
                
                recommendations = f"""
                ### {priority} Priority
                
                **Current Situation:**
                - Average monthly order: {avg_monthly_sales:.0f} bales
                - Average monthly returns: {avg_monthly_returns:.0f} bales
                - Return rate: {return_rate:.1f}%
                
                **Recommended Changes:**
                
                1. **Order Quantity**: {recommended_qty:.0f} bales per order
                   - Change: {((recommended_qty/avg_monthly_sales - 1) * 100):+.1f}%
                   - Rationale: Optimize for current return rate
                
                2. **Order Frequency**: Every 14 days (bi-weekly)
                   - Current: Monthly
                   - Benefit: Fresher products, reduced spoilage
                
                3. **Expected Impact:**
                   - Return rate reduction: {expected_return_reduction:.1f}%
                   - New expected return rate: {max(0, return_rate - expected_return_reduction):.1f}%
                   - Improved stock availability
                
                **Implementation Steps:**
                """
                
                if return_rate > 20:
                    recommendations += """
                1. **Immediate (Week 1)**: 
                   - Investigate root cause of high returns
                   - Check product quality and handling procedures
                   - Review storage conditions
                
                2. **Short-term (Week 2-4)**:
                   - Reduce order quantity to {:.0f} bales
                   - Switch to bi-weekly ordering
                   - Monitor returns closely
                
                3. **Medium-term (Month 2-3)**:
                   - Analyze return trends
                   - Adjust quantities based on actual performance
                   - Consider supplier quality review
                    """.format(recommended_qty)
                elif return_rate > 15:
                    recommendations += """
                1. **Immediate (Week 1)**:
                   - Reduce order quantity to {:.0f} bales
                   - Plan transition to bi-weekly orders
                
                2. **Short-term (Week 2-4)**:
                   - Implement bi-weekly ordering schedule
                   - Monitor return trends
                   - Track product freshness
                
                3. **Medium-term (Month 2-3)**:
                   - Evaluate return reduction
                   - Adjust quantities if needed
                   - Consider increasing orders if returns drop
                    """.format(recommended_qty)
                elif return_rate > 10:
                    recommendations += """
                1. **Immediate (Week 1)**:
                   - Maintain current quantities
                   - Plan transition to bi-weekly orders
                
                2. **Short-term (Week 2-4)**:
                   - Implement bi-weekly ordering
                   - Monitor for improvements
                
                3. **Medium-term (Month 2-3)**:
                   - If returns drop below 10%, consider increasing orders
                   - Optimize based on actual performance
                    """
                else:
                    recommendations += """
                1. **Immediate (Week 1)**:
                   - Increase order quantity to {:.0f} bales
                   - Maintain current monthly frequency or switch to bi-weekly
                
                2. **Short-term (Week 2-4)**:
                   - Monitor sales and returns
                   - Ensure stock availability
                   - Track customer satisfaction
                
                3. **Medium-term (Month 2-3)**:
                   - Continue monitoring
                   - Further increase if demand supports it
                   - Maintain low return rate
                    """.format(recommended_qty)
                
                st.markdown(recommendations)
                
                # Summary table
                st.subheader("📊 Comparison Summary")
                
                comparison_data = {
                    'Metric': [
                        'Average Order Quantity',
                        'Order Frequency',
                        'Expected Return Rate',
                        'Expected Monthly Returns',
                        'Expected Monthly Net Sales'
                    ],
                    'Current': [
                        f"{avg_monthly_sales:.0f} bales",
                        "Monthly",
                        f"{return_rate:.1f}%",
                        f"{avg_monthly_returns:.0f} bales",
                        f"{avg_monthly_sales - avg_monthly_returns:.0f} bales"
                    ],
                    'Recommended': [
                        f"{recommended_qty:.0f} bales",
                        "Every 14 days",
                        f"{max(0, return_rate - expected_return_reduction):.1f}%",
                        f"{(recommended_qty * (max(0, return_rate - expected_return_reduction) / 100)):.0f} bales",
                        f"{recommended_qty - (recommended_qty * (max(0, return_rate - expected_return_reduction) / 100)):.0f} bales"
                    ]
                }
                
                st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v4.0\n\nAI-powered analysis of order quantities, intervals, and returns relationships.")
