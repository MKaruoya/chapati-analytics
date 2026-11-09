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

def color_status_cell(val):
    """Color code status cells"""
    if val == 'CRITICAL':
        return 'background-color: #dc3545; color: white; font-weight: bold; text-align: center;'
    elif val == 'HIGH':
        return 'background-color: #fd7e14; color: white; font-weight: bold; text-align: center;'
    elif val == 'MODERATE':
        return 'background-color: #ffc107; color: black; font-weight: bold; text-align: center;'
    elif val == 'WATCH':
        return 'background-color: #ffc107; color: black; font-weight: bold; text-align: center;'
    elif val == 'GOOD':
        return 'background-color: #28a745; color: white; font-weight: bold; text-align: center;'
    return ''

def show():
    # Check if data is loaded
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Add month column
    df['Month'] = df['Week'].apply(get_month_from_week)
    
    # Filter for October data only (Weeks 41-44, Month 8)
    october_weeks = [41, 42, 43, 44]
    df_october = df[df['Week'].isin(october_weeks)].copy()
    
    if len(df_october) == 0:
        st.error("No October data found in dataset")
        return
    
    # Extract valid branches
    all_names = df_october['Branch'].dropna().unique()
    valid_branches = [
        name for name in all_names 
        if isinstance(name, str) and len(name) > 0
    ]
    
    if not valid_branches:
        st.error("No valid branches found in October data")
        return
    
    # Extract outlet names
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
    
    # Calculate metrics for all branches
    branch_metrics = []
    
    for branch in outlet_branches:
        # October data
        october_data = df_october[df_october['Branch'] == branch]
        
        if len(october_data) == 0:
            continue
        
        # Aggregate October (SUM of all weeks)
        oct_gross = october_data['Gross Sales'].sum()
        oct_returns = october_data['Returns'].sum()
        oct_net = october_data['Net Sales'].sum()
        
        if oct_gross == 0:
            continue
        
        oct_return_rate = (oct_returns / oct_gross * 100)
        
        # Get trend by comparing first 4 months vs last 4 months (from full dataset)
        branch_all = df[df['Branch'] == branch]
        
        # First 4 months: March, April, May, June (Months 1-4)
        first_four = branch_all[branch_all['Month'].isin([1, 2, 3, 4])]
        # Last 4 months: July, August, September, October (Months 5-8)
        last_four = branch_all[branch_all['Month'].isin([5, 6, 7, 8])]
        
        if len(first_four) > 0 and len(last_four) > 0:
            first_rate = first_four['Return Rate'].mean()
            last_rate = last_four['Return Rate'].mean()
            
            if last_rate < first_rate - 2:
                trend = "Improving"
            elif last_rate > first_rate + 2:
                trend = "Worsening"
            else:
                trend = "Stable"
        else:
            trend = "Stable"
        
        # Get status
        status = get_status_for_return_rate(oct_return_rate)
        
        branch_metrics.append({
            'Branch': branch,
            'Gross Sales': oct_gross,
            'Returns': oct_returns,
            'Net Sales': oct_net,
            'Return Rate': oct_return_rate,
            'Status': status,
            'Trend': trend,
            'Weeks': len(october_data['Week'].unique())
        })
    
    if not branch_metrics:
        st.info("No data available for selected outlet in October")
        return
    
    # Create metrics dataframe
    metrics_df = pd.DataFrame(branch_metrics)
    
    # Separate normal branches from negative sales branches
    normal_branches = metrics_df[metrics_df['Net Sales'] >= 0].copy()
    negative_branches = metrics_df[metrics_df['Net Sales'] < 0].copy()
    
    # Create tabs
    tab1, tab2 = st.tabs(["Normal Sales", "Negative Sales (High Returns)"])
    
    # ===== TAB 1: NORMAL SALES =====
    with tab1:
        if len(normal_branches) == 0:
            st.info("No branches with normal sales")
        else:
            # Display overview metrics
            st.subheader("October Performance Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Branches", len(normal_branches))
            
            with col2:
                # Calculate TRUE overall return rate (not average of branches)
                total_gross = normal_branches['Gross Sales'].sum()
                total_returns = normal_branches['Returns'].sum()
                true_return_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0
                st.metric("Overall Return Rate", f"{true_return_rate:.1f}%")
            
            with col3:
                critical_count = len(normal_branches[normal_branches['Status'].isin(['CRITICAL', 'HIGH'])])
                st.metric("High Risk Branches", critical_count)
            
            with col4:
                improving_count = len(normal_branches[normal_branches['Trend'] == 'Improving'])
                st.metric("Improving", improving_count)
            
            # Branch Performance Chart
            st.subheader("October Return Rate by Branch")
            st.caption("Sorted by return rate (highest to lowest) - Sum of all October weeks")
            
            sorted_df = normal_branches.sort_values('Return Rate', ascending=False)
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
                title=f"October Return Rates - {selected_outlet}",
                height=500,
                xaxis_tickangle=-45,
                showlegend=False,
                font=dict(size=11),
                yaxis_title="Return Rate (%)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trend Analysis
            st.subheader("Return Rate Trends")
            st.caption("Comparison of first 4 months (March-June) vs last 4 months (July-October)")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                improving = len(normal_branches[normal_branches['Trend'] == 'Improving'])
                st.metric("Improving", improving)
                st.caption("Return rates decreasing")
            
            with col2:
                stable = len(normal_branches[normal_branches['Trend'] == 'Stable'])
                st.metric("Stable", stable)
                st.caption("Return rates unchanged")
            
            with col3:
                worsening = len(normal_branches[normal_branches['Trend'] == 'Worsening'])
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
            with st.expander("View Detailed Branch Data - October Summary"):
                display_df = normal_branches.copy()
                display_df['Branch Name'] = display_df['Branch'].apply(lambda x: x.split('-')[-1].strip() if '-' in x else x)
                
                final_df = display_df[['Branch Name', 'Gross Sales', 'Returns', 'Net Sales', 'Return Rate', 'Trend', 'Status', 'Weeks']].copy()
                final_df['Gross Sales'] = final_df['Gross Sales'].apply(lambda x: f"{int(x):,}")
                final_df['Returns'] = final_df['Returns'].apply(lambda x: f"{int(x):,}")
                final_df['Net Sales'] = final_df['Net Sales'].apply(lambda x: f"{int(x):,}")
                final_df['Return Rate'] = final_df['Return Rate'].apply(lambda x: f"{x:.1f}%")
                final_df['Weeks'] = final_df['Weeks'].apply(lambda x: f"{int(x)}/4")
                final_df = final_df.sort_values('Return Rate', ascending=False)
                
                # Apply color coding to Status column
                styled_df = final_df.style.map(color_status_cell, subset=['Status'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                st.caption("📊 All figures are sums of available October weeks (Weeks 41-44). 'Weeks' column shows data coverage (e.g., 2/4 means 2 weeks of data available).")
    
    # ===== TAB 2: NEGATIVE SALES =====
    with tab2:
        if len(negative_branches) == 0:
            st.success("✅ No branches with negative sales!")
        else:
            st.info(f"**{len(negative_branches)} branches with Negative Net Sales**")
            
            # Overview
            st.subheader("Negative Sales Summary")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Branches", len(negative_branches))
            
            with col2:
                # Calculate TRUE overall return rate for negative branches
                total_gross = negative_branches['Gross Sales'].sum()
                total_returns = negative_branches['Returns'].sum()
                true_return_rate = (total_returns / total_gross * 100) if total_gross > 0 else 0
                st.metric("Overall Return Rate", f"{true_return_rate:.1f}%")
            
            with col3:
                total_negative = negative_branches['Net Sales'].sum()
                st.metric("Total Negative Sales", f"{int(total_negative):,}")
            
            # Chart
            st.subheader("Negative Sales Branches")
            
            sorted_neg = negative_branches.sort_values('Net Sales')
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sorted_neg['Branch'],
                y=sorted_neg['Net Sales'],
                marker=dict(color='#dc3545', line=dict(color='#721c24', width=1)),
                text=sorted_neg['Net Sales'].apply(lambda x: f"{int(x)}"),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Net Sales: %{y}<extra></extra>'
            ))
            
            fig.update_layout(
                title=f"Negative Net Sales - {selected_outlet}",
                height=500,
                xaxis_tickangle=-45,
                showlegend=False,
                font=dict(size=11),
                yaxis_title="Net Sales (units)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed table
            with st.expander("View Detailed Negative Sales Data"):
                display_df = negative_branches.copy()
                display_df['Branch Name'] = display_df['Branch'].apply(lambda x: x.split('-')[-1].strip() if '-' in x else x)
                
                final_df = display_df[['Branch Name', 'Gross Sales', 'Returns', 'Net Sales', 'Return Rate', 'Status', 'Weeks']].copy()
                final_df['Gross Sales'] = final_df['Gross Sales'].apply(lambda x: f"{int(x):,}")
                final_df['Returns'] = final_df['Returns'].apply(lambda x: f"{int(x):,}")
                final_df['Net Sales'] = final_df['Net Sales'].apply(lambda x: f"{int(x):,}")
                final_df['Return Rate'] = final_df['Return Rate'].apply(lambda x: f"{x:.1f}%")
                final_df['Weeks'] = final_df['Weeks'].apply(lambda x: f"{int(x)}/4")
                final_df = final_df.sort_values('Return Rate', ascending=False)
                
                # Apply color coding to Status column
                styled_df = final_df.style.map(color_status_cell, subset=['Status'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
