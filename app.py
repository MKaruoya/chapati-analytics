import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_monthly_metrics, get_active_periods

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

MAJOR_OUTLETS = ['Majid', 'quickmart', 'Naivas', 'Magunas', 'cleanshelf', 'powerstar', 'chandarana']

st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📊 Dashboard (Major Outlets Only)",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

def is_major_outlet(branch_name):
    """Check if branch belongs to a major outlet"""
    if not isinstance(branch_name, str):
        return False
    branch_lower = branch_name.lower()
    return any(outlet.lower() in branch_lower for outlet in MAJOR_OUTLETS)

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
            st.write(f"Go to **Dashboard (Major Outlets Only)** to compare: {', '.join(MAJOR_OUTLETS)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif page == "📊 Dashboard (Major Outlets Only)":
    st.header(f"🏪 Major Outlets Performance Dashboard")
    st.info(f"📊 Analyzing: {', '.join(MAJOR_OUTLETS)}")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper() and is_major_outlet(name)]
        
        st.write(f"Found {len(branches)} branches from major outlets")
        
        if len(branches) == 0:
            st.error("❌ No branches found from major outlets!")
            st.write("Available branches:")
            for name in sorted(all_names):
                if isinstance(name, str) and '-' in name:
                    st.write(f"  • {name}")
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
                        
                        worsening = m6_m7_change is not None and m6_m7_change > 5
                        high_volatility = volatility > 10
                        
                        branch_metrics.append({
                            'Branch': branch,
                            'Active Status': active_status,
                            'Period': period_info,
                            'M7 Return Rate': m7_return_rate,
                            'M7 Sales': m7_sales if is_active_m7 else None,
                            'M6→M7 Trend': m6_m7_trend,
                            'M6→M7 Change': m6_m7_change,
                            'Overall Trend': overall_trend,
                            'Total Sales': total_sales,
                            'Total Returns': total_returns,
                            'Volume Category': volume_category,
                            'Volatility': volatility,
                            'High Volatility': high_volatility,
                            'Status': status,
                            'Priority': priority,
                            'Worsening': worsening
                        })
            
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                
                st.subheader("📊 Summary - Major Outlets")
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
                    display_active = active_df[['Branch', 'M7 Return Rate', 'Volume Category', 'Volatility', 'M6→M7 Trend', 'Overall Trend', 'Status']].copy()
                    display_active['M7 Return Rate'] = display_active['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_active['Volatility'] = display_active['Volatility'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_active, use_container_width=True)
                
                st.subheader("🔴 Critical Branches")
                critical_df = metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')].sort_values('Priority')
                if len(critical_df) > 0:
                    display_critical = critical_df[['Branch', 'M7 Return Rate', 'Volume Category', 'M6→M7 Trend', 'Status']].copy()
                    display_critical['M7 Return Rate'] = display_critical['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(display_critical, use_container_width=True)
                
                st.subheader("📊 Visualizations")
                col1, col2 = st.columns(2)
                
                with col1:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=active_only['Branch'], y=active_only['M7 Return Rate'], marker=dict(color=active_only['M7 Return Rate'], colorscale='RdYlGn_r')))
                    fig.update_layout(title="Month 7 Return Rate - Major Outlets", height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=active_only['M7 Return Rate'], y=active_only['Volatility'], mode='markers', marker=dict(size=12, color=active_only['M7 Return Rate'], colorscale='RdYlGn_r'), text=active_only['Branch'], hovertemplate='<b>%{text}</b><br>Return Rate: %{x:.1f}%<br>Volatility: %{y:.1f}%<extra></extra>'))
                    fig.update_layout(title="Return Rate vs Volatility", xaxis_title="Return Rate (%)", yaxis_title="Volatility (%)", height=400)
                    st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("🔍 Peer Comparison")
                active_only = metrics_df[metrics_df['Active Status'] == 'Active'].copy()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Best Performers:**")
                    top = active_only.nsmallest(3, 'M7 Return Rate')
                    for idx, row in top.iterrows():
                        st.write(f"  🟢 {row['Branch']}: {row['M7 Return Rate']:.1f}%")
                
                with col2:
                    st.write("**Worst Performers:**")
                    bottom = active_only.nlargest(3, 'M7 Return Rate')
                    for idx, row in bottom.iterrows():
                        st.write(f"  🔴 {row['Branch']}: {row['M7 Return Rate']:.1f}%")

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
    st.header("AI: Relationship Analysis")
    st.info("📊 Coming soon...")

elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Recommendations")
    st.info("💡 Coming soon...")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v20.0\n\nMajor Outlets Only!")
