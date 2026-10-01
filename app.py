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

def calculate_weekly_metrics(branch_row, numeric_cols):
    """Calculate weekly order quantities and returns"""
    weekly_data = []
    
    for i in range(0, len(numeric_cols) - 1, 2):
        net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
        returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
        
        if pd.notna(net_sales_val) or pd.notna(returns_val):
            net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
            returns_val = returns_val if pd.notna(returns_val) else 0
            
            original_order = abs(net_sales_val) + returns_val
            return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
            
            weekly_data.append({
                'week': len(weekly_data) + 1,
                'order_quantity': original_order,
                'net_sales': net_sales_val,
                'returns': returns_val,
                'return_pct': return_pct
            })
    
    return weekly_data

def find_optimal_quantity(weekly_data):
    """Find optimal order quantity for a branch"""
    
    active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
    
    if not active_weeks:
        return None, None, None, "No order data", 0
    
    quantities = [w['order_quantity'] for w in active_weeks]
    returns = [w['return_pct'] for w in active_weeks]
    
    q1 = np.percentile(quantities, 25)
    q2 = np.percentile(quantities, 50)
    q3 = np.percentile(quantities, 75)
    
    q1_returns = [r for q, r in zip(quantities, returns) if q <= q1]
    q2_returns = [r for q, r in zip(quantities, returns) if q1 < q <= q3]
    q3_returns = [r for q, r in zip(quantities, returns) if q > q3]
    
    avg_q1_return = np.mean(q1_returns) if q1_returns else 0
    avg_q2_return = np.mean(q2_returns) if q2_returns else 0
    avg_q3_return = np.mean(q3_returns) if q3_returns else 0
    
    quartile_returns = {
        'Q1 (Low)': (q1, avg_q1_return),
        'Q2 (Medium)': (q2, avg_q2_return),
        'Q3 (High)': (q3, avg_q3_return)
    }
    
    best_quartile = min(quartile_returns.items(), key=lambda x: x[1][1])
    optimal_qty = best_quartile[1][0]
    optimal_return_rate = best_quartile[1][1]
    
    corr = np.corrcoef(quantities, returns)[0, 1]
    
    # Calculate confidence based on data consistency
    current_avg_return = np.mean(returns)
    confidence = min(len(active_weeks) / 35, 1.0)  # 35 weeks is full period
    
    return optimal_qty, optimal_return_rate, corr, best_quartile[0], confidence

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
                    weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                    
                    if weekly_data:
                        active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
                        
                        if active_weeks:
                            current_avg_qty = np.mean([w['order_quantity'] for w in active_weeks])
                            current_avg_return = np.mean([w['return_pct'] for w in active_weeks])
                            
                            optimal_qty, optimal_return_rate, corr, best_quartile, confidence = find_optimal_quantity(weekly_data)
                            
                            if optimal_qty:
                                qty_change_pct = ((optimal_qty - current_avg_qty) / current_avg_qty * 100)
                                expected_improvement = current_avg_return - optimal_return_rate
                                
                                # Determine status
                                if current_avg_return > 25:
                                    status = "🔴 CRITICAL"
                                    priority = 1
                                elif current_avg_return > 20:
                                    status = "🔴 HIGH"
                                    priority = 2
                                elif current_avg_return > 15:
                                    status = "🟡 MODERATE"
                                    priority = 3
                                else:
                                    status = "🟢 GOOD"
                                    priority = 4
                                
                                recommendations.append({
                                    'Branch': branch,
                                    'Current Qty': current_avg_qty,
                                    'Current Return %': current_avg_return,
                                    'Recommended Qty': optimal_qty,
                                    'Expected Return %': optimal_return_rate,
                                    'Qty Change %': qty_change_pct,
                                    'Expected Improvement': expected_improvement,
                                    'Confidence': confidence,
                                    'Status': status,
                                    'Priority': priority,
                                    'Correlation': corr,
                                    'Best Quartile': best_quartile
                                })
            
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                rec_df = rec_df.sort_values('Priority')
                
                st.subheader("📊 Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Branches", len(rec_df))
                col2.metric("Avg Current Qty", f"{rec_df['Current Qty'].mean():.0f} bales")
                col3.metric("Avg Recommended Qty", f"{rec_df['Recommended Qty'].mean():.0f} bales")
                col4.metric("Avg Current Return %", f"{rec_df['Current Return %'].mean():.1f}%")
                col5.metric("Avg Expected Return %", f"{rec_df['Expected Return %'].mean():.1f}%")
                
                st.subheader("🎯 Recommendations by Priority")
                
                # Critical branches first
                critical = rec_df[rec_df['Priority'] <= 2]
                if len(critical) > 0:
                    st.write("### 🔴 Critical & High Priority Branches")
                    for idx, row in critical.iterrows():
                        with st.expander(f"{row['Status']} {row['Branch']} | Current: {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}% returns)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Current Pattern:**")
                                st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Current Return %']:.1f}%")
                            
                            with col2:
                                st.write("**Recommended Pattern:**")
                                st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Expected Return %']:.1f}%")
                            
                            with col3:
                                st.write("**Impact:**")
                                if row['Qty Change %'] < 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", delta="Reduce")
                                elif row['Qty Change %'] > 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:+.1f}%", delta="Increase")
                                else:
                                    st.metric("Qty Change", "0%", delta="Maintain")
                                st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%")
                            
                            st.write("---")
                            st.write(f"**Confidence:** {row['Confidence']*100:.0f}%")
                            st.write(f"**Correlation (Qty vs Returns):** {row['Correlation']:.3f}")
                            st.write(f"**Best Quartile:** {row['Best Quartile']}")
                
                # Moderate branches
                moderate = rec_df[rec_df['Priority'] == 3]
                if len(moderate) > 0:
                    st.write("### 🟡 Moderate Priority Branches")
                    for idx, row in moderate.iterrows():
                        with st.expander(f"{row['Status']} {row['Branch']} | Current: {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}% returns)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Current Pattern:**")
                                st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Current Return %']:.1f}%")
                            
                            with col2:
                                st.write("**Recommended Pattern:**")
                                st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Expected Return %']:.1f}%")
                            
                            with col3:
                                st.write("**Impact:**")
                                if row['Qty Change %'] < 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", delta="Reduce")
                                elif row['Qty Change %'] > 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:+.1f}%", delta="Increase")
                                else:
                                    st.metric("Qty Change", "0%", delta="Maintain")
                                st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%")
                            
                            st.write("---")
                            st.write(f"**Confidence:** {row['Confidence']*100:.0f}%")
                
                # Good branches
                good = rec_df[rec_df['Priority'] >= 4]
                if len(good) > 0:
                    st.write("### 🟢 Good Performing Branches")
                    for idx, row in good.iterrows():
                        with st.expander(f"{row['Status']} {row['Branch']} | Current: {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}% returns)"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Current Pattern:**")
                                st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Current Return %']:.1f}%")
                            
                            with col2:
                                st.write("**Recommended Pattern:**")
                                st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales")
                                st.metric("Return Rate", f"{row['Expected Return %']:.1f}%")
                            
                            with col3:
                                st.write("**Impact:**")
                                if row['Qty Change %'] < 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", delta="Reduce")
                                elif row['Qty Change %'] > 0:
                                    st.metric("Qty Change", f"{row['Qty Change %']:+.1f}%", delta="Increase")
                                else:
                                    st.metric("Qty Change", "0%", delta="Maintain")
                                st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%")
                
                st.subheader("📈 Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Current Qty'],
                        name='Current Weekly Order',
                        marker_color='lightblue'
                    ))
                    
                    fig.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Recommended Qty'],
                        name='Recommended Weekly Order',
                        marker_color='darkblue'
                    ))
                    
                    fig.update_layout(
                        title=f"Current vs Recommended Weekly Order Quantities - {selected_outlet}",
                        xaxis_title="Branch",
                        yaxis_title="Order Quantity (bales)",
                        barmode='group',
                        height=500,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig2 = go.Figure()
                    
                    fig2.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Current Return %'],
                        name='Current Return Rate',
                        marker_color='red'
                    ))
                    
                    fig2.add_trace(go.Bar(
                        x=rec_df['Branch'],
                        y=rec_df['Expected Return %'],
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
                
                export_df = rec_df[[
                    'Branch', 'Current Qty', 'Recommended Qty', 'Qty Change %',
                    'Current Return %', 'Expected Return %', 'Expected Improvement',
                    'Confidence', 'Status'
                ]].copy()
                
                export_df.columns = [
                    'Branch', 'Current Weekly Qty (bales)', 'Recommended Weekly Qty (bales)', 'Change %',
                    'Current Return Rate %', 'Expected Return Rate %', 'Expected Improvement %',
                    'Confidence', 'Status'
                ]
                
                export_df['Current Weekly Qty (bales)'] = export_df['Current Weekly Qty (bales)'].apply(lambda x: f"{x:.0f}")
                export_df['Recommended Weekly Qty (bales)'] = export_df['Recommended Weekly Qty (bales)'].apply(lambda x: f"{x:.0f}")
                export_df['Change %'] = export_df['Change %'].apply(lambda x: f"{x:.1f}%")
                export_df['Current Return Rate %'] = export_df['Current Return Rate %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Return Rate %'] = export_df['Expected Return Rate %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Improvement %'] = export_df['Expected Improvement %'].apply(lambda x: f"{x:.1f}%")
                export_df['Confidence'] = export_df['Confidence'].apply(lambda x: f"{x*100:.0f}%")
                
                st.dataframe(export_df, use_container_width=True)
                
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Recommendations as CSV",
                    data=csv,
                    file_name=f"optimal_weekly_orders_{selected_outlet}.csv",
                    mime="text/csv"
                )

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v30.0\n\nOptimal Order Recommendations Complete!")
