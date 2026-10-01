import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import io

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
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read data starting from row 4 (skip header rows 1-3)
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            
            # Remove "Unnamed" columns (empty spacing columns)
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            
            # Rename first column to "Branch"
            df = df.rename(columns={df.columns[0]: 'Branch'})
            
            st.session_state.data = df
            
            st.success("✅ Data uploaded and cleaned successfully!")
            
            st.subheader("📊 Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            col3.metric("Unique Branches", df['Branch'].nunique())
            col4.metric("Data Pairs (Weeks)", (len(df.columns) - 1) // 2)
            
            st.subheader("📋 Column Structure")
            st.write(f"**First Column:** Branch names")
            st.write(f"**Data Columns:** {len(df.columns) - 1} columns")
            st.write(f"**Weeks:** {(len(df.columns) - 1) // 2} weeks (each week = Sales + Returns)")
            
            st.subheader("🔍 Data Preview (Cleaned)")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.subheader("📈 Data Quality Check")
            
            # Check for branches with data
            branches_with_data = df[df['Branch'].notna()]['Branch'].unique()
            branches_with_data = [b for b in branches_with_data if isinstance(b, str) and '-' in b and 'CHAPATI' not in b.upper()]
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Branches Found:** {len(branches_with_data)}")
                st.write("Sample branches:")
                for branch in sorted(branches_with_data)[:5]:
                    st.write(f"  • {branch}")
            
            with col2:
                # Check data density
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
                total_cells = len(df) * len(numeric_cols)
                filled_cells = df[numeric_cols].notna().sum().sum()
                data_density = (filled_cells / total_cells * 100) if total_cells > 0 else 0
                
                st.write(f"**Data Density:** {data_density:.1f}%")
                st.write(f"**Filled Cells:** {filled_cells:,} / {total_cells:,}")
            
            st.subheader("✅ Ready for Analysis!")
            st.write("Go to **Store Analysis** to view week-by-week and month-by-month performance for any branch.")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.write(traceback.format_exc())

# ============================================================================
# PAGE 2: STORE ANALYSIS
# ============================================================================
elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis - Week by Week & Month by Month")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        # Get unique branch names
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            # Get the branch row
            branch_row = df[df['Branch'] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Performance Analysis for {selected_branch}")
                
                # Get all numeric columns (skip first column which has names)
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                
                # Process pairs: every 2 columns = 1 week (Net Sales, Returns)
                weekly_data = []
                week_num = 1
                
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_col = numeric_cols[i]
                    returns_col = numeric_cols[i + 1]
                    
                    net_sales_val = pd.to_numeric(branch_row[net_sales_col].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[returns_col].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val) or pd.notna(returns_val):
                        net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
                        returns_val = returns_val if pd.notna(returns_val) else 0
                        
                        # Calculate return percentage
                        original_order = abs(net_sales_val) + returns_val
                        
                        if original_order > 0:
                            return_pct = (returns_val / original_order) * 100
                        else:
                            return_pct = 0
                        
                        # Determine status
                        if net_sales_val < 0:
                            status = "🔴"
                        elif return_pct > 20:
                            status = "🔴"
                        elif return_pct > 15:
                            status = "🟡"
                        else:
                            status = "🟢"
                        
                        weekly_data.append({
                            'Week': f"W{week_num}",
                            'Net Sales': f"{net_sales_val:.0f}",
                            'Returns': f"{returns_val:.0f}",
                            'Return %': f"{return_pct:.1f}%",
                            'Status': status,
                            'net_sales_numeric': net_sales_val,
                            'returns_numeric': returns_val,
                            'return_pct_numeric': return_pct
                        })
                    
                    week_num += 1
                
                if weekly_data:
                    # ===== WEEKLY ANALYSIS =====
                    st.subheader("📅 Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    display_weekly = weekly_df[['Week', 'Net Sales', 'Returns', 'Return %', 'Status']].copy()
                    st.dataframe(display_weekly, use_container_width=True)
                    
                    # ===== MONTHLY ANALYSIS =====
                    st.subheader("📊 Monthly Performance")
                    
                    # Estimate months based on weeks
                    # Assuming: Weeks 1-5 = Month 1, Weeks 6-10 = Month 2, etc.
                    # But we need to be smarter - let's group by approximate month boundaries
                    
                    weeks_per_month = 5  # Approximate
                    monthly_data = []
                    
                    for month_num in range(1, 10):  # Support up to 9 months
                        start_week = (month_num - 1) * weeks_per_month
                        end_week = month_num * weeks_per_month
                        
                        month_weeks = weekly_data[start_week:end_week]
                        
                        if month_weeks:
                            month_sales = sum([w['net_sales_numeric'] for w in month_weeks])
                            month_returns = sum([w['returns_numeric'] for w in month_weeks])
                            month_original = abs(month_sales) + month_returns
                            
                            if month_original > 0:
                                month_return_pct = (month_returns / month_original) * 100
                            else:
                                month_return_pct = 0
                            
                            monthly_data.append({
                                'Month': f"M{month_num}",
                                'Weeks': f"W{start_week+1}-W{end_week}",
                                'Net Sales': f"{month_sales:.0f}",
                                'Returns': f"{month_returns:.0f}",
                                'Return %': f"{month_return_pct:.1f}%",
                                'net_sales_numeric': month_sales,
                                'returns_numeric': month_returns,
                                'return_pct_numeric': month_return_pct
                            })
                    
                    if monthly_data:
                        monthly_df = pd.DataFrame(monthly_data)
                        display_monthly = monthly_df[['Month', 'Weeks', 'Net Sales', 'Returns', 'Return %']].copy()
                        st.dataframe(display_monthly, use_container_width=True)
                        
                        # ===== MONTH-OVER-MONTH TRENDS =====
                        st.subheader("📈 Month-over-Month Trends")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Sales Trend:**")
                            if len(monthly_data) > 1:
                                first_month_sales = monthly_data[0]['net_sales_numeric']
                                last_month_sales = monthly_data[-1]['net_sales_numeric']
                                
                                if first_month_sales != 0:
                                    change_pct = ((last_month_sales - first_month_sales) / abs(first_month_sales)) * 100
                                    
                                    if change_pct > 0:
                                        st.success(f"📈 +{change_pct:.1f}% (Growing)")
                                    elif change_pct < 0:
                                        st.error(f"📉 {change_pct:.1f}% (Declining)")
                                    else:
                                        st.info(f"➡️ 0% (Stable)")
                                else:
                                    st.info("No data for comparison")
                        
                        with col2:
                            st.write("**Returns Trend:**")
                            if len(monthly_data) > 1:
                                first_month_returns = monthly_data[0]['returns_numeric']
                                last_month_returns = monthly_data[-1]['returns_numeric']
                                
                                if first_month_returns != 0:
                                    change_pct = ((last_month_returns - first_month_returns) / abs(first_month_returns)) * 100
                                    
                                    if change_pct < 0:
                                        st.success(f"📉 {change_pct:.1f}% (Improving)")
                                    elif change_pct > 0:
                                        st.error(f"📈 +{change_pct:.1f}% (Worsening)")
                                    else:
                                        st.info(f"➡️ 0% (Stable)")
                                else:
                                    st.info("No data for comparison")
                        
                        with col3:
                            st.write("**Return Rate Trend:**")
                            if len(monthly_data) > 1:
                                first_month_rate = monthly_data[0]['return_pct_numeric']
                                last_month_rate = monthly_data[-1]['return_pct_numeric']
                                change = last_month_rate - first_month_rate
                                
                                if change < 0:
                                    st.success(f"📉 {change:.1f}% (Improving)")
                                elif change > 0:
                                    st.error(f"📈 +{change:.1f}% (Worsening)")
                                else:
                                    st.info(f"➡️ 0% (Stable)")
                        
                        # ===== OVERALL SUMMARY =====
                        st.subheader("📊 Overall Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        total_net_sales = sum([w['net_sales_numeric'] for w in weekly_data])
                        total_returns = sum([w['returns_numeric'] for w in weekly_data])
                        total_original_order = abs(total_net_sales) + total_returns
                        
                        if total_original_order > 0:
                            total_return_pct = (total_returns / total_original_order) * 100
                        else:
                            total_return_pct = 0
                        
                        if total_net_sales >= 0:
                            col1.metric("Total Net Sales", f"{total_net_sales:.0f} bales")
                        else:
                            col1.metric("Total Net Sales", f"{total_net_sales:.0f} bales", delta="🔴 NEGATIVE", delta_color="inverse")
                        
                        col2.metric("Total Returns", f"{total_returns:.0f} bales")
                        col3.metric("Original Order", f"{total_original_order:.0f} bales")
                        col4.metric("Return Rate", f"{total_return_pct:.1f}%")
                        
                        # Alert if negative net sales
                        if total_net_sales < 0:
                            st.error(f"⚠️ **CRITICAL**: Negative net sales of {total_net_sales:.0f} bales! Returns exceeded sales by {abs(total_net_sales):.0f} bales.")
                        
                        # ===== CHARTS =====
                        st.subheader("📈 Visualizations")
                        
                        # Monthly trend chart
                        monthly_df_plot = monthly_df.copy()
                        monthly_df_plot['Net Sales'] = pd.to_numeric(monthly_df_plot['net_sales_numeric'])
                        monthly_df_plot['Returns'] = pd.to_numeric(monthly_df_plot['returns_numeric'])
                        
                        fig_monthly = go.Figure()
                        fig_monthly.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Net Sales'], name='Net Sales', marker_color='green'))
                        fig_monthly.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Returns'], name='Returns', marker_color='red'))
                        fig_monthly.update_layout(title="Monthly Net Sales vs Returns", barmode='group', height=400)
                        st.plotly_chart(fig_monthly, use_container_width=True)
                        
                        # Return rate trend
                        fig_rate = go.Figure()
                        fig_rate.add_trace(go.Scatter(x=monthly_df_plot['Month'], y=monthly_df_plot['return_pct_numeric'], 
                                                      name='Return Rate', mode='lines+markers', marker=dict(size=10, color='orange')))
                        fig_rate.update_layout(title="Monthly Return Rate Trend", height=400, yaxis_title="Return %")
                        st.plotly_chart(fig_rate, use_container_width=True)
                        
                        # Weekly detail chart
                        weekly_df_plot = weekly_df.copy()
                        weekly_df_plot['Net Sales'] = pd.to_numeric(weekly_df_plot['net_sales_numeric'])
                        weekly_df_plot['Returns'] = pd.to_numeric(weekly_df_plot['returns_numeric'])
                        
                        fig_weekly = go.Figure()
                        fig_weekly.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Net Sales'], name='Net Sales', marker_color='green'))
                        fig_weekly.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Returns'], name='Returns', marker_color='red'))
                        fig_weekly.update_layout(title="Weekly Net Sales vs Returns", barmode='group', height=400)
                        st.plotly_chart(fig_weekly, use_container_width=True)
                
                else:
                    st.warning("⚠️ No data found for this branch")
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
        st.info("📊 Analyzing relationships between order quantities, intervals, and returns...")
        
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if branches:
            selected_branch = st.selectbox("Select Branch for Analysis", sorted(branches))
            branch_row = df[df['Branch'] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Relationship Analysis for {selected_branch}")
                
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                
                # Extract weekly data
                weekly_net_sales = []
                weekly_returns = []
                
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        weekly_net_sales.append(net_sales_val)
                    if pd.notna(returns_val):
                        weekly_returns.append(returns_val)
                
                if weekly_net_sales and weekly_returns:
                    # Calculate statistics
                    avg_net_sales = np.mean(weekly_net_sales)
                    avg_returns = np.mean(weekly_returns)
                    std_net_sales = np.std(weekly_net_sales)
                    std_returns = np.std(weekly_returns)
                    
                    st.subheader("📊 Key Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Avg Weekly Net Sales", f"{avg_net_sales:.0f} bales")
                    col2.metric("Avg Weekly Returns", f"{avg_returns:.0f} bales")
                    col3.metric("Sales Variability", f"{std_net_sales:.0f} bales")
                    col4.metric("Returns Variability", f"{std_returns:.0f} bales")
                    
                    # Check for negative net sales
                    negative_weeks = sum(1 for x in weekly_net_sales if x < 0)
                    if negative_weeks > 0:
                        st.warning(f"⚠️ **{negative_weeks} weeks with negative net sales** (returns exceeded sales)")
                    
                    # Correlation
                    if len(weekly_net_sales) > 1 and len(weekly_returns) > 1:
                        correlation = np.corrcoef(weekly_net_sales, weekly_returns)[0, 1]
                        
                        st.subheader("🔍 Relationship Insights")
                        
                        if correlation > 0.7:
                            st.warning(f"🔴 **STRONG POSITIVE CORRELATION ({correlation:.2f})**: Higher net sales lead to higher returns. This suggests quality or handling issues.")
                        elif correlation > 0.3:
                            st.info(f"🟡 **MODERATE POSITIVE CORRELATION ({correlation:.2f})**: Some relationship between net sales and returns.")
                        elif correlation > -0.3:
                            st.success(f"🟢 **WEAK/NO CORRELATION ({correlation:.2f})**: Net sales and returns are independent.")
                        else:
                            st.success(f"🟢 **NEGATIVE CORRELATION ({correlation:.2f})**: Higher net sales actually lead to lower returns (good sign!).")
                    
                    # Trend analysis
                    st.subheader("📈 Trend Analysis")
                    
                    if len(weekly_net_sales) > 1:
                        sales_trend = "Increasing" if weekly_net_sales[-1] > weekly_net_sales[0] else "Decreasing" if weekly_net_sales[-1] < weekly_net_sales[0] else "Stable"
                        returns_trend = "Increasing" if weekly_returns[-1] > weekly_returns[0] else "Decreasing" if weekly_returns[-1] < weekly_returns[0] else "Stable"
                        
                        st.write(f"**Net Sales Trend:** {sales_trend}")
                        st.write(f"**Returns Trend:** {returns_trend}")

# ============================================================================
# PAGE 4: OPTIMAL ORDER RECOMMENDATIONS
# ============================================================================
elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("💡 Generating recommendations based on order patterns...")
        
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if branches:
            selected_branch = st.selectbox("Select Branch for Recommendations", sorted(branches))
            branch_row = df[df['Branch'] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Recommendations for {selected_branch}")
                
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                
                # Extract weekly data
                weekly_net_sales = []
                weekly_returns = []
                
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        weekly_net_sales.append(net_sales_val)
                    if pd.notna(returns_val):
                        weekly_returns.append(returns_val)
                
                if weekly_net_sales and weekly_returns:
                    avg_net_sales = np.mean(weekly_net_sales)
                    avg_returns = np.mean(weekly_returns)
                    
                    # Calculate return percentage
                    avg_original_order = abs(avg_net_sales) + avg_returns
                    if avg_original_order > 0:
                        return_rate = (avg_returns / avg_original_order) * 100
                    else:
                        return_rate = 0
                    
                    st.subheader("📋 Current Pattern")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Avg Weekly Net Sales", f"{avg_net_sales:.0f} bales")
                    col2.metric("Avg Weekly Returns", f"{avg_returns:.0f} bales")
                    col3.metric("Avg Original Order", f"{avg_original_order:.0f} bales")
                    col4.metric("Return Rate", f"{return_rate:.1f}%")
                    
                    st.subheader("✅ Recommendations")
                    
                    if avg_net_sales < 0:
                        st.error("🔴 **CRITICAL - NEGATIVE NET SALES**")
                        st.write("- **IMMEDIATE ACTION REQUIRED**")
                        st.write("- Returns are exceeding sales")
                        st.write("- Reduce order quantities significantly (50%+)")
                        st.write("- Investigate critical quality/handling issues")
                        st.write("- Consider temporary halt to orders until issues resolved")
                    elif return_rate > 50:
                        st.error("🔴 **CRITICAL - EXTREMELY HIGH RETURN RATE**")
                        st.write("- Reduce order quantities by 50%+")
                        st.write("- Investigate quality and handling issues immediately")
                        st.write("- Increase order frequency for fresher stock")
                    elif return_rate > 30:
                        st.error("🔴 **HIGH RETURN RATE**")
                        st.write("- Reduce order quantities by 30-40%")
                        st.write("- Investigate quality and handling issues")
                        st.write("- Increase order frequency for fresher stock")
                    elif return_rate > 20:
                        st.warning("🟡 **MODERATE-HIGH RETURN RATE**")
                        st.write("- Reduce order quantities by 20-25%")
                        st.write("- Monitor quality closely")
                        st.write("- Consider more frequent orders")
                    elif return_rate > 15:
                        st.warning("🟡 **MODERATE RETURN RATE**")
                        st.write("- Reduce order quantities by 10-15%")
                        st.write("- Monitor returns trend")
                    elif return_rate > 10:
                        st.info("🟡 **ACCEPTABLE RETURN RATE**")
                        st.write("- Maintain current quantities")
                        st.write("- Monitor returns trend")
                    else:
                        st.success("🟢 **EXCELLENT PERFORMANCE**")
                        st.write("- Consider increasing order quantities by 10-15%")
                        st.write("- Maintain current practices")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v14.0\n\nMonth-by-month analysis added!")
