import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_monthly_metrics, get_active_periods

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📊 Dashboard",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

def calculate_volatility(monthly_data):
    """Calculate volatility score (std dev of return rates)"""
    return_rates = [m['return_rate'] for m in monthly_data if m['has_data']]
    if len(return_rates) > 1:
        volatility = np.std(return_rates)
    else:
        volatility = 0
    return volatility

def get_sales_volume_category(total_sales):
    """Categorize branch by sales volume"""
    abs_sales = abs(total_sales)
    if abs_sales > 500:
        return "High Volume"
    elif abs_sales > 200:
        return "Medium Volume"
    elif abs_sales > 50:
        return "Low Volume"
    else:
        return "Very Low Volume"

if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data (CSV)")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            df = df.rename(columns={df.columns[0]: 'Branch'})
            st.session_state.data = df
            st.success("✅ Data uploaded and cleaned successfully!")
            st.subheader("📊 Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            col3.metric("Unique Branches", df['Branch'].nunique())
            col4.metric("Data Pairs (Weeks)", (len(df.columns) - 1) // 2)
            st.subheader("✅ Ready for Analysis!")
            st.write("Go to **Dashboard** to see overall summary of all branches.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif page == "📊 Dashboard":
    st.header("Overall Branch Performance Dashboard")
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            branch_metrics = []
            
            for branch in branches:
                branch_row = df[df['Branch'] == branch]
                if len(branch_row) > 0:
                    monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
                    active_periods = get_active_periods(monthly_data)
                    
                    if active_periods:
                        current_period = active_periods[-1]
                        current_period_start = current_period[0]['month_num']
                        current_period_end = current_period[-1]['month_num']
                        
                        month_7 = monthly_data[6]
                        is_active_m7 = month_7['has_data']
                        
                        first_active_month = active_periods[0][0]['month_num']
                        
                        if is_active_m7:
                            m7_return_rate = month_7['return_rate']
                            m7_sales = month_7['sales']
                        else:
                            m7_return_rate = None
                            m7_sales = None
                        
                        month_6 = monthly_data[5]
                        m6_return_rate = month_6['return_rate'] if month_6['has_data'] else None
                        
                        if is_active_m7 and m6_return_rate is not None:
                            m6_m7_trend = "📉" if m7_return_rate < m6_return_rate else "📈" if m7_return_rate > m6_return_rate else "➡️"
                            m6_m7_change = m7_return_rate - m6_return_rate
                        else:
                            m6_m7_trend = None
                            m6_m7_change = None
                        
                        first_period_start = active_periods[0][0]
                        last_period_end = active_periods[-1][-1]
                        
                        overall_trend = "📉" if last_period_end['return_rate'] < first_period_start['return_rate'] else "📈" if last_period_end['return_rate'] > first_period_start['return_rate'] else "➡️"
                        overall_change = last_period_end['return_rate'] - first_period_start['return_rate']
                        
                        if len(active_periods) > 1:
                            period_info = f"M{current_period_start}-M{current_period_end} (was M{first_active_month}-M{active_periods[-2][-1]['month_num']})"
                        else:
                            period_info = f"M{current_period_start}-M{current_period_end}"
                        
                        total_sales = sum([m['sales'] for m in monthly_data])
                        total_returns = sum([m['returns'] for m in monthly_data])
                        
                        volatility = calculate_volatility(monthly_data)
                        volume_category = get_sales_volume_category(abs(total_sales))
                        
                        if is_active_m7:
                            if m7_sales < 0:
                                status = "🔴 CRITICAL"
                                priority = 1
                            elif m7_return_rate > 30:
                                status = "🔴 HIGH"
                                priority = 2
                            elif m7_return_rate > 20:
                                status = "🟡 MODERATE"
                                priority = 3
                            elif m7_return_rate > 15:
                                status = "🟡 WATCH"
                                priority = 4
                            else:
                                status = "🟢 GOOD"
                                priority = 5
                            active_status = "Active"
                        else:
                            last_return_rate = last_period_end['return_rate']
                            if last_return_rate > 30:
                                status = "🔴 DELISTED (High Returns)"
                                priority = 2
                            elif last_return_rate > 20:
                                status = "🟡 DELISTED (Moderate Returns)"
                                priority = 3
                            else:
                                status = "⚪ DELISTED"
                                priority = 6
                            active_status = "Delisted"
                            m7_return_rate = last_return_rate
                        
                        worsening = m6_m7_change is not None and m6_m7_change > 5
                        if worsening and priority > 2:
                            priority -= 1
                        
                        high_volatility = volatility > 10
                        if high_volatility and priority > 3:
                            priority -= 1
                        
                        branch_metrics.append({
                            'Branch': branch,
                            'Active Status': active_status,
                            'Period': period_info,
                            'M7 Return Rate': m7_return_rate,
                            'M7 Sales': m7_sales if is_active_m7 else None,
                            'M6→M7 Trend': m6_m7_trend,
                            'M6→M7 Change': m6_m7_change,
                            'Overall Trend': overall_trend,
                            'Overall Change': overall_change,
                            'Total Sales': total_sales,
                            'Total Returns': total_returns,
                            'Volume Category': volume_category,
                            'Volatility': volatility,
                            'High Volatility': high_volatility,
                            'Status': status,
                            'Priority': priority,
                            'Worsening': worsening,
                            'monthly_data': monthly_data
                        })
            
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                
                st.subheader("📊 Overall Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                active_branches = len(metrics_df[metrics_df['Active Status'] == 'Active'])
                delisted_branches = len(metrics_df[metrics_df['Active Status'] == 'Delisted'])
                col1.metric("Total Branches", len(metrics_df))
                col2.metric("Active (M7)", active_branches)
                col3.metric("Delisted", delisted_branches)
                col4.metric("Avg M7 Return Rate", f"{metrics_df[metrics_df['Active Status'] == 'Active']['M7 Return Rate'].mean():.1f}%")
                critical_count = len(metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')])
                col5.metric("Critical/High Issues", critical_count, delta=f"🔴" if critical_count > 0 else "✅")
                
                st.subheader("🟢 Active Branches (Month 7)")
                active_df = metrics_df[metrics_df['Active Status'] == 'Active'].sort_values('Priority')
                if len(active_df) > 0:
                    display_active = active_df[['Branch', 'Period', 'M7 Return Rate', 'Volume Category', 'Volatility', 'M6→M7 Trend', 'Overall Trend', 'Status']].copy()
                    display_active['M7 Return Rate'] = display_active['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_active['Volatility'] = display_active['Volatility'].apply(lambda x: f"{x:.1f}%" if x > 0 else "N/A")
                    st.dataframe(display_active, use_container_width=True)
                    st.info("💡 **Volume Category:** Sales magnitude | **Volatility:** Return rate consistency | **M6→M7:** Latest trend")
                
                critical_branches = metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')].sort_values('Priority')
                if len(critical_branches) > 0:
                    st.subheader("🔴 Branches Needing Immediate Attention")
                    display_critical = critical_branches[['Branch', 'Active Status', 'Period', 'M7 Return Rate', 'Volume Category', 'Volatility', 'M6→M7 Trend', 'Status']].copy()
                    display_critical['M7 Return Rate'] = display_critical['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_critical['Volatility'] = display_critical['Volatility'].apply(lambda x: f"{x:.1f}%" if x > 0 else "N/A")
                    st.dataframe(display_critical, use_container_width=True)
                
                worsening_branches = metrics_df[metrics_df['Worsening'] == True].sort_values('M6→M7 Change', ascending=False)
                if len(worsening_branches) > 0:
                    st.subheader("⚠️ Branches with Worsening Return Rates (M6→M7)")
                    display_worsening = worsening_branches[['Branch', 'Period', 'M7 Return Rate', 'Volume Category', 'M6→M7 Change', 'Status']].copy()
                    display_worsening['M7 Return Rate'] = display_worsening['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_worsening['M6→M7 Change'] = display_worsening['M6→M7 Change'].apply(lambda x: f"{x:+.1f}%")
                    st.dataframe(display_worsening, use_container_width=True)
                
                volatile_branches = metrics_df[metrics_df['High Volatility'] == True].sort_values('Volatility', ascending=False)
                if len(volatile_branches) > 0:
                    st.subheader("📊 Branches with High Volatility (Unstable Performance)")
                    display_volatile = volatile_branches[['Branch', 'Period', 'M7 Return Rate', 'Volatility', 'Volume Category', 'Status']].copy()
                    display_volatile['M7 Return Rate'] = display_volatile['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_volatile['Volatility'] = display_volatile['Volatility'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_volatile, use_container_width=True)
                    st.info("💡 **High Volatility:** Return rate varies significantly month-to-month. Indicates inconsistent performance or handling issues.")
                
                delisted_df = metrics_df[metrics_df['Active Status'] == 'Delisted'].sort_values('Priority')
                if len(delisted_df) > 0:
                    st.subheader("⚪ Delisted Branches")
                    display_delisted = delisted_df[['Branch', 'Period', 'Total Sales', 'Volume Category', 'Overall Trend', 'Status']].copy()
                    display_delisted['Total Sales'] = display_delisted['Total Sales'].apply(lambda x: f"{x:.0f} bales")
                    st.dataframe(display_delisted, use_container_width=True)
                
                st.subheader("📊 Visualizations")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    fig_returns = go.Figure()
                    fig_returns.add_trace(go.Bar(x=active_only['Branch'].str[:30], y=active_only['M7 Return Rate'], marker=dict(color=active_only['M7 Return Rate'], colorscale='RdYlGn_r', showscale=True)))
                    fig_returns.update_layout(title="Month 7 Return Rate (Active Branches)", height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_returns, use_container_width=True)
                
                with col2:
                    volume_counts = metrics_df['Volume Category'].value_counts()
                    fig_volume = go.Figure()
                    fig_volume.add_trace(go.Bar(x=volume_counts.index, y=volume_counts.values, marker_color=['darkgreen', 'green', 'orange', 'red']))
                    fig_volume.update_layout(title="Branches by Sales Volume", height=400)
                    st.plotly_chart(fig_volume, use_container_width=True)
                
                with col3:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    fig_volatility = go.Figure()
                    fig_volatility.add_trace(go.Scatter(x=active_only['M7 Return Rate'], y=active_only['Volatility'], mode='markers', marker=dict(size=10, color=active_only['M7 Return Rate'], colorscale='RdYlGn_r', showscale=True), text=active_only['Branch'], hovertemplate='<b>%{text}</b><br>Return Rate: %{x:.1f}%<br>Volatility: %{y:.1f}%<extra></extra>'))
                    fig_volatility.update_layout(title="Return Rate vs Volatility", xaxis_title="Return Rate (%)", yaxis_title="Volatility (%)", height=400)
                    st.plotly_chart(fig_volatility, use_container_width=True)
                
                st.subheader("📈 Trend Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**M6→M7 Trends (Active Branches):**")
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    improving = len(active_only[active_only['M6→M7 Trend'] == '📉'])
                    worsening = len(active_only[active_only['M6→M7 Trend'] == '📈'])
                    stable = len(active_only[active_only['M6→M7 Trend'] == '➡️'])
                    fig_m6m7 = go.Figure(data=[go.Pie(labels=['📉 Improving', '📈 Worsening', '➡️ Stable'], values=[improving, worsening, stable], marker=dict(colors=['green', 'red', 'gray']))])
                    st.plotly_chart(fig_m6m7, use_container_width=True)
                
                with col2:
                    st.write("**Overall Trends (All Branches):**")
                    improving_overall = len(metrics_df[metrics_df['Overall Trend'] == '📉'])
                    worsening_overall = len(metrics_df[metrics_df['Overall Trend'] == '📈'])
                    stable_overall = len(metrics_df[metrics_df['Overall Trend'] == '➡️'])
                    fig_overall = go.Figure(data=[go.Pie(labels=['📉 Improving', '📈 Worsening', '➡️ Stable'], values=[improving_overall, worsening_overall, stable_overall], marker=dict(colors=['green', 'red', 'gray']))])
                    st.plotly_chart(fig_overall, use_container_width=True)
                
                st.subheader("🔍 Peer Comparison")
                active_only = metrics_df[metrics_df['Active Status'] == 'Active'].copy()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Top Performers (Lowest Return Rate):**")
                    top_performers = active_only.nsmallest(5, 'M7 Return Rate')[['Branch', 'M7 Return Rate', 'Volume Category']]
                    for idx, row in top_performers.iterrows():
                        st.write(f"  🟢 {row['Branch']}: {row['M7 Return Rate']:.1f}% ({row['Volume Category']})")
                
                with col2:
                    st.write("**Bottom Performers (Highest Return Rate):**")
                    bottom_performers = active_only.nlargest(5, 'M7 Return Rate')[['Branch', 'M7 Return Rate', 'Volume Category']]
                    for idx, row in bottom_performers.iterrows():
                        st.write(f"  🔴 {row['Branch']}: {row['M7 Return Rate']:.1f}% ({row['Volume Category']})")
                
                st.write("**Average Return Rate by Volume Category:**")
                avg_by_volume = active_only.groupby('Volume Category')['M7 Return Rate'].mean().sort_values()
                for volume, avg_rate in avg_by_volume.items():
                    st.write(f"  • {volume}: {avg_rate:.1f}%")

elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis - Week by Week & Month by Month")
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            branch_row = df[df['Branch'] == selected_branch]
            if len(branch_row) > 0:
                st.subheader(f"Performance Analysis for {selected_branch}")
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                weekly_data = []
                week_num = 1
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    if pd.notna(net_sales_val) or pd.notna(returns_val):
                        net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
                        returns_val = returns_val if pd.notna(returns_val) else 0
                        original_order = abs(net_sales_val) + returns_val
                        if original_order > 0:
                            return_pct = (returns_val / original_order) * 100
                        else:
                            return_pct = 0
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
                    st.subheader("📅 Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    display_weekly = weekly_df[['Week', 'Net Sales', 'Returns', 'Return %', 'Status']].copy()
                    st.dataframe(display_weekly, use_container_width=True)
                    st.subheader("📊 Monthly Performance")
                    weeks_per_month = 5
                    monthly_data = []
                    for month_num in range(1, 10):
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
                        st.subheader("📈 Visualizations")
                        monthly_df_plot = monthly_df.copy()
                        monthly_df_plot['Net Sales'] = pd.to_numeric(monthly_df_plot['net_sales_numeric'])
                        monthly_df_plot['Returns'] = pd.to_numeric(monthly_df_plot['returns_numeric'])
                        fig_monthly = go.Figure()
                        fig_monthly.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Net Sales'], name='Net Sales', marker_color='green'))
                        fig_monthly.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Returns'], name='Returns', marker_color='red'))
                        fig_monthly.update_layout(title="Monthly Net Sales vs Returns", barmode='group', height=400)
                        st.plotly_chart(fig_monthly, use_container_width=True)
                        fig_rate = go.Figure()
                        fig_rate.add_trace(go.Scatter(x=monthly_df_plot['Month'], y=monthly_df_plot['return_pct_numeric'], name='Return Rate', mode='lines+markers', marker=dict(size=10, color='orange')))
                        fig_rate.update_layout(title="Monthly Return Rate Trend", height=400, yaxis_title="Return %")
                        st.plotly_chart(fig_rate, use_container_width=True)
                        weekly_df_plot = weekly_df.copy()
                        weekly_df_plot['Net Sales'] = pd.to_numeric(weekly_df_plot['net_sales_numeric'])
                        weekly_df_plot['Returns'] = pd.to_numeric(weekly_df_plot['returns_numeric'])
                        fig_weekly = go.Figure()
                        fig_weekly.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Net Sales'], name='Net Sales', marker_color='green'))
                        fig_weekly.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Returns'], name='Returns', marker_color='red'))
                        fig_weekly.update_layout(title="Weekly Net Sales vs Returns", barmode='group', height=400)
                        st.plotly_chart(fig_weekly, use_container_width=True)

elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis")
    st.info("📊 Coming soon...")

elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Recommendations")
    st.info("💡 Coming soon...")

st.sidebar.markdown("---")
st.sidebar.info("
st.sidebar.info("🍞 **Chapati Analytics Agent** v18.0\n\nAdded: Volatility, Volume Context, Peer Comparison!")
