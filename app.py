import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_monthly_metrics, get_active_periods

st.set_page_config(page_title="Chapati Analytics", layout="wide")

st.markdown("""
<style>
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1 { font-size: 32px; font-weight: 700; color: #2c3e50; margin-bottom: 0.3rem; }
    h2 { font-size: 20px; font-weight: 600; color: #34495e; margin-top: 1.5rem; border-bottom: 3px solid #3498db; padding-bottom: 0.7rem; }
    h3 { font-size: 15px; font-weight: 600; color: #34495e; }
    .stMetric { background: linear-gradient(135deg, #ecf0f1 0%, #f8f9fa 100%); padding: 1.2rem; border-radius: 8px; border-left: 4px solid #3498db; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stDataFrame { font-size: 13px; }
    .header-box { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-box"><h1 style="color: white; margin: 0;">Chapati Analytics</h1><p style="color: #ecf0f1; margin: 0.5rem 0 0 0;">Data-driven order optimization for retail distribution</p></div>', unsafe_allow_html=True)

st.sidebar.header("Navigation")
page = st.sidebar.radio("Select", ["Upload Data", "Dashboard", "Store Analysis", "Relationship Analysis", "Order Recommendations"], label_visibility="collapsed")

if 'data' not in st.session_state:
    st.session_state.data = None

def calculate_volatility(monthly_data):
    return_rates = [m['return_rate'] for m in monthly_data if m['has_data']]
    return np.std(return_rates) if len(return_rates) > 1 else 0

def get_sales_volume_category(total_sales):
    abs_sales = abs(total_sales)
    if abs_sales > 500: return "High Volume"
    elif abs_sales > 200: return "Medium Volume"
    elif abs_sales > 50: return "Low Volume"
    else: return "Very Low Volume"

def extract_outlet_name(branch_name):
    if isinstance(branch_name, str) and '-' in branch_name:
        return branch_name.split('-')[0].strip()
    return None

def calculate_quarter_trend(monthly_data):
    active_months = [m for m in monthly_data if m['has_data']]
    if len(active_months) < 3:
        return None, None, None
    last_quarter = active_months[-3:]
    last_quarter_avg = np.mean([m['return_rate'] for m in last_quarter])
    if len(active_months) >= 6:
        prev_quarter = active_months[-6:-3]
        prev_quarter_avg = np.mean([m['return_rate'] for m in prev_quarter])
        quarter_change = last_quarter_avg - prev_quarter_avg
        trend = "Improving" if quarter_change < -2 else "Worsening" if quarter_change > 2 else "Stable"
    else:
        quarter_change = None
        trend = "N/A"
    return last_quarter_avg, quarter_change, trend

def calculate_weekly_metrics(branch_row, numeric_cols):
    weekly_data = []
    for i in range(0, len(numeric_cols) - 1, 2):
        net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
        returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
        if pd.notna(net_sales_val) or pd.notna(returns_val):
            net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
            returns_val = returns_val if pd.notna(returns_val) else 0
            original_order = abs(net_sales_val) + returns_val
            return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
            weekly_data.append({'week': len(weekly_data) + 1, 'order_quantity': original_order, 'net_sales': net_sales_val, 'returns': returns_val, 'return_pct': return_pct})
    return weekly_data

def find_optimal_quantity(weekly_data):
    active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
    if not active_weeks:
        return None, None, None, "No data", 0
    quantities = [w['order_quantity'] for w in active_weeks]
    returns = [w['return_pct'] for w in active_weeks]
    q1 = np.percentile(quantities, 25)
    q3 = np.percentile(quantities, 75)
    q1_returns = [r for q, r in zip(quantities, returns) if q <= q1]
    q2_returns = [r for q, r in zip(quantities, returns) if q1 < q <= q3]
    q3_returns = [r for q, r in zip(quantities, returns) if q > q3]
    avg_q1_return = np.mean(q1_returns) if q1_returns else 0
    avg_q2_return = np.mean(q2_returns) if q2_returns else 0
    avg_q3_return = np.mean(q3_returns) if q3_returns else 0
    quartile_returns = {'Q1': (q1, avg_q1_return), 'Q2': (np.percentile(quantities, 50), avg_q2_return), 'Q3': (q3, avg_q3_return)}
    best_quartile = min(quartile_returns.items(), key=lambda x: x[1][1])
    optimal_qty = best_quartile[1][0]
    optimal_return_rate = best_quartile[1][1]
    corr = np.corrcoef(quantities, returns)[0, 1]
    confidence = min(len(active_weeks) / 35, 1.0)
    return optimal_qty, optimal_return_rate, corr, best_quartile[0], confidence

if page == "Upload Data":
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Select CSV file", type=['csv'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            df = df.rename(columns={df.columns[0]: 'Branch'})
            st.session_state.data = df
            st.success("Data uploaded successfully")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rows", len(df))
            col2.metric("Columns", len(df.columns))
            col3.metric("Branches", df['Branch'].nunique())
            col4.metric("Weeks", (len(df.columns) - 1) // 2)
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif page == "Dashboard":
    st.header("Dashboard")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
        if not outlet_names:
            st.error("No outlets found")
        else:
            selected_outlet = st.selectbox("Select outlet", outlet_names, label_visibility="collapsed")
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            branch_metrics = []
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
                        last_quarter_avg, quarter_change, quarter_trend = calculate_quarter_trend(monthly_data)
                        first_period_start = active_periods[0][0]
                        last_period_end = active_periods[-1][-1]
                        overall_trend = "Improving" if last_period_end['return_rate'] < first_period_start['return_rate'] else "Worsening" if last_period_end['return_rate'] > first_period_start['return_rate'] else "Stable"
                        total_sales = sum([m['sales'] for m in monthly_data])
                        total_returns = sum([m['returns'] for m in monthly_data])
                        volatility = calculate_volatility(monthly_data)
                        volume_category = get_sales_volume_category(abs(total_sales))
                        if is_active_m7:
                            if m7_sales < 0:
                                status = "CRITICAL"
                                priority = 1
                            elif m7_return_rate > 30:
                                status = "HIGH"
                                priority = 2
                            elif m7_return_rate > 20:
                                status = "MODERATE"
                                priority = 3
                            elif m7_return_rate > 15:
                                status = "WATCH"
                                priority = 4
                            else:
                                status = "GOOD"
                                priority = 5
                            active_status = "Active"
                        else:
                            status = "DELISTED"
                            priority = 6
                            active_status = "Delisted"
                            m7_return_rate = last_period_end['return_rate']
                        branch_metrics.append({'Branch': branch, 'Active Status': active_status, 'M7 Return Rate': m7_return_rate, 'Last Quarter Avg': last_quarter_avg, 'Quarter Trend': quarter_trend, 'Volume Category': volume_category, 'Volatility': volatility, 'Status': status, 'Priority': priority})
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                st.subheader("Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                active_branches = len(metrics_df[metrics_df['Active Status'] == 'Active'])
                delisted_branches = len(metrics_df[metrics_df['Active Status'] == 'Delisted'])
                col1.metric("Total", len(metrics_df))
                col2.metric("Active", active_branches)
                col3.metric("Delisted", delisted_branches)
                avg_rate = metrics_df[metrics_df['Active Status'] == 'Active']['M7 Return Rate'].mean()
                col4.metric("Avg Return %", f"{avg_rate:.1f}%")
                critical_count = len(metrics_df[metrics_df['Status'].isin(['CRITICAL', 'HIGH'])])
                col5.metric("Issues", critical_count)
                st.subheader("Active Branches")
                active_df = metrics_df[metrics_df['Active Status'] == 'Active'].sort_values('Priority')
                if len(active_df) > 0:
                    display_active = active_df[['Branch', 'M7 Return Rate', 'Last Quarter Avg', 'Quarter Trend', 'Volume Category', 'Status']].copy()
                    display_active['M7 Return Rate'] = display_active['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_active['Last Quarter Avg'] = display_active['Last Quarter Avg'].apply(lambda x: f"{x:.1f}%" if x else "N/A")
                    st.dataframe(display_active, use_container_width=True, hide_index=True)
                st.subheader("Visualizations")
                col1, col2 = st.columns(2)
                with col1:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    if len(active_only) > 0:
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=active_only['Branch'], y=active_only['M7 Return Rate'], marker=dict(color=active_only['M7 Return Rate'], colorscale='RdYlGn_r', line=dict(color='#2c3e50', width=1))))
                        fig.update_layout(title="Return Rate by Branch", height=550, xaxis_tickangle=-45, showlegend=False, font=dict(size=12), title_font_size=16)
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    if len(active_only) > 0:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=active_only['M7 Return Rate'], y=active_only['Volatility'], mode='markers', marker=dict(size=14, color=active_only['M7 Return Rate'], colorscale='RdYlGn_r', line=dict(color='#2c3e50', width=2)), text=active_only['Branch']))
                        fig.update_layout(title="Return Rate vs Volatility", xaxis_title="Return Rate (%)", yaxis_title="Volatility (%)", height=550, showlegend=False, font=dict(size=12), title_font_size=16)
                        st.plotly_chart(fig, use_container_width=True)

elif page == "Store Analysis":
    st.header("Store Analysis")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        if branches:
            selected_branch = st.selectbox("Select branch", sorted(branches), label_visibility="collapsed")
            branch_row = df[df['Branch'] == selected_branch]
            if len(branch_row) > 0:
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
                        weekly_data.append({'Week': f"W{week_num}", 'Net Sales': f"{net_sales_val:.0f}", 'Returns': f"{returns_val:.0f}", 'Return %': f"{return_pct:.1f}%", 'net_sales_numeric': net_sales_val, 'returns_numeric': returns_val, 'return_pct_numeric': return_pct})
                    week_num += 1
                if weekly_data:
                    st.subheader("Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    st.dataframe(weekly_df[['Week', 'Net Sales', 'Returns', 'Return %']], use_container_width=True, hide_index=True)
                    st.subheader("Monthly Performance")
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
                            monthly_data.append({'Month': f"M{month_num}", 'Net Sales': f"{month_sales:.0f}", 'Returns': f"{month_returns:.0f}", 'Return %': f"{month_return_pct:.1f}%", 'net_sales_numeric': month_sales, 'returns_numeric': month_returns, 'return_pct_numeric': month_return_pct})
                    if monthly_data:
                        monthly_df = pd.DataFrame(monthly_data)
                        st.dataframe(monthly_df[['Month', 'Net Sales', 'Returns', 'Return %']], use_container_width=True, hide_index=True)
                        st.subheader("Trend")
                        monthly_df_plot = monthly_df.copy()
                        monthly_df_plot['Net Sales'] = pd.to_numeric(monthly_df_plot['net_sales_numeric'])
                        monthly_df_plot['Returns'] = pd.to_numeric(monthly_df_plot['returns_numeric'])
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Net Sales'], name='Net Sales', marker_color='#27ae60', marker_line=dict(color='#1e8449', width=1)))
                        fig.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Returns'], name='Returns', marker_color='#e74c3c', marker_line=dict(color='#c0392b', width=1)))
                        fig.update_layout(title="Monthly Net Sales vs Returns", barmode='group', height=550, showlegend=True, font=dict(size=12), title_font_size=16)
                        st.plotly_chart(fig, use_container_width=True)

elif page == "Relationship Analysis":
    st.header("Relationship Analysis")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        if valid_branches:
            selected_branch = st.selectbox("Select branch", sorted(valid_branches), label_visibility="collapsed")
            branch_row = df[df['Branch'] == selected_branch]
            if len(branch_row) > 0:
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                if weekly_data:
                    weekly_df = pd.DataFrame(weekly_data)
                    active_weeks = weekly_df[weekly_df['order_quantity'] > 0]
                    optimal_qty, optimal_return_rate, corr, best_quartile, confidence = find_optimal_quantity(weekly_data)
                    st.subheader("Analysis")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Correlation", f"{corr:.3f}")
                    col2.metric("Avg Weekly Order", f"{active_weeks['order_quantity'].mean():.0f} bales")
                    col3.metric("Avg Return Rate", f"{active_weeks['return_pct'].mean():.1f}%")
                    st.subheader("Scatter Plot")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=weekly_df['order_quantity'], y=weekly_df['return_pct'], mode='markers', marker=dict(size=10, color=weekly_df['return_pct'], colorscale='RdYlGn_r', line=dict(color='#2c3e50', width=1))))
                    if len(active_weeks) > 1:
                        z = np.polyfit(active_weeks['order_quantity'], active_weeks['return_pct'], 1)
                        p = np.poly1d(z)
                        x_trend = np.linspace(active_weeks['order_quantity'].min(), active_weeks['order_quantity'].max(), 100)
                        fig.add_trace(go.Scatter(x=x_trend, y=p(x_trend), mode='lines', name='Trend', line=dict(color='#e74c3c', dash='dash', width=3)))
                    fig.update_layout(title="Order Quantity vs Return Rate", xaxis_title="Order Qty (bales)", yaxis_title="Return Rate (%)", height=550, showlegend=False, font=dict(size=12), title_font_size=16)
                    st.plotly_chart(fig, use_container_width=True)
                    st.subheader("Optimal Pattern")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Avg", f"{active_weeks['order_quantity'].mean():.0f} bales")
                        st.metric("Current Return %", f"{active_weeks['return_pct'].mean():.1f}%")
                    with col2:
                        st.metric("Recommended", f"{optimal_qty:.0f} bales")
                        st.metric("Expected Return %", f"{optimal_return_rate:.1f}%")

elif page == "Order Recommendations":
    st.header("Order Recommendations")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
        if not outlet_names:
            st.error("No outlets found")
        else:
            selected_outlet = st.selectbox("Select outlet", outlet_names, label_visibility="collapsed")
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
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
                                    status = "CRITICAL"
                                    priority = 1
                                elif current_avg_return > 20:
                                    status = "HIGH"
                                    priority = 2
                                elif current_avg_return > 15:
                                    status = "MODERATE"
                                    priority = 3
                                else:
                                    status = "GOOD"
                                    priority = 4
                                recommendations.append({'Branch': branch, 'Current Qty': current_avg_qty, 'Current Return %': current_avg_return, 'Recommended Qty': optimal_qty, 'Expected Return %': optimal_return_rate, 'Qty Change %': qty_change_pct, 'Expected Improvement': expected_improvement, 'Confidence': confidence, 'Status': status, 'Priority': priority})
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                rec_df = rec_df.sort_values('Priority')
                st.subheader("Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Branches", len(rec_df))
                col2.metric("Avg Current Qty", f"{rec_df['Current Qty'].mean():.0f} bales")
                col3.metric("Avg Recommended Qty", f"{rec_df['Recommended Qty'].mean():.0f} bales")
                col4.metric("Avg Current Return %", f"{rec_df['Current Return %'].mean():.1f}%")
                col5.metric("Avg Expected Return %", f"{rec_df['Expected Return %'].mean():.1f}%")
                st.subheader("Recommendations")
                for idx, row in rec_df.iterrows():
                    with st.expander(f"{row['Branch']} - {row['Status']} | {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}%)"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("**Current**")
                            st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales", label_visibility="collapsed")
                            st.metric("Return Rate", f"{row['Current Return %']:.1f}%", label_visibility="collapsed")
                        with col2:
                            st.markdown("**Recommended**")
                            st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales", label_visibility="collapsed")
                            st.metric("Return Rate", f"{row['Expected Return %']:.1f}%", label_visibility="collapsed")
                        with col3:
                            st.markdown("**Impact**")
                            st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", label_visibility="collapsed")
                            st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%", label_visibility="collapsed")
                        st.caption(f"Confidence: {row['Confidence']*100:.0f}%")
                st.subheader("Visualizations")
                col1, col2 = st.columns(2)
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Current Qty'], name='Current', marker_color='#95a5a6', marker_line=dict(color='#7f8c8d', width=1)))
                    fig.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Recommended Qty'], name='Recommended', marker_color='#3498db', marker_line=dict(color='#2980b9', width=1)))
                    fig.update_layout(title="Current vs Recommended", barmode='group', height=550, xaxis_tickangle=-45, showlegend=True, font=dict(size=12), title_font_size=16)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Current Return %'], name='Current', marker_color='#e74c3c', marker_line=dict(color='#c0392b', width=1)))
                    fig2.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Expected Return %'], name='Expected', marker_color='#27ae60', marker_line=dict(color='#1e8449', width=1)))
                    fig2.update_layout(title="Return Rate Comparison", barmode='group', height=550, xaxis_tickangle=-45, showlegend=True, font=dict(size=12), title_font_size=16)
                    st.plotly_chart(fig2, use_container_width=True)
                st.subheader("Export")
                export_df = rec_df[['Branch', 'Current Qty', 'Recommended Qty', 'Qty Change %', 'Current Return %', 'Expected Return %', 'Expected Improvement', 'Confidence', 'Status']].copy()
                export_df.columns = ['Branch', 'Current Qty', 'Recommended Qty', 'Change %', 'Current Return %', 'Expected Return %', 'Improvement %', 'Confidence', 'Status']
                st.dataframe(export_df, use_container_width=True, hide_index=True)

st.sidebar.markdown("---")
st.sidebar.caption("Chapati Analytics v32.0 | Colorful & Spacious")
