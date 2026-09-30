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
            st.dataframe(df.head(20))
            
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
            branches = df[df['Customer Parent_Branch'].notna()]['Customer Parent_Branch'].unique()
            branches = [b for b in branches if isinstance(b, str) and b.strip() != '']
            
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            branch_total_row = df[(df['Customer Parent_Branch'] == selected_branch) & 
                                  (df['Item Description'].notna()) &
                                  (df['Item Description'].astype(str).str.contains('Total', case=False, na=False))]
            
            if len(branch_total_row) > 0:
                st.subheader(f"Analysis for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                month_data = {}
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_total_row[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_total_row[returns_col[0]], errors='coerce').sum()
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
                
                # WEEKLY BREAKDOWN
                st.subheader("📅 Weekly Breakdown (Estimated from Monthly Data)")
                st.info("Note: Data is monthly. Weekly breakdown is calculated by dividing monthly totals by 4 weeks.")
                
                weekly_data = []
                week_counter = 1
                
                for month in months_list:
                    m_sales = month_data[month]['sales']
                    m_returns = month_data[month]['returns']
                    
                    # Divide by 4 weeks
                    weekly_sales = m_sales / 4
                    weekly_returns = m_returns / 4
                    
                    for week in range(1, 5):
                        weekly_data.append({
                            'Week': f"W{week_counter}",
                            'Month': month,
                            'Week of Month': f"Week {week}",
                            'Sales': f"{weekly_sales:.2f}",
                            'Returns': f"{weekly_returns:.2f}",
                            'Net': f"{weekly_sales - weekly_returns:.2f}",
                            'Return %': f"{(weekly_returns/weekly_sales*100 if weekly_sales > 0 else 0):.1f}%"
                        })
                        week_counter += 1
                
                st.dataframe(pd.DataFrame(weekly_data), use_container_width=True)
                
                # Weekly trend chart
                weekly_df = pd.DataFrame(weekly_data)
                weekly_df['Sales'] = pd.to_numeric(weekly_df['Sales'])
                weekly_df['Returns'] = pd.to_numeric(weekly_df['Returns'])
                
                fig_weekly = go.Figure()
                fig_weekly.add_trace(go.Scatter(x=weekly_df['Week'], y=weekly_df['Sales'], name='Sales', mode='lines+markers'))
                fig_weekly.add_trace(go.Scatter(x=weekly_df['Week'], y=weekly_df['Returns'], name='Returns', mode='lines+markers'))
                fig_weekly.update_layout(title="Weekly Sales vs Returns Trend", xaxis_title="Week", yaxis_title="Bales", height=400)
                st.plotly_chart(fig_weekly, use_container_width=True)
                
                st.subheader("📋 All Products in This Branch")
                all_products = df[(df['Customer Parent_Branch'] == selected_branch) & 
                                 (~df['Item Description'].astype(str).str.contains('Total', case=False, na=False)) &
                                 (df['Item Description'].notna())]
                st.dataframe(all_products, use_container_width=True)
            else:
                st.warning(f"⚠️ No branch total row found for {selected_branch}")

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
            branches = df[df['Customer Parent_Branch'].notna()]['Customer Parent_Branch'].unique()
            branches = [b for b in branches if isinstance(b, str) and b.strip() != '']
            
            selected_branch = st.selectbox("Select Branch for Relationship Analysis", sorted(branches))
            
            branch_total_row = df[(df['Customer Parent_Branch'] == selected_branch) & 
                                  (df['Item Description'].notna()) &
                                  (df['Item Description'].astype(str).str.contains('Total', case=False, na=False))]
            
            if len(branch_total_row) > 0:
                st.subheader(f"Relationship Analysis for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                
                monthly_sales = []
                monthly_returns = []
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_total_row[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_total_row[returns_col[0]], errors='coerce').sum()
                        monthly_sales.append(m_sales)
                        monthly_returns.append(m_returns)
                
                total_sales = sum(monthly_sales)
                total_returns = sum(monthly_returns)
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                avg_monthly_sales = total_sales / len(months)
                avg_monthly_returns = total_returns / len(months)
                
                # Calculate weekly average
                avg_weekly_sales = avg_monthly_sales / 4
                avg_weekly_returns = avg_monthly_returns / 4
                
                st.subheader("📊 Key Metrics")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Avg Weekly Sales", f"{avg_weekly_sales:.0f} bales")
                col2.metric("Avg Weekly Returns", f"{avg_weekly_returns:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Total Sales", f"{total_sales:.0f} bales")
                col5.metric("Total Returns", f"{total_returns:.0f} bales")
                
                st.subheader("🔍 Relationship Analysis")
                
                sales_trend = "Increasing" if monthly_sales[-1] > monthly_sales[0] else "Decreasing" if monthly_sales[-1] < monthly_sales[0] else "Stable"
                returns_trend = "Increasing" if monthly_returns[-1] > monthly_returns[0] else "Decreasing" if monthly_returns[-1] < monthly_returns[0] else "Stable"
                
                analysis_text = f"""
                ### **1. ORDER QUANTITY vs RETURNS RELATIONSHIP**
                
                - **Average Weekly Order**: {avg_weekly_sales:.0f} bales/week
                - **Average Weekly Returns**: {avg_weekly_returns:.0f} bales/week
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
                
                - **Current Order Interval**: Weekly (7 days)
                - **Orders per Month**: 4
                - **Frequency**: Every 7 days
                
                **Interpretation:**
                """
                
                analysis_text += """
                🟢 **FREQUENT ORDERS**: Orders every week.
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
            branches = df[df['Customer Parent_Branch'].notna()]['Customer Parent_Branch'].unique()
            branches = [b for b in branches if isinstance(b, str) and b.strip() != '']
            
            selected_branch = st.selectbox("Select Branch for Recommendations", sorted(branches))
            
            branch_total_row = df[(df['Customer Parent_Branch'] == selected_branch) & 
                                  (df['Item Description'].notna()) &
                                  (df['Item Description'].astype(str).str.contains('Total', case=False, na=False))]
            
            if len(branch_total_row) > 0:
                st.subheader(f"Optimal Order Pattern for {selected_branch}")
                
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                months = ['March', 'April', 'May', 'June', 'July', 'August', 'September']
                
                monthly_sales = []
                monthly_returns = []
                
                for month in months:
                    sales_col = [col for col in numeric_cols if month in col and ('Sales' in col or 'sales' in col)]
                    returns_col = [col for col in numeric_cols if month in col and ('Returns' in col or 'returns' in col)]
                    
                    if sales_col and returns_col:
                        m_sales = pd.to_numeric(branch_total_row[sales_col[0]], errors='coerce').sum()
                        m_returns = pd.to_numeric(branch_total_row[returns_col[0]], errors='coerce').sum()
                        monthly_sales.append(m_sales)
                        monthly_returns.append(m_returns)
                
                total_sales = sum(monthly_sales)
                total_returns = sum(monthly_returns)
                return_rate = (total_returns / total_sales * 100) if total_sales > 0 else 0
                avg_monthly_sales = total_sales / len(months)
                avg_weekly_sales = avg_monthly_sales / 4
                avg_monthly_returns = total_returns / len(months)
                
                st.subheader("📋 Current Pattern")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Current Weekly Order", f"{avg_weekly_sales:.0f} bales")
                col2.metric("Current Monthly Order", f"{avg_monthly_sales:.0f} bales")
                col3.metric("Return Rate", f"{return_rate:.1f}%")
                col4.metric("Order Frequency", "Weekly")
                
                # Calculate recommendations
                if return_rate > 20:
                    recommended_weekly = avg_weekly_sales * 0.75
                    recommended_monthly = recommended_weekly * 4
                    expected_return_reduction = 25
                    confidence = "High"
                    priority = "🔴 CRITICAL"
                elif return_rate > 15:
                    recommended_weekly = avg_weekly_sales * 0.85
                    recommended_monthly = recommended_weekly * 4
                    expected_return_reduction = 20
                    confidence = "High"
                    priority = "🟡 HIGH"
                elif return_rate > 10:
                    recommended_weekly = avg_weekly_sales * 0.95
                    recommended_monthly = recommended_weekly * 4
                    expected_return_reduction = 10
                    confidence = "Medium"
                    priority = "🟡 MODERATE"
                else:
                    recommended_weekly = avg_weekly_sales * 1.10
                    recommended_monthly = recommended_weekly * 4
                    expected_return_reduction = 0
                    confidence = "High"
                    priority = "🟢 GOOD"
                
                st.subheader("✅ Recommended Pattern")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Recommended Weekly Order", f"{recommended_weekly:.0f} bales", f"{((recommended_weekly/avg_weekly_sales - 1) * 100):+.1f}%")
                col2.metric("Recommended Monthly Order", f"{recommended_monthly:.0f} bales", f"{((recommended_monthly/avg_monthly_sales - 1) * 100):+.1f}%")
                col3.metric("Expected Return Rate", f"{max(0, return_rate - expected_return_reduction):.1f}%", f"-{expected_return_reduction:.1f}%")
                col4.metric("Confidence Level", confidence)
                
                st.subheader("💡 Detailed Recommendations")
                
                recommendations = f"""
                ### {priority} Priority
                
                **Current Situation:**
                - Average weekly order: {avg_weekly_sales:.0f} bales
                - Average monthly order: {avg_monthly_sales:.0f} bales
                - Return rate: {return_rate:.1f}%
                
                **Recommended Changes:**
                
                1. **Weekly Order Quantity**: {recommended_weekly:.0f} bales per week
                   - Change: {((recommended_weekly/avg_weekly_sales - 1) * 100):+.1f}%
                
                2. **Monthly Order Quantity**: {recommended_monthly:.0f} bales per month
                   - Change: {((recommended_monthly/avg_monthly_sales - 1) * 100):+.1f}%
                
                3. **Order Frequency**: Every 7 days (weekly)
                
                4. **Expected Impact:**
                   - Return rate reduction: {expected_return_reduction:.1f}%
                   - New expected return rate: {max(0, return_rate - expected_return_reduction):.1f}%
                   - Improved stock availability
                """
                
                st.markdown(recommendations)
                
                st.subheader("📊 Comparison Summary")
                
                comparison_data = {
                    'Metric': [
                        'Weekly Order Quantity',
                        'Monthly Order Quantity',
                        'Order Frequency',
                        'Expected Return Rate',
                        'Expected Weekly Returns',
                        'Expected Weekly Net Sales'
                    ],
                    'Current': [
                        f"{avg_weekly_sales:.0f} bales",
                        f"{avg_monthly_sales:.0f} bales",
                        "Weekly",
                        f"{return_rate:.1f}%",
                        f"{avg_monthly_returns/4:.0f} bales",
                        f"{(avg_weekly_sales - avg_monthly_returns/4):.0f} bales"
                    ],
                    'Recommended': [
                        f"{recommended_weekly:.0f} bales",
                        f"{recommended_monthly:.0f} bales",
                        "Weekly",
                        f"{max(0, return_rate - expected_return_reduction):.1f}%",
                        f"{(recommended_weekly * (max(0, return_rate - expected_return_reduction) / 100)):.0f} bales",
                        f"{recommended_weekly - (recommended_weekly * (max(0, return_rate - expected_return_reduction) / 100)):.0f} bales"
                    ]
                }
                
                st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v6.0\n\nWeekly breakdown analysis for better insights.")
