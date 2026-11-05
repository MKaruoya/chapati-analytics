import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_volatility, get_sales_volume_category, extract_outlet_name, calculate_quarter_trend
from utils import calculate_monthly_metrics, get_active_periods

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

def get_trend(overall_trend):
    """Convert trend value to readable string"""
    if overall_trend is None:
        return "Stable"
    if isinstance(overall_trend, float) and np.isnan(overall_trend):
        return "Stable"
    if pd.isna(overall_trend):
        return "Stable"
    
    overall_trend_str = str(overall_trend).strip()
    if overall_trend_str == "N/A" or overall_trend_str == "nan":
        return "Stable"
    if "Improving" in overall_trend_str:
        return "Improving"
    elif "Worsening" in overall_trend_str:
        return "Worsening"
    else:
        return "Stable"

def get_action(status, trend):
    """Get recommended action based on status and trend"""
    if status == "CRITICAL":
        return "Urgent - Negative sales, stop orders"
    elif status == "HIGH":
        return "Urgent - Review order quantities" if trend == "Worsening" else "Monitor closely"
    elif status == "MODERATE":
        return "Investigate - Returns increasing" if trend == "Worsening" else "Monitor"
    elif status == "WATCH":
        return "Review order pattern" if trend == "Worsening" else "Monitor"
    else:  # GOOD
        return "Maintain current pattern" if trend == "Improving" else "Monitor"

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
    st.header("Dashboard - October Analytics")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first from the 'Upload Data' page")
        return
    
    df = st.session_state.data.copy()
    
    # Extract valid branches
    all_names = df['Branch'].dropna().unique()
    valid_branches = [
        name for name in all_names 
        if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()
    ]
    
    if not valid_branches:
        st.error("❌ No valid branches found in data")
        return
    
    # Extract outlet names
    outlet_names = sorted(set([
        extract_outlet_name(b) for b in valid_branches 
        if extract_outlet_name(b)
    ]))
    
    if not outlet_names:
        st.error("❌ No outlets found")
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
        if extract_outlet_name(b) == selected_outlet
    ]
    
    if not outlet_branches:
        st.error(f"❌ No branches found for {selected_outlet}")
        return
    
    # Get numeric columns
    numeric_cols = [
        col for col in df.columns[1:] 
        if df[col].dtype in ['int64', 'float64']
    ]
    
    if not numeric_cols:
        st.error("❌ No numeric columns found")
        return
    
    # Calculate metrics for all branches
    branch_metrics = []
    
    for branch in outlet_branches:
        branch_row = df[df['Branch'] == branch]
        
        if len(branch_row) == 0:
            continue
        
        # Calculate monthly data
        monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
        active_periods = get_active_periods(monthly_data)
        
        if not active_periods:
            continue
        
        # Get current month data (use last active month if M8 is empty)
        current_month = None
        for i in range(len(monthly_data) - 1, -1, -1):
            if monthly_data[i]['has_data']:
                current_month = monthly_data[i]
                break
        
        if not current_month:
            continue
        
        # Calculate metrics
        current_return_rate = current_month['return_rate']
        current_sales = current_month['sales']
        
        last_quarter_avg, quarter_change, quarter_trend = calculate_quarter_trend(monthly_data)
        
        total_sales = sum([m['sales'] for m in monthly_data])
        total_returns = sum([m['returns'] for m in monthly_data])
        volatility = calculate_volatility(monthly_data)
        volume_category = get_sales_volume_category(abs(total_sales))
        
        # Determine status
        if current_sales < 0:
            status = "CRITICAL"
            priority = 1
        else:
            status = get_status_for_return_rate(current_return_rate)
            priority = {'CRITICAL': 1, 'HIGH': 2, 'MODERATE': 3, 'WATCH': 4, 'GOOD': 5}.get(status, 6)
        
        active_status = "Active"
        
        branch_metrics.append({
            'Branch': branch,
            'Active Status': active_status,
            'Return Rate': current_return_rate,
            'Last Quarter Avg': last_quarter_avg,
            'Quarter Trend': quarter_trend,
            'Volume Category': volume_category,
            'Volatility': volatility,
            'Status': status,
            'Priority': priority,
            'Overall Trend': quarter_trend,
            'Total Sales': total_sales
        })
    
    if not branch_metrics:
        st.info("ℹ️ No data available for selected outlet")
        return
    
    # Create metrics dataframe
    metrics_df = pd.DataFrame(branch_metrics)
    
    # Display overview metrics
    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Branches", len(metrics_df))
    
    with col2:
        avg_return = metrics_df['Return Rate'].mean()
        st.metric("Avg Return Rate", f"{avg_return:.1f}%")
    
    with col3:
        critical_count = len(metrics_df[metrics_df['Status'].isin(['CRITICAL', 'HIGH'])])
        st.metric("Critical Issues", critical_count)
    
    with col4:
        improving_count = len(metrics_df[metrics_df['Overall Trend'] == 'Improving'])
        st.metric("Improving", improving_count)
    
    # Branch Performance Chart
    st.subheader("📈 Branch Performance")
    st.caption("Return Rate by Branch (Color: Red=High Risk, Orange=Moderate, Yellow=Watch, Green=Good)")
    
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
        title="Return Rate by Branch",
        height=500,
        xaxis_tickangle=-45,
        showlegend=False,
        font=dict(size=11),
        yaxis_title="Return Rate (%)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend Analysis
    st.subheader("📉 Trend Analysis")
    st.caption("Comparison of early period (M1-M3) vs recent period (M6-M8)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        improving = len(metrics_df[metrics_df['Overall Trend'] == 'Improving'])
        st.metric("Improving ↓", improving, delta=f"+{improving}")
    
    with col2:
        stable = len(metrics_df[metrics_df['Overall Trend'] == 'Stable'])
        st.metric("Stable →", stable)
    
    with col3:
        worsening = len(metrics_df[metrics_df['Overall Trend'] == 'Worsening'])
        st.metric("Worsening ↑", worsening, delta=f"-{worsening}")
    
    # Status Legend
    st.subheader("🎯 Status Legend")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("<span style='color: #dc3545; font-weight: bold;'>🔴 CRITICAL</span> - Negative sales", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<span style='color: #fd7e14; font-weight: bold;'>🟠 HIGH</span> - Return rate > 30%", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<span style='color: #ffc107; font-weight: bold;'>🟡 MODERATE</span> - Return rate 20-30%", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<span style='color: #ffc107; font-weight: bold;'>🟡 WATCH</span> - Return rate 15-20%", unsafe_allow_html=True)
    
    with col5:
        st.markdown("<span style='color: #28a745; font-weight: bold;'>🟢 GOOD</span> - Return rate < 15%", unsafe_allow_html=True)
    
    # Detailed Data Table
    with st.expander("📋 View All Branches - Detailed Data"):
        display_df = metrics_df.copy()
        display_df['Trend'] = display_df['Overall Trend'].apply(get_trend)
        display_df['Action'] = display_df.apply(lambda row: get_action(row['Status'], row['Trend']), axis=1)
        display_df['Branch Name'] = display_df['Branch'].apply(lambda x: x.split('-')[-1].strip() if '-' in x else x)
        
        final_df = display_df[['Branch Name', 'Return Rate', 'Trend', 'Status', 'Action']].copy()
        final_df['Return Rate'] = final_df['Return Rate'].apply(lambda x: f"{x:.1f}%")
        final_df = final_df.sort_values('Status', key=lambda x: x.map({'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'WATCH': 3, 'GOOD': 4}))
        
        st.dataframe(final_df, use_container_width=True, hide_index=True)
