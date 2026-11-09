import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def get_month_from_week(week):
    """Convert week number to month (1-8)"""
    if week <= 14:
        return 1  # March
    elif week <= 18:
        return 2  # April
    elif week <= 22:
        return 3  # May
    elif week <= 27:
        return 4  # June
    elif week <= 31:
        return 5  # July
    elif week <= 36:
        return 6  # August
    elif week <= 40:
        return 7  # September
    else:
        return 8  # October

def show():
    st.header("Branch Analysis")
    
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Add month column
    df['Month'] = df['Week'].apply(get_month_from_week)
    
    # Get all valid branches
    all_names = df['Branch'].dropna().unique()
    branches = [
        name for name in all_names 
        if isinstance(name, str) and len(name) > 0
    ]
    
    if not branches:
        st.error("No valid branches found")
        return
    
    # Branch selector
    st.subheader("Select Branch")
    selected_branch = st.selectbox(
        "Choose a branch to analyze:",
        sorted(branches),
        label_visibility="collapsed"
    )
    
    branch_data = df[df['Branch'] == selected_branch]
    
    if len(branch_data) == 0:
        st.error("Branch data not found")
        return
    
    # Calculate monthly metrics
    monthly_metrics = []
    
    for month in sorted(branch_data['Month'].unique()):
        month_data = branch_data[branch_data['Month'] == month]
        
        # Skip if no data for this month
        if len(month_data) == 0:
            continue
        
        gross = month_data['Gross Sales'].sum()
        returns = month_data['Returns'].sum()
        net = month_data['Net Sales'].sum()
        
        # Skip if no sales
        if gross == 0:
            continue
        
        return_rate = (returns / gross * 100)
        
        monthly_metrics.append({
            'Month': month,
            'Gross Sales': gross,
            'Returns': returns,
            'Net Sales': net,
            'Return Rate': return_rate,
            'Weeks': len(month_data['Week'].unique())
        })
    
    monthly_df = pd.DataFrame(monthly_metrics)
    
    if len(monthly_df) == 0:
        st.error("No data available for this branch")
        return
    
    # Check if branch has October data
    october_data_check = branch_data[branch_data['Month'] == 8]
    has_october = len(october_data_check) > 0
    
    if not has_october:
        st.error("❌ This branch has NO October data")
        st.info("This branch did not report data for October (Weeks 41-44).")
        
        if len(monthly_df) > 0:
            st.subheader("Historical Data (March - September)")
            monthly_df = monthly_df[monthly_df['Month'] != 8]
        else:
            return
    
    # Performance Summary
    st.subheader("Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    current_month = monthly_df.iloc[-1]
    avg_return = monthly_df['Return Rate'].mean()
    total_gross = monthly_df['Gross Sales'].sum()
    total_returns = monthly_df['Returns'].sum()
    
    with col1:
        month_label = "October" if has_october else f"M{int(current_month['Month'])}"
        st.metric(f"{month_label} Return Rate", f"{current_month['Return Rate']:.1f}%")
        st.caption("Latest month")
    
    with col2:
        st.metric("Average Return Rate", f"{avg_return:.1f}%")
        st.caption("All months average")
    
    with col3:
        st.metric("Total Gross Sales", f"{int(total_gross):,}")
        st.caption("Cumulative")
    
    with col4:
        st.metric("Total Returns", f"{int(total_returns):,}")
        st.caption("Cumulative")
    
    # Monthly Trend Chart
    st.subheader("Monthly Return Rate Trend")
    st.caption("Return rate progression")
    
    month_labels = [f"M{int(m)}" for m in monthly_df['Month']]
    
    fig_monthly_trend = go.Figure()
    
    fig_monthly_trend.add_trace(go.Scatter(
        x=month_labels,
        y=monthly_df['Return Rate'],
        mode='lines+markers',
        name='Return Rate',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.1)'
    ))
    
    fig_monthly_trend.update_layout(
        title="Return Rate Trend",
        xaxis_title="Month",
        yaxis_title="Return Rate (%)",
        hovermode='x unified',
        height=450,
        font=dict(size=11),
        showlegend=False
    )
    
    st.plotly_chart(fig_monthly_trend, use_container_width=True)
    
    # Monthly Sales vs Returns Chart
    st.subheader("Monthly Sales and Returns Comparison")
    st.caption("Monthly gross sales and returns volume")
    
    fig_monthly_comparison = go.Figure()
    
    fig_monthly_comparison.add_trace(go.Bar(
        x=month_labels,
        y=monthly_df['Gross Sales'],
        name='Gross Sales',
        marker_color='#3498db'
    ))
    
    fig_monthly_comparison.add_trace(go.Bar(
        x=month_labels,
        y=monthly_df['Returns'],
        name='Returns',
        marker_color='#e74c3c'
    ))
    
    fig_monthly_comparison.update_layout(
        title="Monthly Sales and Returns",
        xaxis_title="Month",
        yaxis_title="Volume",
        barmode='group',
        height=400,
        font=dict(size=11),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_monthly_comparison, use_container_width=True)
    
    # Performance Analysis
    st.subheader("Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Key Metrics**")
        
        first_month_return = monthly_df.iloc[0]['Return Rate']
        last_month_return = monthly_df.iloc[-1]['Return Rate']
        
        if last_month_return < first_month_return - 2:
            trend = "Improving"
            trend_color = "#28a745"
        elif last_month_return > first_month_return + 2:
            trend = "Worsening"
            trend_color = "#dc3545"
        else:
            trend = "Stable"
            trend_color = "#6c757d"
        
        st.markdown(f"<span style='color: {trend_color}; font-weight: bold;'>Trend: {trend}</span>", unsafe_allow_html=True)
        st.write(f"Started at: {first_month_return:.1f}% | Current: {last_month_return:.1f}%")
        
        st.write("")
        st.markdown("**Best Month**")
        best_month = monthly_df.loc[monthly_df['Return Rate'].idxmin()]
        st.write(f"M{int(best_month['Month'])}: {best_month['Return Rate']:.1f}% return rate")
        
        st.write("")
        st.markdown("**Worst Month**")
        worst_month = monthly_df.loc[monthly_df['Return Rate'].idxmax()]
        st.write(f"M{int(worst_month['Month'])}: {worst_month['Return Rate']:.1f}% return rate")
    
    with col2:
        st.markdown("**Insights**")
        
        volatility = monthly_df['Return Rate'].std()
        st.write(f"Volatility: {volatility:.1f}%")
        
        if volatility > 10:
            st.caption("High volatility - inconsistent performance")
        elif volatility > 5:
            st.caption("Moderate volatility - some fluctuation")
        else:
            st.caption("Low volatility - consistent performance")
        
        st.write("")
        
        if len(monthly_df) > 1:
            gross_values = monthly_df['Gross Sales'].values
            returns_values = monthly_df['Returns'].values
            
            if len(gross_values) > 1 and np.std(gross_values) > 0 and np.std(returns_values) > 0:
                corr = np.corrcoef(gross_values, returns_values)[0, 1]
                st.write(f"Sales vs Returns Correlation: {corr:.3f}")
                
                if corr > 0.3:
                    st.caption("Higher sales correlate with higher returns")
                elif corr < -0.3:
                    st.caption("Higher sales correlate with lower returns")
                else:
                    st.caption("No strong relationship between sales and returns")
    
    # Current Status
    st.subheader("Current Status")
    
    if current_month['Return Rate'] > 30:
        status_color = "#dc3545"
        status_text = "CRITICAL"
    elif current_month['Return Rate'] > 20:
        status_color = "#fd7e14"
        status_text = "HIGH"
    elif current_month['Return Rate'] > 15:
        status_color = "#ffc107"
        status_text = "MODERATE"
    else:
        status_color = "#28a745"
        status_text = "GOOD"
    
    st.markdown(f"""
    <div style='background: #f8f9fa; padding: 1.5rem; border-left: 4px solid {status_color}; border-radius: 4px;'>
        <b style='color: {status_color}; font-size: 18px;'>{status_text}</b><br>
        Latest Return Rate: {current_month['Return Rate']:.1f}% | Trend: {trend}
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed Data Tabs
    tab1, tab2 = st.tabs(["Monthly Data", "Weekly Data"])
    
    with tab1:
        st.subheader("Detailed Monthly Data")
        
        display_monthly = monthly_df.copy()
        display_monthly['Month'] = display_monthly['Month'].apply(lambda x: f"M{int(x)}")
        display_monthly['Gross Sales'] = display_monthly['Gross Sales'].apply(lambda x: f"{int(x):,}")
        display_monthly['Returns'] = display_monthly['Returns'].apply(lambda x: f"{int(x):,}")
        display_monthly['Net Sales'] = display_monthly['Net Sales'].apply(lambda x: f"{int(x):,}")
        display_monthly['Return Rate'] = display_monthly['Return Rate'].apply(lambda x: f"{x:.1f}%")
        
        final_display = display_monthly[['Month', 'Gross Sales', 'Returns', 'Net Sales', 'Return Rate', 'Weeks']]
        st.dataframe(final_display, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Weekly Data")
        
        if not has_october:
            st.info("📊 No October weekly data available for this branch.")
            
            # Show latest available data instead
            latest_week = branch_data['Week'].max()
            latest_data = branch_data[branch_data['Week'] == latest_week]
            
            if len(latest_data) > 0:
                st.subheader("Latest Available Data")
                st.caption(f"Last reported: Week {int(latest_week)}")
                display_latest = latest_data[['Week', 'Gross Sales', 'Returns', 'Net Sales', 'Return Rate']].copy()
                display_latest['Gross Sales'] = display_latest['Gross Sales'].apply(lambda x: f"{int(x):,}")
                display_latest['Returns'] = display_latest['Returns'].apply(lambda x: f"{int(x):,}")
                display_latest['Net Sales'] = display_latest['Net Sales'].apply(lambda x: f"{int(x):,}")
                display_latest['Return Rate'] = display_latest['Return Rate'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(display_latest, use_container_width=True, hide_index=True)
        else:
            st.caption("October weekly sales and returns")
            
            # Get October weekly data
            october_weeks = [41, 42, 43, 44]
            october_data = branch_data[branch_data['Week'].isin(october_weeks)].copy()
            
            if len(october_data) == 0:
                st.info("No October weekly data available")
            else:
                # Weekly Return Rate Trend Chart
                fig_weekly_trend = go.Figure()
                
                fig_weekly_trend.add_trace(go.Scatter(
                    x=october_data['Week'],
                    y=october_data['Return Rate'],
                    mode='lines+markers',
                    name='Return Rate',
                    line=dict(color='#9b59b6', width=2),
                    marker=dict(size=6)
                ))
                
                fig_weekly_trend.update_layout(
                    title="October Weekly Return Rate Trend",
                    xaxis_title="Week",
                    yaxis_title="Return Rate (%)",
                    hovermode='x unified',
                    height=400,
                    font=dict(size=11),
                    showlegend=False
                )
                
                st.plotly_chart(fig_weekly_trend, use_container_width=True)
                
                # Weekly Sales vs Returns Chart
                fig_weekly_comparison = go.Figure()
                
                fig_weekly_comparison.add_trace(go.Bar(
                    x=october_data['Week'],
                    y=october_data['Gross Sales'],
                    name='Gross Sales',
                    marker_color='#3498db'
                ))
                
                fig_weekly_comparison.add_trace(go.Bar(
                    x=october_data['Week'],
                    y=october_data['Returns'],
                    name='Returns',
                    marker_color='#e74c3c'
                ))
                
                fig_weekly_comparison.update_layout(
                    title="October Weekly Sales and Returns",
                    xaxis_title="Week",
                    yaxis_title="Volume",
                    barmode='group',
                    height=400,
                    font=dict(size=11),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_weekly_comparison, use_container_width=True)
                
                # Weekly data table
                display_weekly = october_data[['Week', 'Gross Sales', 'Returns', 'Net Sales', 'Return Rate']].copy()
                display_weekly['Gross Sales'] = display_weekly['Gross Sales'].apply(lambda x: f"{int(x):,}")
                display_weekly['Returns'] = display_weekly['Returns'].apply(lambda x: f"{int(x):,}")
                display_weekly['Net Sales'] = display_weekly['Net Sales'].apply(lambda x: f"{int(x):,}")
                display_weekly['Return Rate'] = display_weekly['Return Rate'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(display_weekly, use_container_width=True, hide_index=True)
