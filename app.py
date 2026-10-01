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
                    st.info("💡 **Last Quarter Avg:** Average return rate for last 3 months | **Quarter Trend:** Comparing last 3 months to previous 3 months")
                else:
                    st.info("No active branches in Month 7")
                
                st.subheading("🔴 Critical Branches")
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
    st.header("🤖 AI Relationship Analysis")
    
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
            branch_data = []
            
            for branch in outlet_branches:
                branch_row = df[df['Branch'] == branch]
                if len(branch_row) > 0:
                    monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
                    active_periods = get_active_periods(monthly_data)
                    
                    if active_periods:
                        month_7 = monthly_data[6]
                        is_active_m7 = month_7['has_data']
                        
                        if is_active_m7:
                            m7_return_rate = month_7['return_rate']
                            m7_sales = month_7['sales']
                        else:
                            m7_return_rate = None
                            m7_sales = None
                        
                        total_sales = sum([m['sales'] for m in monthly_data])
                        total_returns = sum([m['returns'] for m in monthly_data])
                        volatility = calculate_volatility(monthly_data)
                        
                        if is_active_m7 and m7_return_rate is not None:
                            branch_data.append({
                                'Branch': branch,
                                'Return Rate': m7_return_rate,
                                'Sales Volume': abs(total_sales),
                                'Total Returns': total_returns,
                                'Volatility': volatility,
                                'M7 Sales': m7_sales
                            })
            
            if branch_data:
                analysis_df = pd.DataFrame(branch_data)
                
                st.subheader("📊 Correlation Analysis")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Return Rate vs Sales Volume**")
                    corr_sales = analysis_df['Return Rate'].corr(analysis_df['Sales Volume'])
                    st.metric("Correlation", f"{corr_sales:.3f}")
                    if corr_sales > 0.5:
                        st.warning("🔴 Strong positive: Higher sales = Higher returns")
                    elif corr_sales > 0.2:
                        st.info("🟡 Moderate positive: Some relationship")
                    elif corr_sales < -0.2:
                        st.success("🟢 Negative: Higher sales = Lower returns (good!)")
                    else:
                        st.success("🟢 Weak: Independent relationship")
                
                with col2:
                    st.write("**Return Rate vs Volatility**")
                    corr_volatility = analysis_df['Return Rate'].corr(analysis_df['Volatility'])
                    st.metric("Correlation", f"{corr_volatility:.3f}")
                    if corr_volatility > 0.5:
                        st.warning("🔴 Strong positive: Unstable = High returns")
                    elif corr_volatility > 0.2:
                        st.info("🟡 Moderate positive: Some instability")
                    else:
                        st.success("🟢 Weak: Stability independent of returns")
                
                with col3:
                    st.write("**Sales Volume vs Volatility**")
                    corr_vol_sales = analysis_df['Sales Volume'].corr(analysis_df['Volatility'])
                    st.metric("Correlation", f"{corr_vol_sales:.3f}")
                    if corr_vol_sales > 0.5:
                        st.warning("🔴 High volume = Unstable")
                    elif corr_vol_sales < -0.2:
                        st.success("🟢 High volume = Stable")
                    else:
                        st.info("🟡 No clear relationship")
                
                st.subheader("📈 Relationship Visualizations")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Sales Volume'],
                        y=analysis_df['Return Rate'],
                        mode='markers',
                        marker=dict(size=10, color=analysis_df['Return Rate'], colorscale='RdYlGn_r'),
                        text=analysis_df['Branch'],
                        hovertemplate='<b>%{text}</b><br>Sales: %{x:.0f}<br>Return Rate: %{y:.1f}%<extra></extra>'
                    ))
                    z = np.polyfit(analysis_df['Sales Volume'], analysis_df['Return Rate'], 1)
                    p = np.poly1d(z)
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Sales Volume'].sort_values(),
                        y=p(analysis_df['Sales Volume'].sort_values()),
                        mode='lines',
                        name='Trend',
                        line=dict(color='red', dash='dash')
                    ))
                    fig.update_layout(title="Return Rate vs Sales Volume", xaxis_title="Sales Volume (bales)", yaxis_title="Return Rate (%)", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Volatility'],
                        y=analysis_df['Return Rate'],
                        mode='markers',
                        marker=dict(size=10, color=analysis_df['Return Rate'], colorscale='RdYlGn_r'),
                        text=analysis_df['Branch'],
                        hovertemplate='<b>%{text}</b><br>Volatility: %{x:.1f}%<br>Return Rate: %{y:.1f}%<extra></extra>'
                    ))
                    z = np.polyfit(analysis_df['Volatility'], analysis_df['Return Rate'], 1)
                    p = np.poly1d(z)
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Volatility'].sort_values(),
                        y=p(analysis_df['Volatility'].sort_values()),
                        mode='lines',
                        name='Trend',
                        line=dict(color='red', dash='dash')
                    ))
                    fig.update_layout(title="Return Rate vs Volatility", xaxis_title="Volatility (%)", yaxis_title="Return Rate (%)", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Sales Volume'],
                        y=analysis_df['Volatility'],
                        mode='markers',
                        marker=dict(size=10, color=analysis_df['Return Rate'], colorscale='RdYlGn_r'),
                        text=analysis_df['Branch'],
                        hovertemplate='<b>%{text}</b><br>Sales: %{x:.0f}<br>Volatility: %{y:.1f}%<extra></extra>'
                    ))
                    z = np.polyfit(analysis_df['Sales Volume'], analysis_df['Volatility'], 1)
                    p = np.poly1d(z)
                    fig.add_trace(go.Scatter(
                        x=analysis_df['Sales Volume'].sort_values(),
                        y=p(analysis_df['Sales Volume'].sort_values()),
                        mode='lines',
                        name='Trend',
                        line=dict(color='red', dash='dash')
                    ))
                    fig.update_layout(title="Sales Volume vs Volatility", xaxis_title="Sales Volume (bales)", yaxis_title="Volatility (%)", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("🔍 Pattern Recognition")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Volume Categories Analysis:**")
                    analysis_df['Volume Cat'] = analysis_df['Sales Volume'].apply(get_sales_volume_category)
                    
                    for vol_cat in ['High Volume', 'Medium Volume', 'Low Volume', 'Very Low Volume']:
                        if vol_cat in analysis_df['Volume Cat'].values:
                            cat_data = analysis_df[analysis_df['Volume Cat'] == vol_cat]
                            avg_return = cat_data['Return Rate'].mean()
                            avg_volatility = cat_data['Volatility'].mean()
                            count = len(cat_data)
                            st.write(f"**{vol_cat}** ({count} branches)")
                            st.write(f"  • Avg Return Rate: {avg_return:.1f}%")
                            st.write(f"  • Avg Volatility: {avg_volatility:.1f}%")
                
                with col2:
                    st.write("**Anomalies & Outliers:**")
                    
                    mean_return = analysis_df['Return Rate'].mean()
                    std_return = analysis_df['Return Rate'].std()
                    
                    outliers = analysis_df[
                        (analysis_df['Return Rate'] > mean_return + std_return) |
                        (analysis_df['Return Rate'] < mean_return - std_return)
                    ]
                    
                    if len(outliers) > 0:
                        st.write(f"Found {len(outliers)} outlier branches:")
                        for idx, row in outliers.iterrows():
                            if row['Return Rate'] > mean_return + std_return:
                                st.write(f"  🔴 {row['Branch']}: {row['Return Rate']:.1f}% (High)")
                            else:
                                st.write(f"  🟢 {row['Branch']}: {row['Return Rate']:.1f}% (Low)")
                    else:
                        st.write("✅ No significant outliers detected")
                
                st.subheader("💡 AI Insights & Recommendations")
                
                st.write("**Key Findings:**")
                
                findings = []
                
                if corr_sales > 0.5:
                    findings.append("🔴 **High Sales = High Returns**: Larger orders lead to more returns. Possible quality or handling issues at scale.")
                elif corr_sales < -0.2:
                    findings.append("🟢 **High Sales = Low Returns**: Larger orders are handled better. These branches are efficient.")
                else:
                    findings.append("🟡 **Sales & Returns Independent**: Order size doesn't strongly affect return rate.")
                
                if corr_volatility > 0.5:
                    findings.append("🔴 **Unstable = High Returns**: Inconsistent performance correlates with high returns. Need standardization.")
                elif corr_volatility < -0.2:
                    findings.append("🟢 **Stable = Good Performance**: Consistent branches have lower returns.")
                else:
                    findings.append("🟡 **Volatility Doesn't Predict Returns**: Consistency is independent of return rate.")
                
                if corr_vol_sales > 0.5:
                    findings.append("⚠️ **High Volume = Unstable**: Larger branches are more volatile. May need better management.")
                elif corr_vol_sales < -0.2:
                    findings.append("✅ **High Volume = Stable**: Larger branches are more consistent.")
                
                for finding in findings:
                    st.write(f"• {finding}")
                
                st.write("**Recommendations:**")
                
                recommendations = []
                
                if corr_sales > 0.3:
                    recommendations.append("📉 Reduce order quantities for high-return branches")
                    recommendations.append("🔍 Investigate quality/handling issues at scale")
                
                if corr_volatility > 0.3:
                    recommendations.append("📋 Standardize processes for volatile branches")
                    recommendations.append("📊 Implement consistency monitoring")
                
                best_branch = analysis_df.loc[analysis_df['Return Rate'].idxmin()]
                recommendations.append(f"📚 Learn from {best_branch['Branch']} (Return Rate: {best_branch['Return Rate']:.1f}%)")
                
                worst_branch = analysis_df.loc[analysis_df['Return Rate'].idxmax()]
                recommendations.append(f"🆘 Focus on {worst_branch['Branch']} (Return Rate: {worst_branch['Return Rate']:.1f}%)")
                
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
                
                st.subheader("📊 Statistical Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Avg Return Rate", f"{analysis_df['Return Rate'].mean():.1f}%")
                col2.metric("Avg Volatility", f"{analysis_df['Volatility'].mean():.1f}%")
                col3.metric("Avg Sales Volume", f"{analysis_df['Sales Volume'].mean():.0f} bales")
                col4.metric("Branches Analyzed", len(analysis_df))

elif page == "💡 Optimal Order Recommendations":
    st.header("💡 Optimal Order Recommendations")
    st.info("💡 Coming soon...")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v25.0\n\nClean redraft - no unused imports!")
