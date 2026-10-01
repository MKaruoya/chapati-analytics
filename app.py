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
    """Calculate volatility score"""
    return_rates = [m['return_rate'] for m in monthly_data if m['has_data']]
    if len(return_rates) > 1:
        return np.std(return_rates)
    return 0

def get_sales_volume_category(total_sales):
    """Categorize by sales volume"""
    abs_sales = abs(total_sales)
    if abs_sales > 500:
        return "High Volume"
    elif abs_sales > 200:
        return "Medium Volume"
    elif abs_sales > 50:
        return "Low Volume"
    else:
        return "Very Low Volume"

def extract_outlet_name(branch_name):
    """Extract outlet name from branch name"""
    if isinstance(branch_name, str) and '-' in branch_name:
        return branch_name.split('-')[0].strip()
    return None

def calculate_quarter_trend(monthly_data):
    """Calculate quarter trend"""
    active_months = [m for m in monthly_data if m['has_data']]
    
    if len(active_months) < 3:
        return None, None, None
    
    last_quarter = active_months[-3:]
    last_quarter_avg = np.mean([m['return_rate'] for m in last_quarter])
    
    if len(active_months) >= 6:
        prev_quarter = active_months[-6:-3]
        prev_quarter_avg = np.mean([m['return_rate'] for m in prev_quarter])
    else:
        prev_quarter_avg = None
    
    if prev_quarter_avg is not None:
        quarter_change = last_quarter_avg - prev_quarter_avg
        if quarter_change < -2:
            trend = "📉 Improving"
        elif quarter_change > 2:
            trend = "📈 Worsening"
        else:
            trend = "➡️ Stable"
    else:
        quarter_change = None
        trend = "N/A"
    
    return last_quarter_avg, quarter_change, trend

