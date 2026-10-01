import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_monthly_metrics, get_active_periods

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📊 Dashboard",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

def calculate_volatility(monthly_data):
    """Calculate volatility score"""
    return_rates = [m['return_rate'] for m in monthly_data if m['has_data']]
    if len(return_rates) > 1:
        return np.std(return_rates)
    return 0

def get_sales_volume_category(total_sales):
    """Categorize by sales volume"""
    abs_sales = abs(total_sales)
    if abs_sales > 500:
        return "High Volume"
    elif abs_sales > 200:
        return "Medium Volume"
    elif abs_sales > 50:
        return "Low Volume"
    else:
        return "Very Low Volume"

def extract_outlet_name(branch_name):
    """Extract outlet name from branch name"""
    if isinstance(branch_name, str) and '-' in branch_name:
        return branch_name.split('-')[0].strip()
    return None

def calculate_quarter_trend(monthly_data):
    """Calculate quarter trend"""
    active_months = [m for m in monthly_data if m['has_data']]
    
    if len(active_months) < 3:
        return None, None, None
    
    last_quarter = active_months[-3:]
    last_quarter_avg = np.mean([m['return_rate'] for m in last_quarter])
    
    if len(active_months) >= 6:
        prev_quarter = active_months[-6:-3]
        prev_quarter_avg = np.mean([m['return_rate'] for m in prev_quarter])
    else:
        prev_quarter_avg = None
    
    if prev_quarter_avg is not None:
        quarter_change = last_quarter_avg - prev_quarter_avg
        if quarter_change < -2:
            trend = "📉 Improving"
        elif quarter_change > 2:
            trend = "📈 Worsening"
        else:
            trend = "➡️ Stable"
    else:
        quarter_change = None
        trend = "N/A"
    
    return last_quarter_avg, quarter_change, trend

def calculate_optimal_order_qty(monthly_data, current_avg_qty, current_return_rate):
    """Calculate optimal order quantity"""
    
    # Get all monthly order quantities and return rates
    quantities = []
    return_rates = []
    
    for m in monthly_data:
        if m['has_data']:
            original_order = abs(m['sales']) + m['returns']
            if original_order > 0:
                quantities.append(original_order)
                return_rates.append(m['return_rate'])
    
    if not quantities:
        return current_avg_qty, current_return_rate, 0.5, "Insufficient data"
    
    # Find the quantity that gives lowest return rate
    best_qty_idx = np.argmin(return_rates)
    best_qty = quantities[best_qty_idx]
    best_return_rate = return_rates[best_qty_idx]
    
    # Calculate median (more stable than mean)
    median_qty = np.median(quantities)
    median_return_rate = np.median(return_rates)
    
    # Recommended quantity: balance between best and median
    # If current return rate is high, reduce quantity
    # If current return rate is low, maintain or slightly increase
    
    if current_return_rate > 25:
        # High returns - reduce significantly
        recommended_qty = median_qty * 0.8
        confidence = 0.8
        reason = "High return rate detected - reduce quantity"
    elif current_return_rate > 20:
        # Moderate returns - reduce slightly
        recommended_qty = median_qty * 0.9
        confidence = 0.7
        reason = "Moderate return rate - slight reduction recommended"
    elif current_return_rate > 15:
        # Watch level - maintain or slight reduction
        recommended_qty = median_qty * 0.95
        confidence = 0.6
        reason = "Return rate in watch zone - maintain current"
    else:
        # Good performance - maintain
        recommended_qty = median_qty
        confidence = 0.8
        reason = "Good performance - maintain current quantity"
    
    return recommended_qty, best_return_rate, confidence, reason

