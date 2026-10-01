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

def calculate_weekly_metrics(branch_row, numeric_cols):
    """Calculate weekly order quantities and returns"""
    weekly_data = []
    
    for i in range(0, len(numeric_cols) - 1, 2):
        net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
        returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
        
        if pd.notna(net_sales_val) or pd.notna(returns_val):
            net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
            returns_val = returns_val if pd.notna(returns_val) else 0
            
            original_order = abs(net_sales_val) + returns_val
            return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
            
            weekly_data.append({
                'week': len(weekly_data) + 1,
                'order_quantity': original_order,
                'net_sales': net_sales_val,
                'returns': returns_val,
                'return_pct': return_pct
            })
    
    return weekly_data

def find_optimal_quantity(weekly_data):
    """Find optimal order quantity for a branch"""
    
    active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
    
    if not active_weeks:
        return None, None, None, "No order data", 0
    
    quantities = [w['order_quantity'] for w in active_weeks]
    returns = [w['return_pct'] for w in active_weeks]
    
    q1 = np.percentile(quantities, 25)
    q2 = np.percentile(quantities, 50)
    q3 = np.percentile(quantities, 75)
    
    q1_returns = [r for q, r in zip(quantities, returns) if q <= q1]
    q2_returns = [r for q, r in zip(quantities, returns) if q1 < q <= q3]
    q3_returns = [r for q, r in zip(quantities, returns) if q > q3]
    
    avg_q1_return = np.mean(q1_returns) if q1_returns else 0
    avg_q2_return = np.mean(q2_returns) if q2_returns else 0
    avg_q3_return = np.mean(q3_returns) if q3_returns else 0
    
    quartile_returns = {
        'Q1 (Low)': (q1, avg_q1_return),
        'Q2 (Medium)': (q2, avg_q2_return),
        'Q3 (High)': (q3, avg_q3_return)
    }
    
    best_quartile = min(quartile_returns.items(), key=lambda x: x[1][1])
    optimal_qty = best_quartile[1][0]
    optimal_return_rate = best_quartile[1][1]
    
    corr = np.corrcoef(quantities, returns)[0, 1]
    
    confidence = min(len(active_weeks) / 35, 1.0)
    
    return optimal_qty, optimal_return_rate, corr, best_quartile[0], confidence

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
            st.write("Navigate to other tabs to analyze the data.")
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
            selected_outlet = st.selectbox("Choose an outlet:", outlet_names, key="dash_outlet")
            
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

elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis - Week by Week & Month by Month")
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        if branches:
            selected_branch = st.selectbox("Select Branch", sorted(branches), key="store_branch")
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
    st.header("🤖 AI Relationship Analysis: Individual Branch Weekly Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not valid_branches:
            st.error("❌ No branches found in data!")
        else:
            st.subheader("🏪 Select Branch to Analyze")
            selected_branch = st.selectbox("Choose a branch:", sorted(valid_branches), key="ai_branch")
            
            branch_row = df[df['Branch'] == selected_branch]
            
            if len(branch_row) > 0:
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                
                if weekly_data:
                    weekly_df = pd.DataFrame(weekly_data)
                    
                    st.info(f"📍 Analyzing **{selected_branch}** - {len(weekly_data)} weeks of data")
                    
                    active_weeks = weekly_df[weekly_df['order_quantity'] > 0]
                    optimal_qty, optimal_return_rate, corr, best_quartile, confidence = find_optimal_quantity(weekly_data)
                    
                    st.subheader("📊 Weekly Correlation Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Correlation:**")
                        st.metric("Order Qty vs Return Rate", f"{corr:.3f}")
                        
                        if corr > 0.3:
                            st.error("🔴 Positive: Larger orders = Higher returns")
                        elif corr < -0.3:
                            st.success("🟢 Negative: Larger orders = Lower returns")
                        else:
                            st.info("🟡 Weak: Independent relationship")
                    
                    with col2:
                        st.write("**Weekly Statistics:**")
                        st.write(f"Total weeks: {len(weekly_df)}")
                        st.write(f"Active weeks: {len(active_weeks)}")
                        st.write(f"Avg order: {active_weeks['order_quantity'].mean():.0f} bales")
                        st.write(f"Avg return rate: {active_weeks['return_pct'].mean():.1f}%")
                    
                    with col3:
                        st.write("**Order Range:**")
                        st.write(f"Min: {active_weeks['order_quantity'].min():.0f} bales")
                        st.write(f"Max: {active_weeks['order_quantity'].max():.0f} bales")
                        st.write(f"Median: {active_weeks['order_quantity'].median():.0f} bales")
                    
                    st.subheader("📈 Weekly Order Quantity vs Return Rate")
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=weekly_df['order_quantity'],
                        y=weekly_df['return_pct'],
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=weekly_df['return_pct'],
                            colorscale='RdYlGn_r',
                            showscale=True,
                            colorbar=dict(title="Return %")
                        ),
                        text=[f"Week {w}<br>Order: {q:.0f} bales<br>Return: {r:.1f}%" 
                              for w, q, r in zip(weekly_df['week'], weekly_df['order_quantity'], weekly_df['return_pct'])],
                        hovertemplate='%{text}<extra></extra>'
                    ))
                    
                    if len(active_weeks) > 1:
                        z = np.polyfit(active_weeks['order_quantity'], active_weeks['return_pct'], 1)
                        p = np.poly1d(z)
                        x_trend = np.linspace(active_weeks['order_quantity'].min(), active_weeks['order_quantity'].max(), 100)
                        fig.add_trace(go.Scatter(
                            x=x_trend,
                            y=p(x_trend),
                            mode='lines',
                            name='Trend',
                            line=dict(color='red', dash='dash', width=2)
                        ))
                    
                    fig.update_layout(
                        title=f"Weekly Order Quantity vs Return Rate - {selected_branch}",
                        xaxis_title="Weekly Order Quantity (bales)",
                        yaxis_title="Weekly Return Rate (%)",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("🎯 Optimal Order Quantity Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Current Pattern:**")
                        st.metric("Avg Weekly Order", f"{active_weeks['order_quantity'].mean():.0f} bales")
                        st.metric("Avg Return Rate", f"{active_weeks['return_pct'].mean():.1f}%")
                    
                    with col2:
                        st.write("**Optimal Pattern:**")
                        st.metric("Recommended Order", f"{optimal_qty:.0f} bales")
                        st.metric("Expected Return Rate", f"{optimal_return_rate:.1f}%")
                    
                    with col3:
                        st.write("**Improvement:**")
                        current_avg_return = active_weeks['return_pct'].mean()
                        improvement = current_avg_return - optimal_return_rate
                        improvement_pct = (improvement / current_avg_return * 100) if current_avg_return > 0 else 0
                        st.metric("Return Reduction", f"{improvement:.1f}%")
                        st.metric("Improvement %", f"{improvement_pct:.1f}%")
                    
                    st.write(f"**Best Quartile:** {best_quartile}")

elif page == "💡 Optimal Order Recommendations":
    st.header("💡 Optimal Order Recommendations for Each Store")
    
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
            st.subheader("🏪 Select Outlet")
            selected_outlet = st.selectbox("Choose an outlet:", outlet_names, key="rec_outlet")
            
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
            
            st.info(f"📍 Generating recommendations for **{selected_outlet}** - {len(outlet_branches)} branches")
            
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            recommendations = []
            
            for branch in outlet_branches:
                branch_row = df[df['Branch'] == branch]
                if len(branch_row) > 0:
                    weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                    
                
                    if weekly_data:
                        active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
                        
                        if active_weeks:
                            current_avg_qty = np.mean([w['order_quantity'] for w in active_weeks])
                            current_avg_return = np.mean([w['return_pct'] for w in active_weeks])
                            
                            optimal_qty, optimal_return_rate, corr, best_quartile, confidence = find_optimal_quantity(weekly_data)
                            
                            if optimal_qty:
                                qty_change_pct = ((optimal_qty - current_avg_qty) / current_avg_qty * 100)
                                expected_improvement = current_avg_return - optimal_return_rate
                                
                                if current_avg_return > 25:
                                    status = "🔴 CRITICAL"
                                    priority = 1
                                elif current_avg_return > 20:
                                    status = "🔴 HIGH"
                                    priority = 2
                                elif current_avg_return > 15:
                                    status = "🟡 MODERATE"
                                    priority = 3
                                else:
                                    status = "🟢 GOOD"
                                    priority = 4
                                
                                recommendations.append({
                                    'Branch': branch,
                                    'Current Qty': current_avg_qty,
                                    'Current Return %': current_avg_return,
                                    'Recommended Qty': optimal_qty,
                                    'Expected Return %': optimal_return_rate,
                                    'Qty Change %': qty_change_pct,
                                    'Expected Improvement': expected_improvement,
                                    'Confidence': confidence,
                                    'Status': status,
                                    'Priority': priority,
                                    'Correlation': corr,
                                    'Best Quartile': best_quartile
                                })
            
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                rec_df = rec_df.sort_values('Priority')
                
                st.subheader("📊 Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Branches", len(rec_df))
                col2.metric("Avg Current Qty", f"{rec_df['Current Qty'].mean():.0f} bales")
                col3.metric("Avg Recommended Qty", f"{rec_df['Recommended Qty'].mean():.0f} bales")
                col4.metric("Avg Current Return %", f"{rec_df['Current Return %'].mean():.1f}%")
                col5.metric("Avg Expected Return %", f"{rec_df['Expected Return %'].mean():.1f}%")
                
                st.subheader("🎯 Recommendations by Priority")
                
                critical = rec_df[rec_df['Priority'] <= 2]
                if len(critical) > 0:
                    st.write("### 🔴 Critical & High Priority Branches")
                    for idx, row in critical.iterrows():
                        with st.expander(f"{row['Status']} {row['Branch']} | Current: {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}% returns)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Current Pattern:**")
                                st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Current Return %']:.1f}%")
                            
                            with col2:
                                st.write("**Recommended Pattern:**")
                                st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Expected Return %']:.1f}%")
                            
                            with col3:
                                st.write("**Impact:**")
                                if row['Qty Change %'] < 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", delta="Reduce")
                                elif row['Qty Change %'] > 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:+.1f}%", delta="Increase")
                                else:
                                    st.metric("Qty Change", "0%", delta="Maintain")
                                st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%")
                            
                            st.write("---")
                            st.write(f"**Confidence:** {row['Confidence']*100:.0f}%")
                            st.write(f"**Correlation (Qty vs Returns):** {row['Correlation']:.3f}")
                            st.write(f"**Best Quartile:** {row['Best Quartile']}")
                
                moderate = rec_df[rec_df['Priority'] == 3]
                if len(moderate) > 0:
                    st.write("### 🟡 Moderate Priority Branches")
                    for idx, row in moderate.iterrows():
                        with st.expander(f"{row['Status']} {row['Branch']} | Current: {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}% returns)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Current Pattern:**")
                                st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Current Return %']:.1f}%")
                            
                            with col2:
                                st.write("**Recommended Pattern:**")
                                st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Expected Return %']:.1f}%")
                            
                            with col3:
                                st.write("**Impact:**")
                                if row['Qty Change %'] < 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", delta="Reduce")
                                elif row['Qty Change %'] > 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:+.1f}%", delta="Increase")
                                else:
                                    st.metric("Qty Change", "0%", delta="Maintain")
                                st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%")
                            
                            st.write("---")
                            st.write(f"**Confidence:** {row['Confidence']*100:.0f}%")
                
                good = rec_df[rec_df['Priority'] >= 4]
                if len(good) > 0:
                    st.write("### 🟢 Good Performing Branches")
                    for idx, row in good.iterrows():
                        with st.expander(f"{row['Status']} {row['Branch']} | Current: {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}% returns)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Current Pattern:**")
                                st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Current Return %']:.1f}%")
                            
                            with col2:
                                st.write("**Recommended Pattern:**")
                                st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Expected Return %']:.1f}%")
                            
                            with col3:
                                st.write("**Impact:**")
                                if row['Qty Change %'] < 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", delta="Reduce")
                                elif row['Qty Change %'] > 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:+.1f}%", delta="Increase")
                                else:
                                    st.metric("Qty Change", "0%", delta="Maintain")
                                st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%")
                
                st.subheader("📈 Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Current Qty'],
                        name='Current Weekly Order',
                        marker_color='lightblue'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Recommended Qty'],
                        name='Recommended Weekly Order',
                        marker_color='darkblue'
                    ))
                    
                    fig.update_layout(
                        title=f"Current vs Recommended Weekly Order Quantities - {selected_outlet}",
                        xaxis_title="Branch",
                        yaxis_title="Order Quantity (bales)",
                        barmode='group',
                        height=500,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig2 = go.Figure()
                    
                    fig2.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Current Return %'],
                        name='Current Return Rate',
                        marker_color='red'
                    ))
                    
                    fig2.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Expected Return %'],
                        name='Expected Return Rate',
                        marker_color='green'
                    ))
                    
                    fig2.update_layout(
                        title=f"Return Rate: Current vs Expected - {selected_outlet}",
                        xaxis_title="Branch",
                        yaxis_title="Return Rate (%)",
                        barmode='group',
                        height=500,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
                
                st.subheader("📋 Export Recommendations")
                
                export_df = rec_df[[
                    'Branch', 'Current Qty', 'Recommended Qty', 'Qty Change %',
                    'Current Return %', 'Expected Return %', 'Expected Improvement',
                    'Confidence', 'Status'
                ]].copy()
                
                export_df.columns = [
                    'Branch', 'Current Weekly Qty (bales)', 'Recommended Weekly Qty (bales)', 'Change %',
                    'Current Return Rate %', 'Expected Return Rate %', 'Expected Improvement %',
                    'Confidence', 'Status'
                ]
                
                export_df['Current Weekly Qty (bales)'] = export_df['Current Weekly Qty (bales)'].apply(lambda x: f"{x:.0f}")
                export_df['Recommended Weekly Qty (bales)'] = export_df['Recommended Weekly Qty (bales)'].apply(lambda x: f"{x:.0f}")
                export_df['Change %'] = export_df['Change %'].apply(lambda x: f"{x:.1f}%")
                export_df['Current Return Rate %'] = export_df['Current Return Rate %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Return Rate %'] = export_df['Expected Return Rate %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Improvement %'] = export_df['Expected Improvement %'].apply(lambda x: f"{x:.1f}%")
                export_df['Confidence'] = export_df['Confidence'].apply(lambda x: f"{x*100:.0f}%")
                
                st.dataframe(export_df, use_container_width=True)
                
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Recommendations as CSV",
                    data=csv,
                    file_name=f"optimal_weekly_orders_{selected_outlet}.csv",
                    mime="text/csv"
                )

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v31.0\n\nAll tabs functional!")