def calculate_order_metrics(branch_row, numeric_cols):
    """Calculate order quantities and intervals"""
    orders = []
    
    for i in range(0, len(numeric_cols) - 1, 2):
        net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
        returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
        
        if pd.notna(net_sales_val) or pd.notna(returns_val):
            net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
            returns_val = returns_val if pd.notna(returns_val) else 0
            
            original_order = abs(net_sales_val) + returns_val
            return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
            
            orders.append({
                'order_quantity': original_order,
                'net_sales': net_sales_val,
                'returns': returns_val,
                'return_pct': return_pct
            })
    
    # Calculate intervals (weeks between orders with data)
    intervals = []
    last_order_week = None
    for week, order in enumerate(orders):
        if order['order_quantity'] > 0:
            if last_order_week is not None:
                interval = week - last_order_week
                intervals.append(interval)
            last_order_week = week
    
    return orders, intervals

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
            st.write("Go to **Dashboard** to select an outlet and compare all its branches.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif page == "📊 Dashboard":
    st.header("📊 Outlet Performance Dashboard")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
        
        if not outlet_names:
            st.error("❌ No outlets found in data!")
        else:
            st.subheader("🏪 Select Outlet to Analyze")
            selected_outlet = st.selectbox("Choose an outlet:", outlet_names)
            
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
            
            st.info(f"📍 Analyzing **{selected_outlet}** - Found {len(outlet_branches)} branches")
            
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            branch_metrics = []
            
            for branch in outlet_branches:
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
                        
                        if is_active_m7:
                            m7_return_rate = month_7['return_rate']
                            m7_sales = month_7['sales']
                        else:
                            m7_return_rate = None
                            m7_sales = None
                        
                        last_quarter_avg, quarter_change, quarter_trend = calculate_quarter_trend(monthly_data)
                        
                        first_period_start = active_periods[0][0]
                        last_period_end = active_periods[-1][-1]
                        
                        overall_trend = "📉" if last_period_end['return_rate'] < first_period_start['return_rate'] else "📈" if last_period_end['return_rate'] > first_period_start['return_rate'] else "➡️"
                        overall_change = last_period_end['return_rate'] - first_period_start['return_rate']
                        
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
                                status = "🔴 DELISTED"
                                priority = 2
                            else:
                                status = "⚪ DELISTED"
                                priority = 6
                            active_status = "Delisted"
                            m7_return_rate = last_return_rate
                        
                        worsening = quarter_change is not None and quarter_change > 2
                        high_volatility = volatility > 10
                        
                        branch_metrics.append({
                            'Branch': branch,
                            'Active Status': active_status,
                            'Period': period_info,
                            'M7 Return Rate': m7_return_rate,
                            'M7 Sales': m7_sales if is_active_m7 else None,
                            'Last Quarter Avg': last_quarter_avg,
                            'Quarter Trend': quarter_trend,
                            'Quarter Change': quarter_change,
                            'Overall Trend': overall_trend,
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
                
                st.subheader(f"📊 Summary - {selected_outlet}")
                col1, col2, col3, col4, col5 = st.columns(5)
                active_branches = len(metrics_df[metrics_df['Active Status'] == 'Active'])
                delisted_branches = len(metrics_df[metrics_df['Active Status'] == 'Delisted'])
                col1.metric("Total Branches", len(metrics_df))
                col2.metric("Active (M7)", active_branches)
                col3.metric("Delisted", delisted_branches)
                avg_rate = metrics_df[metrics_df['Active Status'] == 'Active']['M7 Return Rate'].mean()
                col4.metric("Avg M7 Return Rate", f"{avg_rate:.1f}%")
                critical_count = len(metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')])
                col5.metric("Critical/High", critical_count)
                
                st.subheader("🟢 Active Branches (Month 7)")
                active_df = metrics_df[metrics_df['Active Status'] == 'Active'].sort_values('Priority')
                if len(active_df) > 0:
                    display_active = active_df[['Branch', 'M7 Return Rate', 'Last Quarter Avg', 'Quarter Trend', 'Volume Category', 'Volatility', 'Overall Trend', 'Status']].copy()
                    display_active['M7 Return Rate'] = display_active['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_active['Last Quarter Avg'] = display_active['Last Quarter Avg'].apply(lambda x: f"{x:.1f}%" if x else "N/A")
                    display_active['Volatility'] = display_active['Volatility'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_active, use_container_width=True)
                else:
                    st.info("No active branches in Month 7")
                
                st.subheader("🔴 Critical Branches")
                critical_df = metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')].sort_values('Priority')
                if len(critical_df) > 0:
                    display_critical = critical_df[['Branch', 'M7 Return Rate', 'Last Quarter Avg', 'Quarter Trend', 'Volume Category', 'Status']].copy()
                    display_critical['M7 Return Rate'] = display_critical['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_critical['Last Quarter Avg'] = display_critical['Last Quarter Avg'].apply(lambda x: f"{x:.1f}%" if x else "N/A")
                    st.dataframe(display_critical, use_container_width=True)
                else:
                    st.success("✅ No critical branches")
                
                st.subheader("⚠️ Worsening Branches (Quarter Trend)")
                worsening_df = metrics_df[metrics_df['Worsening'] == True].sort_values('Quarter Change', ascending=False)
                if len(worsening_df) > 0:
                    display_worsening = worsening_df[['Branch', 'M7 Return Rate', 'Last Quarter Avg', 'Quarter Change', 'Quarter Trend', 'Status']].copy()
                    display_worsening['M7 Return Rate'] = display_worsening['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_worsening['Last Quarter Avg'] = display_worsening['Last Quarter Avg'].apply(lambda x: f"{x:.1f}%" if x else "N/A")
                    display_worsening['Quarter Change'] = display_worsening['Quarter Change'].apply(lambda x: f"{x:+.1f}%" if x else "N/A")
                    st.dataframe(display_worsening, use_container_width=True)
                else:
                    st.success("✅ No worsening branches")
                
                st.subheader("📊 Visualizations")
                col1, col2 = st.columns(2)
                
                with col1:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    if len(active_only) > 0:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(
                            x=active_only['Branch'],
                            y=active_only['M7 Return Rate'],
                            marker=dict(color=active_only['M7 Return Rate'], colorscale='RdYlGn_r'),
                            text=active_only['M7 Return Rate'].apply(lambda x: f"{x:.1f}%"),
                            textposition='auto',
                            hovertemplate='<b>%{x}</b><br>Return Rate: %{y:.1f}%<extra></extra>'
                        ))
                        fig.update_layout(
                            title=f"Month 7 Return Rate - {selected_outlet}",
                            height=500,
                            xaxis_tickangle=-45,
                            xaxis=dict(automargin=True),
                            yaxis_title="Return Rate (%)"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    if len(active_only) > 0:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=active_only['M7 Return Rate'],
                            y=active_only['Volatility'],
                            mode='markers',
                            marker=dict(
                                size=12,
                                color=active_only['M7 Return Rate'],
                                colorscale='RdYlGn_r',
                                showscale=True,
                                colorbar=dict(title="Return Rate (%)")
                            ),
                            text=active_only['Branch'],
                            hovertemplate='<b>%{text}</b><br>Return Rate: %{x:.1f}%<br>Volatility: %{y:.1f}%<extra></extra>'
                        ))
                        fig.update_layout(
                            title="Return Rate vs Volatility",
                            xaxis_title="Return Rate (%)",
                            yaxis_title="Volatility (%)",
                            height=500
                        )
                        st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("🔍 Branch Comparison")
                active_only = metrics_df[metrics_df['Active Status'] == 'Active'].copy()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Best Performing Branches (Lowest M7 Return Rate):**")
                    if len(active_only) > 0:
                        top = active_only.nsmallest(3, 'M7 Return Rate')
                        for idx, row in top.iterrows():
                            st.write(f"  🟢 {row['Branch']}: {row['M7 Return Rate']:.1f}% ({row['Volume Category']})")
                    else:
                        st.write("No active branches")
                
                with col2:
                    st.write("**Worst Performing Branches (Highest M7 Return Rate):**")
                    if len(active_only) > 0:
                        bottom = active_only.nlargest(3, 'M7 Return Rate')
                        for idx, row in bottom.iterrows():
                            st.write(f"  🔴 {row['Branch']}: {row['M7 Return Rate']:.1f}% ({row['Volume Category']})")
                    else:
                        st.write("No active branches")

elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis")
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        if branches:
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            branch_row = df[df['Branch'] == selected_branch]
            if len(branch_row) > 0:
                st.subheader(f"Analysis for {selected_branch}")
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
                        return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
                        weekly_data.append({
                            'Week': f"W{week_num}",
                            'Net Sales': f"{net_sales_val:.0f}",
                            'Returns': f"{returns_val:.0f}",
                            'Return %': f"{return_pct:.1f}%",
                            'net_sales_numeric': net_sales_val,
                            'returns_numeric': returns_val,
                            'return_pct_numeric': return_pct
                        })
                    week_num += 1
                if weekly_data:
                    st.subheader("📅 Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    st.dataframe(weekly_df[['Week', 'Net Sales', 'Returns', 'Return %']], use_container_width=True)
                    
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
                            month_return_pct = (month_returns / month_original * 100) if month_original > 0 else 0
                            monthly_data.append({
                                'Month': f"M{month_num}",
                                'Net Sales': f"{month_sales:.0f}",
                                'Returns': f"{month_returns:.0f}",
                                'Return %': f"{month_return_pct:.1f}%",
                                'net_sales_numeric': month_sales,
                                'returns_numeric': month_returns,
                                'return_pct_numeric': month_return_pct
                            })
                    if monthly_data:
                        monthly_df = pd.DataFrame(monthly_data)
                        st.dataframe(monthly_df[['Month', 'Net Sales', 'Returns', 'Return %']], use_container_width=True)
                        
                        st.subheader("📈 Visualizations")
                        monthly_df_plot = monthly_df.copy()
                        monthly_df_plot['Net Sales'] = pd.to_numeric(monthly_df_plot['net_sales_numeric'])
                        monthly_df_plot['Returns'] = pd.to_numeric(monthly_df_plot['returns_numeric'])
                        
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Net Sales'], name='Net Sales', marker_color='green'))
                        fig.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Returns'], name='Returns', marker_color='red'))
                        fig.update_layout(title="Monthly Net Sales vs Returns", barmode='group', height=400)
                        st.plotly_chart(fig, use_container_width=True)

elif page == "🤖 AI Relationship Analysis":
    st.header("🤖 AI Relationship Analysis: Order Quantities & Intervals vs Returns")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
        
        if not outlet_names:
            st.error("❌ No outlets found in data!")
        else:
            st.subheader("🏪 Select Outlet to Analyze")
            selected_outlet = st.selectbox("Choose an outlet:", outlet_names, key="ai_outlet")
            
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
            
            st.info(f"📍 Analyzing **{selected_outlet}** - Found {len(outlet_branches)} branches")
            
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            branch_analysis = []
            
            for branch in outlet_branches:
                branch_row = df[df['Branch'] == branch]
                if len(branch_row) > 0:
                    orders, intervals = calculate_order_metrics(branch_row, numeric_cols)
                    
                    if orders:
                        avg_order_qty = np.mean([o['order_quantity'] for o in orders if o['order_quantity'] > 0])
                        avg_return_pct = np.mean([o['return_pct'] for o in orders])
                        avg_interval = np.mean(intervals) if intervals else 0
                        
                        branch_analysis.append({
                            'Branch': branch,
                            'Avg Order Qty': avg_order_qty,
                            'Avg Return %': avg_return_pct,
                            'Avg Interval (weeks)': avg_interval,
                            'Total Orders': len([o for o in orders if o['order_quantity'] > 0]),
                            'orders': orders,
                            'intervals': intervals
                        })
            
            if branch_analysis:
                analysis_df = pd.DataFrame(branch_analysis)
                
                st.subheader("📊 Correlation Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Order Quantity vs Return Rate**")
                    corr_qty = analysis_df['Avg Order Qty'].corr(analysis_df['Avg Return %'])
                    st.metric("Correlation", f"{corr_qty:.3f}")
                    
                    if corr_qty > 0.5:
                        st.error("🔴 Strong positive: Larger orders = Higher returns")
                        st.write("**Insight:** Quality or handling issues increase with order size")
                    elif corr_qty > 0.2:
                        st.warning("🟡 Moderate positive: Some relationship")
                    elif corr_qty < -0.2:
                        st.success("🟢 Negative: Larger orders = Lower returns (good!)")
                        st.write("**Insight:** Larger orders are handled better")
                    else:
                        st.info("🟡 Weak: Order size independent of returns")
                
                with col2:
                    st.write("**Order Interval vs Return Rate**")
                    corr_interval = analysis_df['Avg Interval (weeks)'].corr(analysis_df['Avg Return %'])
                    st.metric("Correlation", f"{corr_interval:.3f}")
                    
                    if corr_interval > 0.5:
                        st.error("🔴 Strong positive: Longer intervals = Higher returns")
                        st.write("**Insight:** Longer gaps between orders lead to more returns (freshness issue?)")
                    elif corr_interval > 0.2:
                        st.warning("🟡 Moderate positive: Some relationship")
                    elif corr_interval < -0.2:
                        st.success("🟢 Negative: Longer intervals = Lower returns")
                        st.write("**Insight:** Less frequent orders have fewer returns")
                    else:
                        st.info("🟡 Weak: Order interval independent of returns")
                
                st.subheader("📈 Relationship Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Avg Order Qty'],
                        y=analysis_df['Avg Return %'],
                        mode='markers',
                        marker=dict(size=12, color=analysis_df['Avg Return %'], colorscale='RdYlGn_r'),
                        text=analysis_df['Branch'],
                        hovertemplate='<b>%{text}</b><br>Avg Order Qty: %{x:.0f} bales<br>Avg Return Rate: %{y:.1f}%<extra></extra>'
                    ))
                    
                    if len(analysis_df) > 1:
                        z = np.polyfit(analysis_df['Avg Order Qty'], analysis_df['Avg Return %'], 1)
                        p = np.poly1d(z)
                        fig.add_trace(go.Scatter(
                            x=analysis_df['Avg Order Qty'].sort_values(),
                            y=p(analysis_df['Avg Order Qty'].sort_values()),
                            mode='lines',
                            name='Trend',
                            line=dict(color='red', dash='dash')
                        ))
                    
                    fig.update_layout(
                        title="Order Quantity vs Return Rate",
                        xaxis_title="Average Order Quantity (bales)",
                        yaxis_title="Average Return Rate (%)",
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Avg Interval (weeks)'],
                        y=analysis_df['Avg Return %'],
                        mode='markers',
                        marker=dict(size=12, color=analysis_df['Avg Return %'], colorscale='RdYlGn_r'),
                        text=analysis_df['Branch'],
                        hovertemplate='<b>%{text}</b><br>Avg Interval: %{x:.1f} weeks<br>Avg Return Rate: %{y:.1f}%<extra></extra>'
                    ))
                    
                    if len(analysis_df) > 1:
                        z = np.polyfit(analysis_df['Avg Interval (weeks)'], analysis_df['Avg Return %'], 1)
                        p = np.poly1d(z)
                        fig.add_trace(go.Scatter(
                            x=analysis_df['Avg Interval (weeks)'].sort_values(),
                                                        y=p(analysis_df['Avg Interval (weeks)'].sort_values()),
                            mode='lines',
                            name='Trend',
                            line=dict(color='red', dash='dash')
                        ))
                    
                    fig.update_layout(
                        title="Order Interval vs Return Rate",
                        xaxis_title="Average Order Interval (weeks)",
                        yaxis_title="Average Return Rate (%)",
                        height=450
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📊 Individual Branch Analysis")
                
                st.write("**Detailed Metrics for Each Branch:**")
                display_df = analysis_df[['Branch', 'Avg Order Qty', 'Avg Interval (weeks)', 'Avg Return %', 'Total Orders']].copy()
                display_df['Avg Order Qty'] = display_df['Avg Order Qty'].apply(lambda x: f"{x:.0f} bales")
                display_df['Avg Interval (weeks)'] = display_df['Avg Interval (weeks)'].apply(lambda x: f"{x:.1f}")
                display_df['Avg Return %'] = display_df['Avg Return %'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_df, use_container_width=True)
                
                st.subheader("💡 Key Insights")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Highest Return Rate:**")
                    worst = analysis_df.loc[analysis_df['Avg Return %'].idxmax()]
                    st.write(f"🔴 {worst['Branch']}")
                    st.write(f"Return Rate: {worst['Avg Return %']:.1f}%")
                    st.write(f"Avg Order: {worst['Avg Order Qty']:.0f} bales")
                    st.write(f"Avg Interval: {worst['Avg Interval (weeks)']:.1f} weeks")
                
                with col2:
                    st.write("**Lowest Return Rate:**")
                    best = analysis_df.loc[analysis_df['Avg Return %'].idxmin()]
                    st.write(f"🟢 {best['Branch']}")
                    st.write(f"Return Rate: {best['Avg Return %']:.1f}%")
                    st.write(f"Avg Order: {best['Avg Order Qty']:.0f} bales")
                    st.write(f"Avg Interval: {best['Avg Interval (weeks)']:.1f} weeks")
                
                with col3:
                    st.write("**Outlet Average:**")
                    st.write(f"Avg Return Rate: {analysis_df['Avg Return %'].mean():.1f}%")
                    st.write(f"Avg Order Qty: {analysis_df['Avg Order Qty'].mean():.0f} bales")
                    st.write(f"Avg Interval: {analysis_df['Avg Interval (weeks)'].mean():.1f} weeks")
                
                st.subheader("🎯 Recommendations Based on Analysis")
                
                st.write("**For High Return Rate Branches:**")
                
                for idx, row in analysis_df[analysis_df['Avg Return %'] > analysis_df['Avg Return %'].mean()].iterrows():
                    st.write(f"**{row['Branch']}** (Return Rate: {row['Avg Return %']:.1f}%)")
                    
                    if corr_qty > 0.3:
                        reduction = row['Avg Order Qty'] * 0.8
                        st.write(f"  • Reduce order quantity from {row['Avg Order Qty']:.0f} to ~{reduction:.0f} bales")
                    
                    if corr_interval > 0.3:
                        st.write(f"  • Increase order frequency (reduce interval from {row['Avg Interval (weeks)']:.1f} to ~{row['Avg Interval (weeks)'] * 0.8:.1f} weeks)")
                    
                    if corr_interval < -0.3:
                        st.write(f"  • Maintain or increase order interval (currently {row['Avg Interval (weeks)']:.1f} weeks)")
                    
                    st.write("")

elif page == "💡 Optimal Order Recommendations":
    st.header("💡 Optimal Order Recommendations")
    st.info("💡 Coming soon...")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v26.0\n\nAI Relationship Analysis: Order Qty & Intervals!")
