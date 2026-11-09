import streamlit as st
import pandas as pd
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

def calculate_recommendations(branch_data):
    """Calculate optimal order recommendations for a branch"""
    
    if len(branch_data) == 0:
        return None
    
    # Current metrics (October only)
    avg_quantity = branch_data['Gross Sales'].mean()
    total_quantity = branch_data['Gross Sales'].sum()
    total_returns = branch_data['Returns'].sum()
    
    if total_quantity == 0:
        return None
    
    current_return_rate = (total_returns / total_quantity * 100)
    
    # Calculate order interval (days between orders)
    weeks = sorted(branch_data['Week'].unique())
    if len(weeks) > 1:
        intervals = np.diff(weeks)
        avg_interval = intervals.mean()
    else:
        avg_interval = 7
    
    # Recommendations based on October return rate
    if current_return_rate > 30:
        # CRITICAL - reduce quantity slightly
        recommended_quantity = avg_quantity * 0.85
        recommended_interval = avg_interval
        expected_return_reduction = current_return_rate * 0.3
        expected_sales_increase = 0
        confidence = 0.85
        status = "CRITICAL"
        action = "Reduce Quantity"
    elif current_return_rate > 20:
        # HIGH - reduce quantity slightly
        recommended_quantity = avg_quantity * 0.88
        recommended_interval = avg_interval
        expected_return_reduction = current_return_rate * 0.25
        expected_sales_increase = 0
        confidence = 0.80
        status = "HIGH PRIORITY"
        action = "Reduce Quantity"
    elif current_return_rate > 15:
        # MODERATE - small reduction
        recommended_quantity = avg_quantity * 0.92
        recommended_interval = avg_interval
        expected_return_reduction = current_return_rate * 0.2
        expected_sales_increase = 0
        confidence = 0.75
        status = "MODERATE"
        action = "Reduce Quantity"
    elif current_return_rate > 10:
        # WATCH - maintain
        recommended_quantity = avg_quantity * 1.00
        recommended_interval = avg_interval
        expected_return_reduction = current_return_rate * 0.1
        expected_sales_increase = 0
        confidence = 0.70
        status = "WATCH"
        action = "Maintain Orders"
    else:
        # EXCELLENT - increase quantity
        recommended_quantity = avg_quantity * 1.15
        recommended_interval = avg_interval
        expected_return_reduction = 0
        expected_sales_increase = 12
        confidence = 0.85
        status = "EXCELLENT"
        action = "Increase Orders"
    
    return {
        'avg_quantity': avg_quantity,
        'recommended_quantity': recommended_quantity,
        'avg_interval': avg_interval,
        'recommended_interval': recommended_interval,
        'current_return_rate': current_return_rate,
        'expected_return_reduction': expected_return_reduction,
        'expected_sales_increase': expected_sales_increase,
        'confidence': confidence,
        'status': status,
        'action': action,
        'quantity_change': ((recommended_quantity - avg_quantity) / avg_quantity * 100),
        'interval_change': ((recommended_interval - avg_interval) / avg_interval * 100)
    }

def show():
    # Check if data is loaded
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Add month column
    df['Month'] = df['Week'].apply(get_month_from_week)
    
    # Filter for October data
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
    
    # Calculate recommendations for all branches
    recommendations_list = []
    
    for branch in outlet_branches:
        branch_data = df[df['Branch'] == branch]
        october_data = branch_data[branch_data['Week'].isin(october_weeks)]
        
        if len(october_data) == 0:
            continue
        
        rec = calculate_recommendations(october_data)
        
        if rec:
            rec['Branch'] = branch
            rec['Branch Name'] = branch.split('-')[-1].strip() if '-' in branch else branch
            recommendations_list.append(rec)
    
    if not recommendations_list:
        st.info("No recommendations available for selected outlet")
        return
    
    # Create recommendations dataframe
    rec_df = pd.DataFrame(recommendations_list)
    
    # Overview metrics
    st.subheader("Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Branches", len(rec_df))
    
    with col2:
        excellent = len(rec_df[rec_df['status'] == 'EXCELLENT'])
        st.metric("Excellent", excellent)
    
    with col3:
        high_priority = len(rec_df[rec_df['status'].isin(['CRITICAL', 'HIGH PRIORITY'])])
        st.metric("High Priority", high_priority)
    
    with col4:
        avg_return_rate = rec_df['current_return_rate'].mean()
        st.metric("Avg Return Rate", f"{avg_return_rate:.1f}%")
    
    # Recommendations table
    st.subheader("Recommendations")
    
    # Create display dataframe
    display_df = rec_df[['Branch Name', 'current_return_rate', 'avg_quantity', 'recommended_quantity', 'status', 'action', 'confidence']].copy()
    display_df.columns = ['Branch', 'Return Rate', 'Current Qty/Week', 'Recommended Qty/Week', 'Status', 'Action', 'Confidence']
    
    # Add total October column
    display_df['Total Oct'] = (display_df['Current Qty/Week'].astype(float) * 4).astype(int)
    
    display_df['Return Rate'] = display_df['Return Rate'].apply(lambda x: f"{x:.1f}%")
    display_df['Current Qty/Week'] = display_df['Current Qty/Week'].apply(lambda x: f"{int(x)}")
    display_df['Recommended Qty/Week'] = display_df['Recommended Qty/Week'].apply(lambda x: f"{int(x)}")
    display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.0%}")
    
    display_df = display_df.sort_values('Return Rate', ascending=False)
    display_df = display_df[['Branch', 'Return Rate', 'Current Qty/Week', 'Total Oct', 'Recommended Qty/Week', 'Status', 'Action', 'Confidence']]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.caption("📊 Qty/Week = average weekly order quantity. Total Oct = estimated total for 4 weeks. High returns = reduce slightly. Low returns = increase to boost sales.")
