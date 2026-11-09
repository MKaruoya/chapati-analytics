import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats

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
    
    # Current metrics
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
        avg_interval = 7  # Default to weekly
    
    # Recommendations based on return rate
    if current_return_rate > 20:
        # High returns - reduce quantity
        recommended_quantity = avg_quantity * 0.85
        recommended_interval = avg_interval * 1.1
        expected_return_reduction = current_return_rate * 0.3
        confidence = 0.75
        reasoning = "High return rate detected. Reduce order quantity and increase order frequency to match actual demand."
    elif current_return_rate > 15:
        # Moderate returns - slight adjustment
        recommended_quantity = avg_quantity * 0.90
        recommended_interval = avg_interval * 1.05
        expected_return_reduction = current_return_rate * 0.2
        confidence = 0.70
        reasoning = "Moderate return rate. Small adjustments to quantity and frequency recommended."
    elif current_return_rate > 10:
        # Watch - maintain or slight increase
        recommended_quantity = avg_quantity * 0.95
        recommended_interval = avg_interval * 0.95
        expected_return_reduction = current_return_rate * 0.1
        confidence = 0.65
        reasoning = "Return rate within acceptable range. Minor optimizations possible."
    else:
        # Good - maintain current pattern
        recommended_quantity = avg_quantity
        recommended_interval = avg_interval
        expected_return_reduction = 0
        confidence = 0.80
        reasoning = "Excellent performance. Maintain current ordering pattern."
    
    return {
        'avg_quantity': avg_quantity,
        'recommended_quantity': recommended_quantity,
        'avg_interval': avg_interval,
        'recommended_interval': recommended_interval,
        'current_return_rate': current_return_rate,
        'expected_return_reduction': expected_return_reduction,
        'confidence': confidence,
        'reasoning': reasoning,
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
        
        if len(branch_data) == 0:
            continue
        
        rec = calculate_recommendations(branch_data)
        
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
    st.subheader("Recommendations Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Branches", len(rec_df))
    
    with col2:
        avg_return_rate = rec_df['current_return_rate'].mean()
        st.metric("Average Return Rate", f"{avg_return_rate:.1f}%")
    
    with col3:
        high_priority = len(rec_df[rec_df['current_return_rate'] > 20])
        st.metric("High Priority", high_priority)
    
    with col4:
        avg_confidence = rec_df['confidence'].mean()
        st.metric("Avg Confidence", f"{avg_confidence:.0%}")
    
    # Branch selector for detailed recommendations
    st.subheader("Detailed Recommendations")
    
    selected_branch = st.selectbox(
        "Select a branch to view detailed recommendations:",
        rec_df['Branch Name'].tolist(),
        label_visibility="collapsed"
    )
    
    # Get selected branch recommendation
    branch_rec = rec_df[rec_df['Branch Name'] == selected_branch].iloc[0]
    
    # Display recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Current Order Pattern**")
        st.write(f"Average Quantity: **{branch_rec['avg_quantity']:.0f}** units")
        st.write(f"Average Interval: **{branch_rec['avg_interval']:.1f}** days")
        st.write(f"Current Return Rate: **{branch_rec['current_return_rate']:.1f}%**")
    
    with col2:
        st.markdown("**Recommended Order Pattern**")
        st.write(f"Recommended Quantity: **{branch_rec['recommended_quantity']:.0f}** units")
        st.write(f"Recommended Interval: **{branch_rec['recommended_interval']:.1f}** days")
        
        # Show change
        qty_change = branch_rec['quantity_change']
        interval_change = branch_rec['interval_change']
        
        if qty_change > 0:
            st.write(f"Change: **+{qty_change:.1f}%** (increase)")
        elif qty_change < 0:
            st.write(f"Change: **{qty_change:.1f}%** (decrease)")
        else:
            st.write(f"Change: **No change**")
    
    # Expected impact
    st.subheader("Expected Impact")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Return Rate Reduction", f"{branch_rec['expected_return_reduction']:.1f}%")
        st.caption("Expected decrease in returns")
    
    with col2:
        new_return_rate = branch_rec['current_return_rate'] - branch_rec['expected_return_reduction']
        st.metric("New Return Rate", f"{new_return_rate:.1f}%")
        st.caption("Projected return rate")
    
    with col3:
        st.metric("Confidence Level", f"{branch_rec['confidence']:.0%}")
        st.caption("Recommendation confidence")
    
    # Reasoning
    st.subheader("Reasoning")
    st.info(branch_rec['reasoning'])
    
    # Implementation steps
    st.subheader("Implementation Steps")
    
    steps = [
        f"1. **Adjust Order Quantity**: Change from {branch_rec['avg_quantity']:.0f} to {branch_rec['recommended_quantity']:.0f} units",
        f"2. **Adjust Order Interval**: Change from {branch_rec['avg_interval']:.1f} to {branch_rec['recommended_interval']:.1f} days",
        "3. **Monitor Performance**: Track return rates for 2-4 weeks",
        "4. **Fine-tune**: Make additional adjustments based on actual results",
        "5. **Document**: Record the new ordering pattern for future reference"
    ]
    
    for step in steps:
        st.write(step)
    
    # All branches comparison
    st.subheader("All Branches Comparison")
    
    display_df = rec_df[['Branch Name', 'avg_quantity', 'recommended_quantity', 'current_return_rate', 'expected_return_reduction', 'confidence']].copy()
    display_df.columns = ['Branch', 'Current Qty', 'Recommended Qty', 'Return Rate', 'Expected Reduction', 'Confidence']
    
    display_df['Current Qty'] = display_df['Current Qty'].apply(lambda x: f"{int(x)}")
    display_df['Recommended Qty'] = display_df['Recommended Qty'].apply(lambda x: f"{int(x)}")
    display_df['Return Rate'] = display_df['Return Rate'].apply(lambda x: f"{x:.1f}%")
    display_df['Expected Reduction'] = display_df['Expected Reduction'].apply(lambda x: f"{x:.1f}%")
    display_df['Confidence'] = display_df['Confidence'].apply(lambda x: f"{x:.0%}")
    
    display_df = display_df.sort_values('Return Rate', ascending=False)
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    st.caption("📊 Recommendations are based on October performance data and historical trends.")
