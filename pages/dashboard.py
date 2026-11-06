import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def get_status_color(status):
    """Return color for status badge"""
    colors = {
        "CRITICAL": "#dc3545",
        "HIGH": "#fd7e14",
        "MODERATE": "#ffc107",
        "WATCH": "#ffc107",
        "GOOD": "#28a745",
        "DELISTED": "#6c757d"
    }
    return colors.get(status, "#6c757d")

def get_status_for_return_rate(return_rate):
    """Determine status based on return rate"""
    if return_rate is None or pd.isna(return_rate):
        return "DELISTED"
    if return_rate > 30:
        return "HIGH"
    elif return_rate > 20:
        return "MODERATE"
    elif return_rate > 15:
        return "WATCH"
    else:
        return "GOOD"

def show():
    # Check if data is loaded
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Filter for October data only (Weeks 41-44)
    october_weeks = [41, 42, 43, 44]
    df = df[df['Week'].isin(october_weeks)].copy()
    
    if len(df) == 0:
        st.error("No October data found in dataset")
        return
    
    # Extract valid branches
    all_names = df['Branch'].dropna().unique()
    valid_branches = [
        name for name in all_names 
        if isinstance(name, str) and len(name) > 0
    ]
    
    if not valid_branches:
        st.error("No valid branches found in October data")
        return
    
    # Extract outlet names (major outlets like MAJID, CHANDARANA, etc.)
    outlet_names = sorted(set([
        b.split('-')[0].strip() for b in valid_branches 
        if '-' in b
    ]))
    
    if not outlet_names:
        st.error("No outlets found")
        return
    
    # Outlet selector
    st.subheader("Select Outlet")
    selected_outlet = st.selectbox(
        "Choose an outlet to analyze:",
        outlet_names,
        label_visibility="collapsed"
    )
    
    # Get branches for selected outlet
    outlet_branches = [
        b for b in valid_branches 
        if b.split('-')[0].strip() == selected_outlet
    ]
    
    if not outlet_branches:
        st.error(f"No branches found for {selected_outlet}")
        return
    
    # Calculate metrics for all branches (October data aggregated)
    branch_metrics = []
    
    for branch in outlet_branches:
        branch_data = df[df['Branch'] == branch]
        
        if len(branch_data) == 0:
            continue
        
        # Aggregate across October weeks
        total_gross = branch_data['Gross Sales'].sum()
        total_returns = branch_data['Returns'].sum()
        total_net = branch_data['Net Sales'].sum()
        
        if total_gross == 0:
            continue
        
        # Calculate overall return rate
        overall_return_rate = (total_returns / total_gross * 100)
        
        # Get status
        status = get_status_for_return_rate(overall_return_rate)
        
        # Get trend (compare early October vs late October)
        weeks = sorted(branch_data['Week'].unique())
        if len(weeks) > 2:
            mid = len(weeks) // 2
            early = branch_data[branch_data['Week'].isin(weeks[:mid])]['Return Rate'].mean()
            late = branch_data[branch_data['Week'].isin(weeks[mid:])]['Return Rate'].mean()
            
            if late < early - 2:
                trend = "Improving"
            elif late > early + 2:
                trend = "Worsening"
            else:
                trend = "Stable"
        else:
            trend = "Stable"
        
        branch_metrics.append({
            'Branch': branch,
            'Gross Sales': total_gross,
            'Returns': total_returns,
            'Net Sales': total_net,
            'Return Rate': overall_return_rate,
            'Status': status,
            'Trend': trend,
            'Weeks': len(weeks)
        })
    
    if not branch_metrics:
        st.info("No data available for selected outlet in October")
        return
    
    # Create metrics dataframe
    metrics_df = pd.DataFrame(branch_metrics)
    
    # Display overview metrics
    st.subheader("October Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Branches", len(metrics_df))
    
    with col2:
        avg_return = metrics_df['Return Rate'].mean()
        st.metric("Average Return Rate", f"{avg_return:.1f}%")
    
    with col3:
        critical_count = len(metrics_df[metrics_df['Status'].isin(['CRITICAL', 'HIGH'])])
        st.metric("High Risk Branches", critical_count)
    
    with col4:
        improving_count = len(metrics_df[metrics_df['Trend'] == 'Improving'])
        st.metric("Improving", improving_count)
    
    # Branch Performance Chart
    st.subheader("October Return Rate by Branch")
    st.caption("Sorted by return rate (highest to lowest)")
    
    sorted_df = metrics_df.sort_values('Return Rate', ascending=False)
    colors = [get_status_color(status) for status in sorted_df['Status']]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sorted_df['Branch'],
        y=sorted_df['Return Rate'],
        marker=dict(color=colors, line=dict(color='#2c3e50', width=1)),
        text=sorted_df['Return Rate'].apply(lambda x: f"{x:.1f}%"),
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Return Rate: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="October Return Rate Analysis",
        height=500,
        xaxis_tickangle=-45,
        showlegend=False,
        font=dict(size=11),
        yaxis_title="Return Rate (%)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend Analysis
    st.subheader("October Trends")
    st.caption("Comparison of early October (Weeks 41-42) vs late October (Weeks 43-44)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        improving = len(metrics_df[metrics_df['Trend'] == 'Improving'])
        st.metric("Improving", improving)
        st.caption("Return rates decreasing")
    
    with col2:
        stable = len(metrics_df[metrics_df['Trend'] == 'Stable'])
        st.metric("Stable", stable)
        st.caption("Return rates unchanged")
    
    with col3:
        worsening = len(metrics_df[metrics_df['Trend'] == 'Worsening'])
        st.metric("Worsening", worsening)
        st.caption("Return rates increasing")
    
    # Status Legend
    st.subheader("Status Classification")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("<span style='color: #dc3545; font-weight: bold;'>CRITICAL</span><br>Return rate > 30%", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<span style='color: #fd7e14; font-weight: bold;'>HIGH</span><br>Return rate 20-30%", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<span style='color: #ffc107; font-weight: bold;'>MODERATE</span><br>Return rate 15-20%", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<span style='color: #ffc107; font-weight: bold;'>WATCH</span><br>Return rate 10-15%", unsafe_allow_html=True)
    
    with col5:
        st.markdown("<span style='color: #28a745; font-weight: bold;'>GOOD</span><br>Return rate < 10%", unsafe_allow_html=True)
    
    # Detailed Data Table
    with st.expander("View Detailed Branch Data"):
        display_df = metrics_df.copy()
        display_df['Branch Name'] = display_df['Branch'].apply(lambda x: x.split('-')[-1].strip() if '-' in x else x)
        
        final_df = display_df[['Branch Name', 'Gross Sales', 'Returns', 'Return Rate', 'Trend', 'Status', 'Weeks']].copy()
        final_df['Gross Sales'] = final_df['Gross Sales'].apply(lambda x: f"{int(x):,}")
        final_df['Returns'] = final_df['Returns'].apply(lambda x: f"{int(x):,}")
        final_df['Return Rate'] = final_df['Return Rate'].apply(lambda x: f"{x:.1f}%")
        final_df = final_df.sort_values('Return Rate', ascending=False)
        
        st.dataframe(final_df, use_container_width=True, hide_index=True)
