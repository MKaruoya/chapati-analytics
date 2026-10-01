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
    
    # Filter out zero orders
    active_weeks = [w for w in weekly_data if w['order_quantity'] > 0]
    
    if not active_weeks:
        return None, None, None, "No order data"
    
    # Create bins of order quantities
    quantities = [w['order_quantity'] for w in active_weeks]
    returns = [w['return_pct'] for w in active_weeks]
    
    # Find quartiles
    q1 = np.percentile(quantities, 25)
    q2 = np.percentile(quantities, 50)  # median
    q3 = np.percentile(quantities, 75)
    
    # Calculate average return rate for each quartile
    q1_returns = [r for q, r in zip(quantities, returns) if q <= q1]
    q2_returns = [r for q, r in zip(quantities, returns) if q1 < q <= q3]
    q3_returns = [r for q, r in zip(quantities, returns) if q > q3]
    
    avg_q1_return = np.mean(q1_returns) if q1_returns else 0
    avg_q2_return = np.mean(q2_returns) if q2_returns else 0
    avg_q3_return = np.mean(q3_returns) if q3_returns else 0
    
    # Find which quartile has lowest return rate
    quartile_returns = {
        'Q1 (Low)': (q1, avg_q1_return),
        'Q2 (Medium)': (q2, avg_q2_return),
        'Q3 (High)': (q3, avg_q3_return)
    }
    
    best_quartile = min(quartile_returns.items(), key=lambda x: x[1][1])
    optimal_qty = best_quartile[1][0]
    optimal_return_rate = best_quartile[1][1]
    
    # Calculate correlation
    corr = np.corrcoef(quantities, returns)[0, 1]
    
    return optimal_qty, optimal_return_rate, corr, best_quartile[0]

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
            st.write("Go to **AI Relationship Analysis** to analyze individual branches.")
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
    st.header("🤖 AI Relationship Analysis: Individual Branch Weekly Analysis")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not valid_branches:
            st.error("❌ No branches found in data!")
        else:
            st.subheader("🏪 Select Branch to Analyze")
            selected_branch = st.selectbox("Choose a branch:", sorted(valid_branches), key="ai_branch")
            
            branch_row = df[df['Branch'] == selected_branch]
            
            if len(branch_row) > 0:
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                
                if weekly_data:
                    weekly_df = pd.DataFrame(weekly_data)
                    
                    st.info(f"📍 Analyzing **{selected_branch}** - {len(weekly_data)} weeks of data")
                    
                    # Calculate metrics
                    active_weeks = weekly_df[weekly_df['order_quantity'] > 0]
                    optimal_qty, optimal_return_rate, corr, best_quartile = find_optimal_quantity(weekly_data)
                    
                    st.subheader("📊 Weekly Correlation Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Correlation:**")
                        st.metric("Order Qty vs Return Rate", f"{corr:.3f}")
                        
                        if corr > 0.3:
                            st.error("🔴 Positive: Larger orders = Higher returns")
                        elif corr < -0.3:
                            st.success("🟢 Negative: Larger orders = Lower returns")
                        else:
                            st.info("🟡 Weak: Independent relationship")
                    
                    with col2:
                        st.write("**Weekly Statistics:**")
                        st.write(f"Total weeks: {len(weekly_df)}")
                        st.write(f"Active weeks: {len(active_weeks)}")
                        st.write(f"Avg order: {active_weeks['order_quantity'].mean():.0f} bales")
                        st.write(f"Avg return rate: {active_weeks['return_pct'].mean():.1f}%")
                    
                    with col3:
                        st.write("**Order Range:**")
                        st.write(f"Min: {active_weeks['order_quantity'].min():.0f} bales")
                        st.write(f"Max: {active_weeks['order_quantity'].max():.0f} bales")
                        st.write(f"Median: {active_weeks['order_quantity'].median():.0f} bales")
                    
                    st.subheader("📈 Weekly Order Quantity vs Return Rate")
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=weekly_df['order_quantity'],
                        y=weekly_df['return_pct'],
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=weekly_df['return_pct'],
                            colorscale='RdYlGn_r',
                            showscale=True,
                            colorbar=dict(title="Return %")
                        ),
                        text=[f"Week {w}<br>Order: {q:.0f} bales<br>Return: {r:.1f}%" 
                              for w, q, r in zip(weekly_df['week'], weekly_df['order_quantity'], weekly_df['return_pct'])],
                        hovertemplate='%{text}<extra></extra>'
                    ))
                    
                    # Add trend line
                    if len(active_weeks) > 1:
                        z = np.polyfit(active_weeks['order_quantity'], active_weeks['return_pct'], 1)
                        p = np.poly1d(z)
                        x_trend = np.linspace(active_weeks['order_quantity'].min(), active_weeks['order_quantity'].max(), 100)
                        fig.add_trace(go.Scatter(
                            x=x_trend,
                            y=p(x_trend),
                            mode='lines',
                            name='Trend',
                            line=dict(color='red', dash='dash', width=2)
                        ))
                    
                    fig.update_layout(
                        title=f"Weekly Order Quantity vs Return Rate - {selected_branch}",
                        xaxis_title="Weekly Order Quantity (bales)",
                        yaxis_title="Weekly Return Rate (%)",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("🎯 Optimal Order Quantity Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Current Pattern:**")
                        st.metric("Avg Weekly Order", f"{active_weeks['order_quantity'].mean():.0f} bales")
                        st.metric("Avg Return Rate", f"{active_weeks['return_pct'].mean():.1f}%")
                    
                    with col2:
                        st.write("**Optimal Pattern:**")
                        st.metric("Recommended Order", f"{optimal_qty:.0f} bales")
                        st.metric("Expected Return Rate", f"{optimal_return_rate:.1f}%")
                    
                    with col3:
                        st.write("**Improvement:**")
                        current_avg_return = active_weeks['return_pct'].mean()
                        improvement = current_avg_return - optimal_return_rate
                        improvement_pct = (improvement / current_avg_return * 100) if current_avg_return > 0 else 0
                        st.metric("Return Reduction", f"{improvement:.1f}%")
                        st.metric("Improvement %", f"{improvement_pct:.1f}%")
                    
                    st.write(f"**Best Quartile:** {best_quartile}")
                    
                    st.subheader("📊 Weekly Data Table")
                    
                    display_weekly = weekly_df.copy()
                    display_weekly['order_quantity'] = display_weekly['order_quantity'].apply(lambda x: f"{x:.0f}")
                    display_weekly['return_pct'] = display_weekly['return_pct'].apply(lambda x: f"{x:.1f}%")
                    display_weekly['net_sales'] = display_weekly['net_sales'].apply(lambda x: f"{x:.0f}")
                    display_weekly['returns'] = display_weekly['returns'].apply(lambda x: f"{x:.0f}")
                    
                    st.dataframe(display_weekly, use_container_width=True)

elif page == "💡 Optimal Order Recommendations":
    st.header("💡 Optimal Order Recommendations")
    st.info("💡 Coming soon - will use individual branch analysis...")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v29.0\n\nIndividual Branch Weekly Analysis!")
