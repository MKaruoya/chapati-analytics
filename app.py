import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import io

st.set_page_config(page_title="Chapati Analytics", layout="wide")
st.title("🍞 Chapati Data Analysis Agent")

st.sidebar.header("📊 Navigation")
page = st.sidebar.radio("Select Analysis", [
    "📤 Upload Data",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

# ============================================================================
# PAGE 1: UPLOAD DATA
# ============================================================================
if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data (CSV)")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read data starting from row 4 (skip header rows 1-3)
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            
            st.session_state.data = df
            
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(20))
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            col3.metric("Data Shape", f"{len(df)} x {len(df.columns)}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# PAGE 2: STORE ANALYSIS
# ============================================================================
elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis - Week by Week Performance")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        # Get first column name
        first_col = df.columns[0]
        
        # Get unique branch names (contain "-" and not product names)
        all_names = df[first_col].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            # Get the branch row
            branch_row = df[df[first_col] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Performance Analysis for {selected_branch}")
                
                # Get all numeric columns (skip first column which has names)
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                
                # Process pairs: every 2 columns = 1 week (Net Sales, Returns)
                weekly_data = []
                week_num = 1
                
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_col = numeric_cols[i]
                    returns_col = numeric_cols[i + 1]
                    
                    net_sales_val = pd.to_numeric(branch_row[net_sales_col].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[returns_col].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val) or pd.notna(returns_val):
                        net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
                        returns_val = returns_val if pd.notna(returns_val) else 0
                        return_pct = (returns_val / (net_sales_val + returns_val) * 100) if (net_sales_val + returns_val) > 0 else 0
                        
                        weekly_data.append({
                            'Week': f"W{week_num}",
                            'Net Sales': f"{net_sales_val:.0f}",
                            'Returns': f"{returns_val:.0f}",
                            'Return %': f"{return_pct:.1f}%"
                        })
                    
                    week_num += 1
                
                if weekly_data:
                    st.subheader("📅 Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    st.dataframe(weekly_df, use_container_width=True)
                    
                    # Calculate totals
                    total_net_sales = sum([float(row['Net Sales']) for row in weekly_data])
                    total_returns = sum([float(row['Returns']) for row in weekly_data])
                    total_return_pct = (total_returns / (total_net_sales + total_returns) * 100) if (total_net_sales + total_returns) > 0 else 0
                    
                    st.subheader("📊 Overall Summary")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Net Sales", f"{total_net_sales:.0f} bales")
                    col2.metric("Total Returns", f"{total_returns:.0f} bales")
                    col3.metric("Return Rate", f"{total_return_pct:.1f}%")
                    
                    # Charts
                    st.subheader("📈 Weekly Trends")
                    
                    weekly_df_plot = weekly_df.copy()
                    weekly_df_plot['Net Sales'] = pd.to_numeric(weekly_df_plot['Net Sales'])
                    weekly_df_plot['Returns'] = pd.to_numeric(weekly_df_plot['Returns'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Net Sales'], name='Net Sales', marker_color='green'))
                    fig.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Returns'], name='Returns', marker_color='red'))
                    fig.update_layout(title="Weekly Net Sales vs Returns", barmode='group', height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Line chart for trend
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(x=weekly_df_plot['Week'], y=weekly_df_plot['Net Sales'], name='Net Sales', mode='lines+markers', marker=dict(size=8)))
                    fig2.add_trace(go.Scatter(x=weekly_df_plot['Week'], y=weekly_df_plot['Returns'], name='Returns', mode='lines+markers', marker=dict(size=8)))
                    fig2.update_layout(title="Weekly Trend", height=400)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.warning("⚠️ No data found for this branch")
            else:
                st.error(f"❌ No data found for {selected_branch}")

# ============================================================================
# PAGE 3: AI RELATIONSHIP ANALYSIS
# ============================================================================
elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis - Quantity, Interval & Returns")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("📊 Analyzing relationships between order quantities, intervals, and returns...")
        
        df = st.session_state.data.copy()
        first_col = df.columns[0]
        all_names = df[first_col].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if branches:
            selected_branch = st.selectbox("Select Branch for Analysis", sorted(branches))
            branch_row = df[df[first_col] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Relationship Analysis for {selected_branch}")
                
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                
                # Extract weekly data
                weekly_net_sales = []
                weekly_returns = []
                
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        weekly_net_sales.append(net_sales_val)
                    if pd.notna(returns_val):
                        weekly_returns.append(returns_val)
                
                if weekly_net_sales and weekly_returns:
                    # Calculate statistics
                    avg_net_sales = np.mean(weekly_net_sales)
                    avg_returns = np.mean(weekly_returns)
                    std_net_sales = np.std(weekly_net_sales)
                    std_returns = np.std(weekly_returns)
                    
                    st.subheader("📊 Key Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Avg Weekly Net Sales", f"{avg_net_sales:.0f} bales")
                    col2.metric("Avg Weekly Returns", f"{avg_returns:.0f} bales")
                    col3.metric("Sales Variability", f"{std_net_sales:.0f} bales")
                    col4.metric("Returns Variability", f"{std_returns:.0f} bales")
                    
                    # Correlation
                    correlation = np.corrcoef(weekly_net_sales, weekly_returns)[0, 1]
                    
                    st.subheader("🔍 Relationship Insights")
                    
                    if correlation > 0.7:
                        st.warning(f"🔴 **STRONG POSITIVE CORRELATION ({correlation:.2f})**: Higher net sales lead to higher returns. This suggests quality or handling issues.")
                    elif correlation > 0.3:
                        st.info(f"🟡 **MODERATE POSITIVE CORRELATION ({correlation:.2f})**: Some relationship between net sales and returns.")
                    elif correlation > -0.3:
                        st.success(f"🟢 **WEAK/NO CORRELATION ({correlation:.2f})**: Net sales and returns are independent.")
                    else:
                        st.success(f"🟢 **NEGATIVE CORRELATION ({correlation:.2f})**: Higher net sales actually lead to lower returns (good sign!).")
                    
                    # Trend analysis
                    st.subheader("📈 Trend Analysis")
                    
                    if len(weekly_net_sales) > 1:
                        sales_trend = "Increasing" if weekly_net_sales[-1] > weekly_net_sales[0] else "Decreasing" if weekly_net_sales[-1] < weekly_net_sales[0] else "Stable"
                        returns_trend = "Increasing" if weekly_returns[-1] > weekly_returns[0] else "Decreasing" if weekly_returns[-1] < weekly_returns[0] else "Stable"
                        
                        st.write(f"**Net Sales Trend:** {sales_trend}")
                        st.write(f"**Returns Trend:** {returns_trend}")

# ============================================================================
# PAGE 4: OPTIMAL ORDER RECOMMENDATIONS
# ============================================================================
elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Pattern Recommendations")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        st.info("💡 Generating recommendations based on order patterns...")
        
        df = st.session_state.data.copy()
        first_col = df.columns[0]
        all_names = df[first_col].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if branches:
            selected_branch = st.selectbox("Select Branch for Recommendations", sorted(branches))
            branch_row = df[df[first_col] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Recommendations for {selected_branch}")
                
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                
                # Extract weekly data
                weekly_net_sales = []
                weekly_returns = []
                
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        weekly_net_sales.append(net_sales_val)
                    if pd.notna(returns_val):
                        weekly_returns.append(returns_val)
                
                if weekly_net_sales and weekly_returns:
                    avg_net_sales = np.mean(weekly_net_sales)
                    avg_returns = np.mean(weekly_returns)
                    return_rate = (avg_returns / (avg_net_sales + avg_returns) * 100) if (avg_net_sales + avg_returns) > 0 else 0
                    
                    st.subheader("📋 Current Pattern")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Avg Weekly Net Sales", f"{avg_net_sales:.0f} bales")
                    col2.metric("Avg Weekly Returns", f"{avg_returns:.0f} bales")
                    col3.metric("Return Rate", f"{return_rate:.1f}%")
                    
                    st.subheader("✅ Recommendations")
                    
                    if return_rate > 20:
                        st.error("🔴 **CRITICAL - HIGH RETURN RATE**")
                        st.write("- Reduce order quantities by 20-25%")
                        st.write("- Investigate quality and handling issues")
                        st.write("- Increase order frequency for fresher stock")
                    elif return_rate > 15:
                        st.warning("🟡 **HIGH RETURN RATE**")
                        st.write("- Reduce order quantities by 10-15%")
                        st.write("- Monitor quality closely")
                        st.write("- Consider more frequent orders")
                    elif return_rate > 10:
                        st.warning("🟡 **MODERATE RETURN RATE**")
                        st.write("- Maintain current quantities")
                        st.write("- Monitor returns trend")
                    else:
                        st.success("🟢 **EXCELLENT PERFORMANCE**")
                        st.write("- Consider increasing order quantities by 10-15%")
                        st.write("- Maintain current practices")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v12.1\n\nWorking with Net Sales (returns already deducted).")
