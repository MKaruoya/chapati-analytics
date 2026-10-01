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
    "📊 Dashboard",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

def calculate_monthly_metrics(branch_row, numeric_cols):
    """Calculate metrics for each month"""
    weeks_per_month = 5
    monthly_metrics = []
    
    for month_num in range(1, 10):
        start_idx = (month_num - 1) * weeks_per_month * 2
        end_idx = month_num * weeks_per_month * 2
        
        month_sales = 0
        month_returns = 0
        has_data = False
        
        for i in range(start_idx, min(end_idx, len(numeric_cols) - 1), 2):
            if i < len(numeric_cols) - 1:
                try:
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        month_sales += net_sales_val
                        has_data = True
                    if pd.notna(returns_val):
                        month_returns += returns_val
                except:
                    pass
        
        if has_data:
            original_order = abs(month_sales) + month_returns
            if original_order > 0:
                return_rate = (month_returns / original_order) * 100
            else:
                return_rate = 0
            
            monthly_metrics.append({
                'month_num': month_num,
                'month': f"M{month_num}",
                'sales': month_sales,
                'returns': month_returns,
                'return_rate': return_rate
            })
    
    return monthly_metrics

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
                    
                    if monthly_data and len(monthly_data) > 0:
                        latest_month = monthly_data[-1]
                        first_month = monthly_data[0]
                        
                        sales_trend = "📈" if latest_month['sales'] > first_month['sales'] else "📉" if latest_month['sales'] < first_month['sales'] else "➡️"
                        returns_trend = "📈" if latest_month['returns'] > first_month['returns'] else "📉" if latest_month['returns'] < first_month['returns'] else "➡️"
                        return_rate_trend = "📈" if latest_month['return_rate'] > first_month['return_rate'] else "📉" if latest_month['return_rate'] < first_month['return_rate'] else "➡️"
                        
                        sales_change = ((latest_month['sales'] - first_month['sales']) / abs(first_month['sales']) * 100) if first_month['sales'] != 0 else 0
                        return_rate_change = latest_month['return_rate'] - first_month['return_rate']
                        
                        if latest_month['sales'] < 0:
                            status = "🔴 CRITICAL"
                            priority = 1
                        elif latest_month['return_rate'] > 30:
                            status = "🔴 HIGH"
                            priority = 2
                        elif latest_month['return_rate'] > 20:
                            status = "🟡 MODERATE"
                            priority = 3
                        elif latest_month['return_rate'] > 15:
                            status = "🟡 WATCH"
                            priority = 4
                        else:
                            status = "🟢 GOOD"
                            priority = 5
                        
                        worsening = return_rate_change > 5
                        if worsening and priority > 2:
                            priority -= 1
                        
                        branch_metrics.append({
                            'Branch': branch,
                            'Latest Month': latest_month['month'],
                            'Latest Sales': latest_month['sales'],
                            'Latest Returns': latest_month['returns'],
                            'Latest Return Rate': latest_month['return_rate'],
                            'Sales Trend': sales_trend,
                            'Sales Change %': sales_change,
                            'Returns Trend': returns_trend,
                            'Return Rate Trend': return_rate_trend,
                            'Return Rate Change': return_rate_change,
                            'Status': status,
                            'Priority': priority,
                            'Worsening': worsening,
                            'Months': len(monthly_data)
                        })
            
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                
                st.subheader("📊 Overall Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                col1.metric("Total Branches", len(metrics_df))
                col2.metric("Avg Latest Return Rate", f"{metrics_df['Latest Return Rate'].mean():.1f}%")
                col3.metric("Latest Total Sales", f"{metrics_df['Latest Sales'].sum():.0f} bales")
                col4.metric("Latest Total Returns", f"{metrics_df['Latest Returns'].sum():.0f} bales")
                
                critical_count = len(metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')])
                col5.metric("Critical/High Issues", critical_count, delta=f"🔴" if critical_count > 0 else "✅")
                
                critical_branches = metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')].sort_values('Priority')
                if len(critical_branches) > 0:
                    st.subheader("🔴 Branches Needing Immediate Attention (Latest Month)")
                    
                    display_critical = critical_branches[[
                        'Branch', 'Latest Month', 'Latest Return Rate', 'Return Rate Trend', 
                        'Return Rate Change', 'Status'
                    ]].copy()
                    display_critical['Latest Return Rate'] = display_critical['Latest Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_critical['Return Rate Change'] = display_critical['Return Rate Change'].apply(lambda x: f"{x:+.1f}%")
                    
                    st.dataframe(display_critical, use_container_width=True)
                    
                    st.info("💡 **Note:** Status is based on LATEST month performance, not overall average. Trend shows if situation is improving or worsening.")
                
                worsening_branches = metrics_df[metrics_df['Worsening'] == True].sort_values('Return Rate Change', ascending=False)
                if len(worsening_branches) > 0:
                    st.subheader("⚠️ Branches with Worsening Return Rates")
                    
                    display_worsening = worsening_branches[[
                        'Branch', 'Latest Month', 'Latest Return Rate', 'Return Rate Change', 'Status'
                    ]].copy()
                    display_worsening['Latest Return Rate'] = display_worsening['Latest Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_worsening['Return Rate Change'] = display_worsening['Return Rate Change'].apply(lambda x: f"{x:+.1f}%")
                    
                    st.dataframe(display_worsening, use_container_width=True)
                
                st.subheader("📈 Sales Performance (Latest Month)")
                
                tab1, tab2, tab3 = st.tabs(["Declining Sales", "Growing Sales", "All Branches"])
                
                with tab1:
                    declining = metrics_df[metrics_df['Sales Change %'] < -5].sort_values('Sales Change %')
                    if len(declining) > 0:
                        display_declining = declining[['Branch', 'Latest Month', 'Latest Sales', 'Sales Change %', 'Status']].copy()
                        display_declining['Sales Change %'] = display_declining['Sales Change %'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(display_declining, use_container_width=True)
                    else:
                        st.info("✅ No branches with declining sales in latest month")
                
                with tab2:
                    growing = metrics_df[metrics_df['Sales Change %'] > 5].sort_values('Sales Change %', ascending=False)
                    if len(growing) > 0:
                        display_growing = growing[['Branch', 'Latest Month', 'Latest Sales', 'Sales Change %', 'Status']].copy()
                        display_growing['Sales Change %'] = display_growing['Sales Change %'].apply(lambda x: f"{x:+.1f}%")
                        st.dataframe(display_growing, use_container_width=True)
                    else:
                        st.info("ℹ️ No branches with significant growth in latest month")
                
                with tab3:
                    display_all = metrics_df[['Branch', 'Latest Month', 'Latest Sales', 'Latest Return Rate', 'Return Rate Trend', 'Status']].copy()
                    display_all['Latest Return Rate'] = display_all['Latest Return Rate'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_all.sort_values('Latest Return Rate', ascending=False), use_container_width=True)
                
                st.subheader("🔍 Return Rate Analysis (Latest Month)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Highest Return Rates:**")
                    high_returns = metrics_df.nlargest(5, 'Latest Return Rate')[['Branch', 'Latest Return Rate', 'Return Rate Trend']]
                    for idx, row in high_returns.iterrows():
                        st.write(f"  🔴 {row['Branch']}: {row['Latest Return Rate']:.1f}% {row['Return Rate Trend']}")
                
                with col2:
                    st.write("**Lowest Return Rates:**")
                    low_returns = metrics_df.nsmallest(5, 'Latest Return Rate')[['Branch', 'Latest Return Rate', 'Return Rate Trend']]
                    for idx, row in low_returns.iterrows():
                        st.write(f"  🟢 {row['Branch']}: {row['Latest Return Rate']:.1f}% {row['Return Rate Trend']}")
                
                st.subheader("📊 Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_returns = go.Figure()
                    fig_returns.add_trace(go.Bar(
                        x=metrics_df['Branch'].str[:30],
                        y=metrics_df['Latest Return Rate'],
                        marker=dict(color=metrics_df['Latest Return Rate'], colorscale='RdYlGn_r', showscale=True)
                    ))
                    fig_returns.update_layout(title="Latest Month Return Rate by Branch", height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_returns, use_container_width=True)
                
                with col2:
                    fig_sales = go.Figure()
                    fig_sales.add_trace(go.Bar(
                        x=metrics_df['Branch'].str[:30],
                        y=metrics_df['Latest Sales'],
                        marker_color=['green' if x > 0 else 'red' for x in metrics_df['Latest Sales']]
                    ))
                    fig_sales.update_layout(title="Latest Month Sales by Branch", height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_sales, use_container_width=True)
                
                st.subheader("📈 Trend Analysis (First Month vs Latest Month)")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Sales Trends:**")
                    improving_sales = len(metrics_df[metrics_df['Sales Change %'] > 5])
                    declining_sales = len(metrics_df[metrics_df['Sales Change %'] < -5])
                    stable_sales = len(metrics_df[(metrics_df['Sales Change %'] >= -5) & (metrics_df['Sales Change %'] <= 5)])
                    
                    fig_sales_trend = go.Figure(data=[
                        go.Pie(labels=['📈 Growing', '📉 Declining', '➡️ Stable'],
                               values=[improving_sales, declining_sales, stable_sales],
                               marker=dict(colors=['green', 'red', 'gray']))
                    ])
                    st.plotly_chart(fig_sales_trend, use_container_width=True)
                
                with col2:
                    st.write("**Return Rate Status (Latest Month):**")
                    critical = len(metrics_df[metrics_df['Latest Return Rate'] > 30])
                    high = len(metrics_df[(metrics_df['Latest Return Rate'] > 20) & (metrics_df['Latest Return Rate'] <= 30)])
                    moderate = len(metrics_df[(metrics_df['Latest Return Rate'] > 15) & (metrics_df['Latest Return Rate'] <= 20)])
                    good = len(metrics_df[metrics_df['Latest Return Rate'] <= 15])
                    
                    fig_status = go.Figure(data=[
                        go.Pie(labels=['🔴 Critical', '🟡 High', '🟡 Moderate', '🟢 Good'],
                               values=[critical, high, moderate, good],
                               marker=dict(colors=['darkred', 'orange', 'yellow', 'green']))
                    ])
                    st.plotly_chart(fig_status, use_container_width=True)

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
                        fig_rate.add_trace(go.Scatter(x=monthly_df_plot['Month'], y=monthly_df_plot['return_pct_numeric'], 
                                                      name='Return Rate', mode='lines+markers', marker=dict(size=10, color='orange')))
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
st.sidebar.info("🍞 **Chapati Analytics Agent** v16.0\n\nMonth-based dashboard!")
