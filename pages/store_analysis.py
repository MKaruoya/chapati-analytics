import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_monthly_metrics, extract_outlet_name

def show():
    st.header("Individual Branch Analysis")
    st.caption("Detailed performance metrics for October")
    
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Load weekly data
    try:
        weekly_df = pd.read_csv('data/october_weekly_actual.csv')
    except:
        st.error("Weekly data file not found. Please run extract_actual_weeks.py first.")
        return
    
    # Get all valid branches
    all_names = df['Branch'].dropna().unique()
    branches = [
        name for name in all_names 
        if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()
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
    
    # Calculate monthly metrics
    monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
    monthly_df = pd.DataFrame(monthly_data)
    
    # Filter to months with data
    monthly_df = monthly_df[monthly_df['has_data'] == True]
    
    if len(monthly_df) == 0:
        st.info("No data available for this branch")
        return
    
    # Extract branch name
    branch_name = selected_branch.split('-')[-1].strip() if '-' in selected_branch else selected_branch
    outlet_name = extract_outlet_name(selected_branch)
    
    st.subheader(f"{outlet_name} - {branch_name}")
    
    # Performance Summary
    st.subheader("Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    current_month = monthly_df.iloc[-1]
    avg_return = monthly_df['return_rate'].mean()
    total_sales = monthly_df['sales'].sum()
    total_returns = monthly_df['returns'].sum()
    
    with col1:
        st.metric("Current Month Return Rate", f"{current_month['return_rate']:.1f}%")
        st.caption("October performance")
    
    with col2:
        st.metric("Average Return Rate", f"{avg_return:.1f}%")
        st.caption("All months average")
    
    with col3:
        st.metric("Total Sales", f"{total_sales:.0f}")
        st.caption("Cumulative net sales")
    
    with col4:
        st.metric("Total Returns", f"{total_returns:.0f}")
        st.caption("Cumulative returns")
    
    # Monthly Trend Chart
    st.subheader("Monthly Return Rate Trend")
    st.caption("Return rate progression from March to October")
    
    month_labels = [f"M{int(m)}" for m in monthly_df['month_num']]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=month_labels,
        y=monthly_df['return_rate'],
        mode='lines+markers',
        name='Return Rate',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(220, 53, 69, 0.1)'
    ))
    
    fig.update_layout(
        title="Return Rate Trend",
        xaxis_title="Month",
        yaxis_title="Return Rate (%)",
        hovermode='x unified',
        height=450,
        font=dict(size=11),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Sales vs Returns Chart
    st.subheader("Sales and Returns Comparison")
    st.caption("Monthly net sales and returns volume")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=month_labels,
        y=monthly_df['sales'],
        name='Net Sales',
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
        font=dict(size=11),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Performance Analysis
    st.subheader("Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Key Metrics**")
        
        first_month_return = monthly_df.iloc[0]['return_rate']
        last_month_return = monthly_df.iloc[-1]['return_rate']
        
        if last_month_return < first_month_return - 2:
            trend = "Declining"
            trend_color = "#28a745"
        elif last_month_return > first_month_return + 2:
            trend = "Rising"
            trend_color = "#dc3545"
        else:
            trend = "Stable"
            trend_color = "#6c757d"
        
        st.markdown(f"<span style='color: {trend_color}; font-weight: bold;'>Trend: {trend}</span>", unsafe_allow_html=True)
        st.write(f"Started at: {first_month_return:.1f}% | Current: {last_month_return:.1f}%")
        
        st.write("")
        st.markdown("**Best Month**")
        best_month = monthly_df.loc[monthly_df['return_rate'].idxmin()]
        st.write(f"M{int(best_month['month_num'])}: {best_month['return_rate']:.1f}% return rate")
        
        st.write("")
        st.markdown("**Worst Month**")
        worst_month = monthly_df.loc[monthly_df['return_rate'].idxmax()]
        st.write(f"M{int(worst_month['month_num'])}: {worst_month['return_rate']:.1f}% return rate")
    
    with col2:
        st.markdown("**Insights**")
        
        volatility = monthly_df['return_rate'].std()
        st.write(f"Volatility: {volatility:.1f}%")
        
        if volatility > 10:
            st.caption("High volatility - inconsistent performance")
        elif volatility > 5:
            st.caption("Moderate volatility - some fluctuation")
        else:
            st.caption("Low volatility - consistent performance")
        
        st.write("")
        
        if len(monthly_df) > 1:
            sales_values = monthly_df['sales'].values
            returns_values = monthly_df['returns'].values
            
            if len(sales_values) > 1 and np.std(sales_values) > 0 and np.std(returns_values) > 0:
                corr = np.corrcoef(sales_values, returns_values)[0, 1]
                st.write(f"Sales vs Returns Correlation: {corr:.3f}")
                
                if corr > 0.3:
                    st.caption("Higher sales correlate with higher returns")
                elif corr < -0.3:
                    st.caption("Higher sales correlate with lower returns")
                else:
                    st.caption("No strong relationship between sales and returns")
    
    # Current Status
    st.subheader("Current Status")
    
    if current_month['return_rate'] > 30:
        status_color = "#dc3545"
        status_text = "CRITICAL"
    elif current_month['return_rate'] > 20:
        status_color = "#fd7e14"
        status_text = "HIGH"
    elif current_month['return_rate'] > 15:
        status_color = "#ffc107"
        status_text = "MODERATE"
    else:
        status_color = "#28a745"
        status_text = "GOOD"
    
    st.markdown(f"""
    <div style='background: #f8f9fa; padding: 1.5rem; border-left: 4px solid {status_color}; border-radius: 4px;'>
        <b style='color: {status_color}; font-size: 18px;'>{status_text}</b><br>
        October Return Rate: {current_month['return_rate']:.1f}% | Trend: {trend}
    </div>
    """, unsafe_allow_html=True)
    
    # Detailed Data Tabs
    tab1, tab2 = st.tabs(["Monthly Data", "Weekly Data"])
    
    with tab1:
        st.subheader("Detailed Monthly Data")
        
        display_monthly = monthly_df.copy()
        display_monthly['Month'] = display_monthly['month_num'].apply(lambda x: f"M{int(x)}")
        display_monthly['Sales'] = display_monthly['sales'].apply(lambda x: f"{x:.0f}")
        display_monthly['Returns'] = display_monthly['returns'].apply(lambda x: f"{x:.0f}")
        display_monthly['Return Rate'] = display_monthly['return_rate'].apply(lambda x: f"{x:.1f}%")
        
        final_display = display_monthly[['Month', 'Sales', 'Returns', 'Return Rate']]
        st.dataframe(final_display, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Weekly Data")
        st.caption("Actual weekly sales and returns")
        
        # Get weekly data for this branch
        branch_weekly = weekly_df[weekly_df['Branch'] == selected_branch].copy()
        
        if len(branch_weekly) == 0:
            st.info("No weekly data available for this branch")
        else:
            # Add month label
            branch_weekly['Month'] = branch_weekly['Month'].apply(lambda x: f"M{int(x)}")
            
            # Display chart
            fig3 = go.Figure()
            
            fig3.add_trace(go.Scatter(
                x=branch_weekly['Week'],
                y=branch_weekly['Return Rate'],
                mode='lines+markers',
                name='Return Rate',
                line=dict(color='#9b59b6', width=2),
                marker=dict(size=6)
            ))
            
            fig3.update_layout(
                title="Weekly Return Rate Trend",
                xaxis_title="Week",
                yaxis_title="Return Rate (%)",
                hovermode='x unified',
                height=400,
                font=dict(size=11),
                showlegend=False
            )
            
            st.plotly_chart(fig3, use_container_width=True)
            
            # Weekly data table
            display_weekly = branch_weekly[['Week', 'Month', 'Sales', 'Returns', 'Return Rate']].copy()
            display_weekly['Return Rate'] = display_weekly['Return Rate'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(display_weekly, use_container_width=True, hide_index=True)
