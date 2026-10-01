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
            st.write("Go to **AI Relationship Analysis** to see weekly order quantity vs returns relationships.")
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
    st.header("🤖 AI Relationship Analysis: Weekly Order Quantities vs Returns")
    
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
            st.subheader("🏪 Select Outlet to Analyze")
            selected_outlet = st.selectbox("Choose an outlet:", outlet_names, key="ai_outlet")
            
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
            
            st.info(f"📍 Analyzing **{selected_outlet}** - Found {len(outlet_branches)} branches")
            
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            
            # Collect all weekly data for the outlet
            all_weekly_data = []
            branch_weekly_summary = []
            
            for branch in outlet_branches:
                branch_row = df[df['Branch'] == branch]
                if len(branch_row) > 0:
                    weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                    
                    if weekly_data:
                        # Add branch name to each week
                        for week in weekly_data:
                            week['branch'] = branch
                            all_weekly_data.append(week)
                        
                        # Calculate branch summary
                        avg_qty = np.mean([w['order_quantity'] for w in weekly_data if w['order_quantity'] > 0])
                        avg_return = np.mean([w['return_pct'] for w in weekly_data])
                        
                        branch_weekly_summary.append({
                            'Branch': branch,
                            'Avg Weekly Qty': avg_qty,
                            'Avg Weekly Return %': avg_return,
                            'Total Weeks': len(weekly_data)
                        })
            
            if all_weekly_data:
                weekly_df = pd.DataFrame(all_weekly_data)
                
                st.subheader("📊 Weekly Correlation Analysis")
                
                # Calculate correlation
                corr_qty_returns = weekly_df['order_quantity'].corr(weekly_df['return_pct'])
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Weekly Order Quantity vs Weekly Return Rate**")
                    st.metric("Correlation", f"{corr_qty_returns:.3f}")
                    
                    if corr_qty_returns > 0.5:
                        st.error("🔴 Strong positive: Larger weekly orders = Higher returns")
                        st.write("**Insight:** Quality or handling issues increase with order size")
                    elif corr_qty_returns > 0.2:
                        st.warning("🟡 Moderate positive: Some relationship")
                    elif corr_qty_returns < -0.2:
                        st.success("🟢 Negative: Larger weekly orders = Lower returns (good!)")
                        st.write("**Insight:** Larger orders are handled better")
                    else:
                        st.info("🟡 Weak: Weekly order size independent of returns")
                
                with col2:
                    st.write("**Statistics:**")
                    st.write(f"Total weeks analyzed: {len(weekly_df)}")
                    st.write(f"Avg weekly order: {weekly_df['order_quantity'].mean():.0f} bales")
                    st.write(f"Avg weekly return rate: {weekly_df['return_pct'].mean():.1f}%")
                    st.write(f"Min weekly order: {weekly_df[weekly_df['order_quantity'] > 0]['order_quantity'].min():.0f} bales")
                    st.write(f"Max weekly order: {weekly_df['order_quantity'].max():.0f} bales")
                
                st.subheader("📈 Weekly Order Quantity vs Return Rate Scatter Plot")
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=weekly_df['order_quantity'],
                    y=weekly_df['return_pct'],
                    mode='markers',
                    marker=dict(size=8, color=weekly_df['return_pct'], colorscale='RdYlGn_r'),
                    text=weekly_df['branch'],
                    hovertemplate='<b>%{text}</b><br>Weekly Order: %{x:.0f} bales<br>Return Rate: %{y:.1f}%<extra></extra>'
                ))
                
                # Add trend line
                if len(weekly_df) > 1:
                    z = np.polyfit(weekly_df['order_quantity'], weekly_df['return_pct'], 1)
                    p = np.poly1d(z)
                    x_trend = np.linspace(weekly_df['order_quantity'].min(), weekly_df['order_quantity'].max(), 100)
                    fig.add_trace(go.Scatter(
                        x=x_trend,
                        y=p(x_trend),
                        mode='lines',
                        name='Trend',
                        line=dict(color='red', dash='dash')
                    ))
                
                fig.update_layout(
                    title=f"Weekly Order Quantity vs Return Rate - {selected_outlet}",
                    xaxis_title="Weekly Order Quantity (bales)",
                    yaxis_title="Weekly Return Rate (%)",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.subheader("📊 Branch Summary - Weekly Averages")
                
                summary_df = pd.DataFrame(branch_weekly_summary)
                display_summary = summary_df.copy()
                display_summary['Avg Weekly Qty'] = display_summary['Avg Weekly Qty'].apply(lambda x: f"{x:.0f} bales")
                display_summary['Avg Weekly Return %'] = display_summary['Avg Weekly Return %'].apply(lambda x: f"{x:.1f}%")
                
                st.dataframe(display_summary, use_container_width=True)
                
                st.subheader("🎯 Key Findings")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Highest Return Rate (Weekly):**")
                    worst_week = weekly_df.loc[weekly_df['return_pct'].idxmax()]
                    st.write(f"🔴 {worst_week['branch']}")
                    st.write(f"Order: {worst_week['order_quantity']:.0f} bales")
                    st.write(f"Return Rate: {worst_week['return_pct']:.1f}%")
                
                with col2:
                    st.write("**Lowest Return Rate (Weekly):**")
                    best_week = weekly_df.loc[weekly_df['return_pct'].idxmin()]
                    st.write(f"🟢 {best_week['branch']}")
                    st.write(f"Order: {best_week['order_quantity']:.0f} bales")
                    st.write(f"Return Rate: {best_week['return_pct']:.1f}%")
                
                with col3:
                    st.write("**Optimal Order Range:**")
                    # Find quartiles
                    q1 = weekly_df[weekly_df['order_quantity'] > 0]['order_quantity'].quantile(0.25)
                    q3 = weekly_df[weekly_df['order_quantity'] > 0]['order_quantity'].quantile(0.75)
                    st.write(f"Q1 (25%): {q1:.0f} bales")
                    st.write(f"Q3 (75%): {q3:.0f} bales")
                    st.write(f"Median: {weekly_df[weekly_df['order_quantity'] > 0]['order_quantity'].median():.0f} bales")

elif page == "💡 Optimal Order Recommendations":
    st.header("💡 Optimal Order Recommendations")
    st.info("💡 Coming soon - will use weekly analysis insights...")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v28.0\n\nWeekly Order Analysis!")
