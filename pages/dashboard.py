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
                            'Overall Trend': overall_trend
                        })
            
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                active_df = metrics_df[metrics_df['Active Status'] == 'Active']
                
                # Key Metrics
                st.subheader("Overview")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Active", len(active_df))
                col2.metric("Avg Return Rate", f"{active_df['M7 Return Rate'].mean():.1f}%")
                critical_count = len(metrics_df[metrics_df['Status'].isin(['CRITICAL', 'HIGH'])])
                col3.metric("Critical Issues", critical_count)
                improving_count = len(metrics_df[metrics_df['Overall Trend'] == 'Improving'])
                col4.metric("Improving", improving_count)
                
                # Main Visualization - Return Rate by Branch
                st.subheader("Branch Performance")
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
                        title="Return Rate by Branch",
                        height=500,
                        xaxis_tickangle=-45,
                        showlegend=False,
                        font=dict(size=12),
                        yaxis_title="Return Rate (%)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Two Column Layout for Issues and Wins
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Issues to Address")
                    critical_df = metrics_df[metrics_df['Status'].isin(['CRITICAL', 'HIGH'])].sort_values('Priority')
                    if len(critical_df) > 0:
                        for idx, row in critical_df.iterrows():
                            color = get_status_color(row['Status'])
                            st.markdown(f"""
                            <div style='background: #f8f9fa; padding: 1rem; border-left: 4px solid {color}; border-radius: 4px; margin-bottom: 0.5rem;'>
                                <b style='color: {color};'>{row['Branch']}</b><br>
                                Return Rate: {row['M7 Return Rate']:.1f}% | Status: {row['Status']}
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("No critical issues")
                
                with col2:
                    st.subheader("Improving Branches")
                    improving_df = metrics_df[metrics_df['Overall Trend'] == 'Improving'].sort_values('M7 Return Rate')
                    if len(improving_df) > 0:
                        for idx, row in improving_df.iterrows():
                            st.markdown(f"""
                            <div style='background: #f8f9fa; padding: 1rem; border-left: 4px solid #28a745; border-radius: 4px; margin-bottom: 0.5rem;'>
                                <b style='color: #28a745;'>{row['Branch']}</b><br>
                                Return Rate: {row['M7 Return Rate']:.1f}% | Trend: Improving
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No improving branches")
                
                # Trend Analysis
                st.subheader("Trend Analysis")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    improving = len(metrics_df[metrics_df['Overall Trend'] == 'Improving'])
                    st.metric("Improving", improving, delta=f"+{improving}")
                
                with col2:
                    stable = len(metrics_df[metrics_df['Overall Trend'] == 'Stable'])
                    st.metric("Stable", stable)
                
                with col3:
                    worsening = len(metrics_df[metrics_df['Overall Trend'] == 'Worsening'])
                    st.metric("Worsening", worsening, delta=f"-{worsening}")
                
                # Detailed Table (Optional - Collapsible)
                with st.expander("View Detailed Data"):
                    display_df = active_df[['Branch', 'M7 Return Rate', 'Last Quarter Avg', 'Quarter Trend', 'Overall Trend', 'Status']].copy()
                    display_df['M7 Return Rate'] = display_df['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_df['Last Quarter Avg'] = display_df['Last Quarter Avg'].apply(lambda x: f"{x:.1f}%" if x else "N/A")
                    st.dataframe(display_df, use_container_width=True, hide_index=True)
