import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_weekly_metrics, find_optimal_quantity, extract_outlet_name

def show():
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
                    fig.add_trace(go.Scatter(x=weekly_df['order_quantity'], y=weekly_df['return_pct'], mode='markers', marker=dict(size=8, color=weekly_df['return_pct'], colorscale='RdYlGn_r')))
                    if len(active_weeks) > 1:
                        z = np.polyfit(active_weeks['order_quantity'], active_weeks['return_pct'], 1)
                        p = np.poly1d(z)
                        x_trend = np.linspace(active_weeks['order_quantity'].min(), active_weeks['order_quantity'].max(), 100)
                        fig.add_trace(go.Scatter(x=x_trend, y=p(x_trend), mode='lines', name='Trend', line=dict(color='#e74c3c', dash='dash')))
                    fig.update_layout(title="Order Quantity vs Return Rate", xaxis_title="Order Qty (bales)", yaxis_title="Return Rate (%)", height=450, showlegend=False, font=dict(size=11))
                    st.plotly_chart(fig, use_container_width=True)
                    st.subheader("Optimal Pattern")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Current Avg", f"{active_weeks['order_quantity'].mean():.0f} bales")
                        st.metric("Current Return %", f"{active_weeks['return_pct'].mean():.1f}%")
                    with col2:
                        st.metric("Recommended", f"{optimal_qty:.0f} bales")
                        st.metric("Expected Return %", f"{optimal_return_rate:.1f}%")
