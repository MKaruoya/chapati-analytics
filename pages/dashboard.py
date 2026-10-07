import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_volatility, get_sales_volume_category, extract_outlet_name, calculate_quarter_trend
from utils import calculate_monthly_metrics, get_active_periods

def get_status_color(status):
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
    # Handle all types of null/missing values
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
    if status == "CRITICAL":
        return "Urgent - Negative sales, stop orders"
    elif status == "HIGH":
        if trend == "Worsening":
            return "Urgent - Review order quantities"
        else:
            return "Monitor closely"
    elif status == "MODERATE":
        if trend == "Worsening":
            return "Investigate - Returns increasing"
        else:
            return "Monitor"
    elif status == "WATCH":
        if trend == "Worsening":
            return "Review order pattern"
        else:
            return "Monitor"
    else:  # GOOD
        if trend == "Improving":
            return "Maintain current pattern"
        else:
            return "Monitor"

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
                            m7_return_rate = last_quarter_avg if last_quarter_avg else 0
                        
                        branch_metrics.append({
                            'Branch': branch,
                            'Active Status': active_status,
                            'M7 Return Rate': m7_return_rate,
                            'Last Quarter Avg': last_quarter_avg,
                            'Quarter Trend': quarter_trend,
                            'Volume Category': volume_category,
                            'Volatility': volatility,
                            'Status': status,
                            'Priority': priority,
                            'Overall Trend': quarter_trend
                        })
            
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                active_df = metrics_df[metrics_df['Active Status'] == 'Active']
                
                # Key Metrics with Tooltips
                st.subheader("Overview")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Active", len(active_df))
                    st.caption("Number of active branches")
                
                with col2:
                    st.metric("Avg Return Rate", f"{active_df['M7 Return Rate'].mean():.1f}%")
                    st.caption("Average returns across all active branches")
                
                with col3:
                    critical_count = len(metrics_df[metrics_df['Status'].isin(['CRITICAL', 'HIGH'])])
                    st.metric("Critical Issues", critical_count)
                    st.caption("Branches needing immediate attention")
                
                with col4:
                    improving_count = len(metrics_df[metrics_df['Overall Trend'] == 'Improving'])
                    st.metric("Improving", improving_count)
                    st.caption("Branches with declining return rates")
                
                # Main Visualization - Return Rate by Branch
                st.subheader("Branch Performance")
                st.caption("Color coding: Red = Critical/High | Orange = Moderate | Yellow = Watch | Green = Good")
                
                if len(active_df) > 0:
                    active_sorted = active_df.sort_values('M7 Return Rate', ascending=False)
                    colors = [get_status_color(status) for status in active_sorted['Status']]
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=active_sorted['Branch'],
                        y=active_sorted['M7 Return Rate'],
                        marker=dict(color=colors, line=dict(color='#2c3e50', width=1)),
                        text=active_sorted['M7 Return Rate'].apply(lambda x: f"{x:.1f}%"),
                        textposition='auto',
                        hovertemplate='<b>%{x}</b><br>Return Rate: %{y:.1f}%<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title="Return Rate by Branch (Month 7)",
                        height=500,
                        xaxis_tickangle=-45,
                        showlegend=False,
                        font=dict(size=12),
                        yaxis_title="Return Rate (%)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Trend Analysis with Explanations
                st.subheader("Trend Analysis")
                st.caption("Compares return rates from early period (M1-M3) to recent period (M5-M7)")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    improving = len(metrics_df[metrics_df['Overall Trend'] == 'Improving'])
                    st.metric("Improving", improving, delta=f"+{improving}")
                    st.caption("Return rate is decreasing (good)")
                
                with col2:
                    stable = len(metrics_df[metrics_df['Overall Trend'] == 'Stable'])
                    st.metric("Stable", stable)
                    st.caption("Return rate is unchanged")
                
                with col3:
                    worsening = len(metrics_df[metrics_df['Overall Trend'] == 'Worsening'])
                    st.metric("Worsening", worsening, delta=f"-{worsening}")
                    st.caption("Return rate is increasing (bad)")
                
                # Status Legend
                st.subheader("Status Legend")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.markdown("<span style='color: #dc3545; font-weight: bold;'>CRITICAL</span> - Negative sales", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<span style='color: #fd7e14; font-weight: bold;'>HIGH</span> - Return rate > 30%", unsafe_allow_html=True)
                
                with col3:
                    st.markdown("<span style='color: #ffc107; font-weight: bold;'>MODERATE</span> - Return rate 20-30%", unsafe_allow_html=True)
                
                with col4:
                    st.markdown("<span style='color: #ffc107; font-weight: bold;'>WATCH</span> - Return rate 15-20%", unsafe_allow_html=True)
                
                with col5:
                    st.markdown("<span style='color: #28a745; font-weight: bold;'>GOOD</span> - Return rate < 15%", unsafe_allow_html=True)
                
                # Simplified Detailed Table
                with st.expander("View All Branches - Detailed Data"):
                    display_df = active_df.copy()
                    display_df['Trend'] = display_df['Overall Trend'].apply(get_trend)
                    display_df['Action'] = display_df.apply(lambda row: get_action(row['Status'], row['Trend']), axis=1)
                    
                    # Extract branch name (remove outlet prefix)
                    display_df['Branch Name'] = display_df['Branch'].apply(lambda x: x.split('-')[-1].strip() if '-' in x else x)
                    
                    final_df = display_df[['Branch Name', 'M7 Return Rate', 'Trend', 'Status', 'Action']].copy()
                    final_df['M7 Return Rate'] = final_df['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    final_df = final_df.sort_values('Status', key=lambda x: x.map({'CRITICAL': 0, 'HIGH': 1, 'MODERATE': 2, 'WATCH': 3, 'GOOD': 4}))
                    
                    st.dataframe(final_df, use_container_width=True, hide_index=True)
