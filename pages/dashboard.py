import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_volatility, get_sales_volume_category, extract_outlet_name, calculate_quarter_trend
from utils import calculate_monthly_metrics, get_active_periods

def show():
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
                        fig.add_trace(go.Bar(x=active_only['Branch'], y=active_only['M7 Return Rate'], marker=dict(color=active_only['M7 Return Rate'], colorscale='RdYlGn_r')))
                        fig.update_layout(title="Return Rate by Branch", height=450, xaxis_tickangle=-45, showlegend=False, font=dict(size=11))
                        st.plotly_chart(fig, use_container_width=True)
                with col2:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    if len(active_only) > 0:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=active_only['M7 Return Rate'], y=active_only['Volatility'], mode='markers', marker=dict(size=10, color=active_only['M7 Return Rate'], colorscale='RdYlGn_r'), text=active_only['Branch']))
                        fig.update_layout(title="Return Rate vs Volatility", xaxis_title="Return Rate (%)", yaxis_title="Volatility (%)", height=450, showlegend=False, font=dict(size=11))
                        st.plotly_chart(fig, use_container_width=True)