if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data (CSV)")
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            df = df.rename(columns={df.columns[0]: 'Branch'})
            st.session_state.data = df
            st.success("✅ Data uploaded and cleaned successfully!")
            st.subheader("📊 Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            col3.metric("Unique Branches", df['Branch'].nunique())
            col4.metric("Data Pairs (Weeks)", (len(df.columns) - 1) // 2)
            st.subheader("✅ Ready for Analysis!")
            st.write("Go to **Optimal Order Recommendations** to get personalized suggestions for each store.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif page == "📊 Dashboard":
    st.header("📊 Outlet Performance Dashboard")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("Dashboard tab - navigate to other tabs for analysis")

elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis")
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("Store Analysis tab - navigate to other tabs for analysis")

elif page == "🤖 AI Relationship Analysis":
    st.header("🤖 AI Relationship Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("AI Relationship Analysis tab - navigate to other tabs for analysis")

elif page == "💡 Optimal Order Recommendations":
    st.header("💡 Optimal Order Recommendations for Each Store")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
        
        if not outlet_names:
            st.error("❌ No outlets found in data!")
        else:
            st.subheader("🏪 Select Outlet")
            selected_outlet = st.selectbox("Choose an outlet:", outlet_names, key="rec_outlet")
            
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
            
            st.info(f"📍 Generating recommendations for **{selected_outlet}** - {len(outlet_branches)} branches")
            
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            recommendations = []
            
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
                        
                        total_sales = sum([m['sales'] for m in monthly_data])
                        total_returns = sum([m['returns'] for m in monthly_data])
                        
                        # Calculate current average order quantity
                        quantities = []
                        for m in monthly_data:
                            if m['has_data']:
                                original_order = abs(m['sales']) + m['returns']
                                if original_order > 0:
                                    quantities.append(original_order)
                        
                        if quantities:
                            current_avg_qty = np.mean(quantities)
                            current_return_rate = np.mean([m['return_rate'] for m in monthly_data if m['has_data']])
                            
                            # Calculate optimal quantity
                            recommended_qty, best_return_rate, confidence, reason = calculate_optimal_order_qty(
                                monthly_data, current_avg_qty, current_return_rate
                            )
                            
                            # Calculate expected improvement
                            expected_return_reduction = current_return_rate - (current_return_rate * 0.85)
                            
                            recommendations.append({
                                'Branch': branch,
                                'Current Avg Qty': current_avg_qty,
                                'Current Return Rate': current_return_rate,
                                'Recommended Qty': recommended_qty,
                                'Qty Change %': ((recommended_qty - current_avg_qty) / current_avg_qty * 100),
                                'Expected Return Rate': current_return_rate * 0.85,
                                'Expected Reduction': expected_return_reduction,
                                'Confidence': confidence,
                                'Reason': reason,
                                'M7 Active': is_active_m7
                            })
            
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                
                st.subheader("📊 Summary")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Branches", len(rec_df))
                col2.metric("Avg Current Qty", f"{rec_df['Current Avg Qty'].mean():.0f} bales")
                col3.metric("Avg Recommended Qty", f"{rec_df['Recommended Qty'].mean():.0f} bales")
                col4.metric("Avg Expected Return Reduction", f"{rec_df['Expected Reduction'].mean():.1f}%")
                
                st.subheader("🎯 Recommendations by Branch")
                
                # Sort by confidence and return rate
                rec_df_sorted = rec_df.sort_values(['Current Return Rate'], ascending=False)
                
                for idx, row in rec_df_sorted.iterrows():
                    with st.expander(f"📦 {row['Branch']} - Current: {row['Current Avg Qty']:.0f} bales | Return Rate: {row['Current Return Rate']:.1f}%"):
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Current Pattern:**")
                            st.metric("Order Quantity", f"{row['Current Avg Qty']:.0f} bales")
                            st.metric("Return Rate", f"{row['Current Return Rate']:.1f}%")
                        
                        with col2:
                            st.write("**Recommended Pattern:**")
                            st.metric("Order Quantity", f"{row['Recommended Qty']:.0f} bales")
                            st.metric("Return Rate", f"{row['Expected Return Rate']:.1f}%")
                        
                        with col3:
                            st.write("**Impact:**")
                            change_pct = row['Qty Change %']
                            if change_pct < 0:
                                st.metric("Qty Change", f"{change_pct:.1f}%", delta="Reduce")
                            elif change_pct > 0:
                                st.metric("Qty Change", f"{change_pct:+.1f}%", delta="Increase")
                            else:
                                st.metric("Qty Change", "0%", delta="Maintain")
                            
                            st.metric("Expected Return Reduction", f"{row['Expected Reduction']:.1f}%")
                        
                        st.write("---")
                        st.write(f"**Reason:** {row['Reason']}")
                        st.write(f"**Confidence Level:** {row['Confidence']*100:.0f}%")
                
                st.subheader("📈 Visualization: Current vs Recommended")
                
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=rec_df_sorted['Branch'],
                    y=rec_df_sorted['Current Avg Qty'],
                    name='Current Order Qty',
                    marker_color='lightblue'
                ))
                
                fig.add_trace(go.Bar(
                    x=rec_df_sorted['Branch'],
                    y=rec_df_sorted['Recommended Qty'],
                    name='Recommended Order Qty',
                    marker_color='darkblue'
                ))
                
                fig.update_layout(
                    title=f"Current vs Recommended Order Quantities - {selected_outlet}",
                    xaxis_title="Branch",
                    yaxis_title="Order Quantity (bales)",
                    barmode='group',
                    height=500,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📊 Return Rate Improvement Potential")
                
                fig2 = go.Figure()
                
                fig2.add_trace(go.Bar(
                    x=rec_df_sorted['Branch'],
                    y=rec_df_sorted['Current Return Rate'],
                    name='Current Return Rate',
                    marker_color='red'
                ))
                
                fig2.add_trace(go.Bar(
                    x=rec_df_sorted['Branch'],
                    y=rec_df_sorted['Expected Return Rate'],
                    name='Expected Return Rate',
                    marker_color='green'
                ))
                
                fig2.update_layout(
                    title=f"Return Rate: Current vs Expected - {selected_outlet}",
                    xaxis_title="Branch",
                    yaxis_title="Return Rate (%)",
                    barmode='group',
                    height=500,
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
                st.subheader("📋 Export Recommendations")
                
                # Create export dataframe
                export_df = rec_df_sorted[[
                    'Branch', 'Current Avg Qty', 'Recommended Qty', 'Qty Change %',
                    'Current Return Rate', 'Expected Return Rate', 'Expected Reduction',
                    'Confidence', 'Reason'
                ]].copy()
                
                export_df.columns = [
                    'Branch', 'Current Qty (bales)', 'Recommended Qty (bales)', 'Change %',
                    'Current Return Rate %', 'Expected Return Rate %', 'Expected Reduction %',
                    'Confidence', 'Reason'
                ]
                
                # Format numbers
                export_df['Current Qty (bales)'] = export_df['Current Qty (bales)'].apply(lambda x: f"{x:.0f}")
                export_df['Recommended Qty (bales)'] = export_df['Recommended Qty (bales)'].apply(lambda x: f"{x:.0f}")
                export_df['Change %'] = export_df['Change %'].apply(lambda x: f"{x:.1f}%")
                export_df['Current Return Rate %'] = export_df['Current Return Rate %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Return Rate %'] = export_df['Expected Return Rate %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Reduction %'] = export_df['Expected Reduction %'].apply(lambda x: f"{x:.1f}%")
                export_df['Confidence'] = export_df['Confidence'].apply(lambda x: f"{x*100:.0f}%")
                
                st.dataframe(export_df, use_container_width=True)
                
                # Download button
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Recommendations as CSV",
                    data=csv,
                    file_name=f"optimal_orders_{selected_outlet}.csv",
                    mime="text/csv"
                )

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v27.0\n\nOptimal Order Recommendations!")
