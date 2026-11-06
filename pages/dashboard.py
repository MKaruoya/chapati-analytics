import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import calculate_monthly_metrics, extract_outlet_name

def show():
    st.header("Branch Performance Dashboard")
    st.caption("October Analytics - Return Rate Analysis")
    
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Get all valid branches
    all_names = df['Branch'].dropna().unique()
    branches = [
        name for name in all_names 
        if isinstance(name, str) and len(name) > 0
    ]
    
    if not branches:
        st.error("No valid branches found")
        return
    
    st.subheader("Select Outlet")
    selected_branch = st.selectbox(
        "Choose a branch:",
        sorted(branches),
        label_visibility="collapsed"
    )
    
    branch_row = df[df['Branch'] == selected_branch]
    
    if len(branch_row) == 0:
        st.error("Branch data not found")
        return
    
    # Get numeric columns
    numeric_cols = [
        col for col in df.columns[1:] 
        if df[col].dtype in ['int64', 'float64']
    ]
    
    if not numeric_cols:
        st.error("No numeric columns found")
        return
    
    # Calculate metrics
    monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
    monthly_df = pd.DataFrame(monthly_data)
    monthly_df = monthly_df[monthly_df['has_data'] == True]
    
    if len(monthly_df) == 0:
        st.info("No data available for selected outlet")
        return
    
    # Extract branch name
    outlet_name = extract_outlet_name(selected_branch)
    
    st.subheader(f"{outlet_name}")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_sales = monthly_df['sales'].sum()
    total_returns = monthly_df['returns'].sum()
    avg_return_rate = monthly_df['return_rate'].mean()
    months_active = len(monthly_df)
    
    with col1:
        st.metric("Total Sales", f"{total_sales:.0f}")
    
    with col2:
        st.metric("Total Returns", f"{total_returns:.0f}")
    
    with col3:
        st.metric("Avg Return Rate", f"{avg_return_rate:.1f}%")
    
    with col4:
        st.metric("Active Months", months_active)
    
    # Return Rate Trend
    st.subheader("Return Rate Trend")
    
    month_labels = [f"M{int(m)}" for m in monthly_df['month_num']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=month_labels,
        y=monthly_df['return_rate'],
        mode='lines+markers',
        name='Return Rate',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title="Monthly Return Rate",
        xaxis_title="Month",
        yaxis_title="Return Rate (%)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sales vs Returns
    st.subheader("Sales and Returns Comparison")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=month_labels,
        y=monthly_df['sales'],
        name='Sales',
        marker_color='#3498db'
    ))
    
    fig2.add_trace(go.Bar(
        x=month_labels,
        y=monthly_df['returns'],
        name='Returns',
        marker_color='#e74c3c'
    ))
    
    fig2.update_layout(
        title="Monthly Sales and Returns",
        xaxis_title="Month",
        yaxis_title="Volume",
        barmode='group',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Detailed Table
    st.subheader("Detailed Monthly Data")
    
    display_df = monthly_df.copy()
    display_df['Month'] = display_df['month_num'].apply(lambda x: f"M{int(x)}")
    display_df['Sales'] = display_df['sales'].apply(lambda x: f"{x:.0f}")
    display_df['Returns'] = display_df['returns'].apply(lambda x: f"{x:.0f}")
    display_df['Return Rate'] = display_df['return_rate'].apply(lambda x: f"{x:.1f}%")
    
    final_display = display_df[['Month', 'Sales', 'Returns', 'Return Rate']]
    st.dataframe(final_display, use_container_width=True, hide_index=True)
