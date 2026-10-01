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
    "📊 Dashboard",
    "📈 Store Analysis",
    "🤖 AI Relationship Analysis",
    "💡 Optimal Order Recommendations"
])

if 'data' not in st.session_state:
    st.session_state.data = None

def get_active_periods(monthly_data):
    """Identify active periods (continuous months with data) and gaps"""
    if not monthly_data:
        return []
    
    periods = []
    current_period = []
    
    for month in monthly_data:
        if month['sales'] != 0 or month['returns'] != 0:
            current_period.append(month)
        else:
            if current_period:
                periods.append(current_period)
                current_period = []
    
    if current_period:
        periods.append(current_period)
    
    return periods

def calculate_monthly_metrics(branch_row, numeric_cols):
    """Calculate metrics for each month"""
    weeks_per_month = 5
    monthly_metrics = []
    
    for month_num in range(1, 10):
        start_idx = (month_num - 1) * weeks_per_month * 2
        end_idx = month_num * weeks_per_month * 2
        
        month_sales = 0
        month_returns = 0
        
        for i in range(start_idx, min(end_idx, len(numeric_cols) - 1), 2):
            if i < len(numeric_cols) - 1:
                try:
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    
                    if pd.notna(net_sales_val):
                        month_sales += net_sales_val
                    if pd.notna(returns_val):
                        month_returns += returns_val
                except:
                    pass
        
        original_order = abs(month_sales) + month_returns
        if original_order > 0:
            return_rate = (month_returns / original_order) * 100
        else:
            return_rate = 0
        
        monthly_metrics.append({
            'month_num': month_num,
            'month': f"M{month_num}",
            'sales': month_sales,
            'returns': month_returns,
            'return_rate': return_rate,
            'has_data': (month_sales != 0 or month_returns != 0)
        })
    
    return monthly_metrics

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
            st.write("Go to **Dashboard** to see overall summary of all branches.")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

elif page == "📊 Dashboard":
    st.header("Overall Branch Performance Dashboard")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
            
            branch_metrics = []
            
            for branch in branches:
                branch_row = df[df['Branch'] == branch]
                
                if len(branch_row) > 0:
                    monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
                    active_periods = get_active_periods(monthly_data)
                    
                    if active_periods:
                        # Get CURRENT period (last active period)
                        current_period = active_periods[-1]
                        current_period_start = current_period[0]['month_num']
                        current_period_end = current_period[-1]['month_num']
                        
                        # Check if currently active in Month 7
                        month_7 = monthly_data[6]  # Month 7 is index 6
                        is_active_m7 = month_7['has_data']
                        
                        # Get first and last active months overall
                        first_active_month = active_periods[0][0]['month_num']
                        last_active_month = active_periods[-1][-1]['month_num']
                        
                        # Month 7 metrics (if active)
                        if is_active_m7:
                            m7_return_rate = month_7['return_rate']
                            m7_sales = month_7['sales']
                        else:
                            m7_return_rate = None
                            m7_sales = None
                        
                        # Month 6 metrics (for M6→M7 trend)
                        month_6 = monthly_data[5]  # Month 6 is index 5
                        m6_return_rate = month_6['return_rate'] if month_6['has_data'] else None
                        
                        # M6→M7 trend (if both have data)
                        if is_active_m7 and m6_return_rate is not None:
                            m6_m7_trend = "📉" if m7_return_rate < m6_return_rate else "📈" if m7_return_rate > m6_return_rate else "➡️"
                            m6_m7_change = m7_return_rate - m6_return_rate
                        else:
                            m6_m7_trend = None
                            m6_m7_change = None
                        
                        # Overall trend (first active → last active)
                        first_period_start = active_periods[0][0]
                        last_period_end = active_periods[-1][-1]
                        
                        overall_trend = "📉" if last_period_end['return_rate'] < first_period_start['return_rate'] else "📈" if last_period_end['return_rate'] > first_period_start['return_rate'] else "➡️"
                        overall_change = last_period_end['return_rate'] - first_period_start['return_rate']
                        
                        # Period info
                        if len(active_periods) > 1:
                            period_info = f"M{current_period_start}-M{current_period_end} (was M{first_active_month}-M{active_periods[-2][-1]['month_num']})"
                            has_gaps = True
                        else:
                            period_info = f"M{current_period_start}-M{current_period_end}"
                            has_gaps = False
                        
                        # Status based on Month 7 (if active) or last active month
                        if is_active_m7:
                            if m7_sales < 0:
                                status = "🔴 CRITICAL"
                                priority = 1
                            elif m7_return_rate > 30:
                                status = "🔴 HIGH"
                                priority = 2
                            elif m7_return_rate > 20:
                                status = "🟡 MODERATE"
                                priority = 3
                            elif m7_return_rate > 15:
                                status = "🟡 WATCH"
                                priority = 4
                            else:
                                status = "🟢 GOOD"
                                priority = 5
                            active_status = "Active"
                        else:
                            # Branch is delisted/inactive
                            last_return_rate = last_period_end['return_rate']
                            if last_return_rate > 30:
                                status = "🔴 DELISTED (High Returns)"
                                priority = 2
                            elif last_return_rate > 20:
                                status = "🟡 DELISTED (Moderate Returns)"
                                priority = 3
                            else:
                                status = "⚪ DELISTED"
                                priority = 6
                            active_status = "Delisted"
                            m7_return_rate = last_return_rate
                        
                        # Worsening flag (M6→M7)
                        worsening = m6_m7_change is not None and m6_m7_change > 5
                        if worsening and priority > 2:
                            priority -= 1
                        
                        branch_metrics.append({
                            'Branch': branch,
                            'Active Status': active_status,
                            'Period': period_info,
                            'Has Gaps': has_gaps,
                            'M7 Return Rate': m7_return_rate,
                            'M7 Sales': m7_sales if is_active_m7 else None,
                            'M6→M7 Trend': m6_m7_trend,
                            'M6→M7 Change': m6_m7_change,
                            'Overall Trend': overall_trend,
                            'Overall Change': overall_change,
                            'Status': status,
                            'Priority': priority,
                            'Worsening': worsening,
                            'monthly_data': monthly_data,
                            'active_periods': active_periods
                        })
            
            if branch_metrics:
                metrics_df = pd.DataFrame(branch_metrics)
                
                st.subheader("📊 Overall Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                
                active_branches = len(metrics_df[metrics_df['Active Status'] == 'Active'])
                delisted_branches = len(metrics_df[metrics_df['Active Status'] == 'Delisted'])
                
                col1.metric("Total Branches", len(metrics_df))
                col2.metric("Active (M7)", active_branches)
                col3.metric("Delisted", delisted_branches)
                col4.metric("Avg M7 Return Rate", f"{metrics_df[metrics_df['Active Status'] == 'Active']['M7 Return Rate'].mean():.1f}%")
                
                critical_count = len(metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')])
                col5.metric("Critical/High Issues", critical_count, delta=f"🔴" if critical_count > 0 else "✅")
                
                # ===== ACTIVE BRANCHES (M7) =====
                st.subheader("🟢 Active Branches (Month 7)")
                
                active_df = metrics_df[metrics_df['Active Status'] == 'Active'].sort_values('Priority')
                
                if len(active_df) > 0:
                    display_active = active_df[[
                        'Branch', 'Period', 'M7 Return Rate', 'M6→M7 Trend', 'M6→M7 Change', 'Overall Trend', 'Status'
                    ]].copy()
                    display_active['M7 Return Rate'] = display_active['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_active['M6→M7 Change'] = display_active['M6→M7 Change'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
                    display_active['Overall Change'] = active_df['Overall Change'].apply(lambda x: f"{x:+.1f}%")
                    
                    st.dataframe(display_active, use_container_width=True)
                    
                    st.info("💡 **M6→M7 Trend:** Latest month-on-month change | **Overall Trend:** First active month to last active month")
                
                # ===== CRITICAL BRANCHES =====
                critical_branches = metrics_df[metrics_df['Status'].str.contains('CRITICAL|HIGH')].sort_values('Priority')
                if len(critical_branches) > 0:
                    st.subheader("🔴 Branches Needing Immediate Attention")
                    
                    display_critical = critical_branches[[
                        'Branch', 'Active Status', 'Period', 'M7 Return Rate', 'M6→M7 Trend', 'Overall Trend', 'Status'
                    ]].copy()
                    display_critical['M7 Return Rate'] = display_critical['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(display_critical, use_container_width=True)
                
                # ===== WORSENING BRANCHES =====
                worsening_branches = metrics_df[metrics_df['Worsening'] == True].sort_values('M6→M7 Change', ascending=False)
                if len(worsening_branches) > 0:
                    st.subheader("⚠️ Branches with Worsening Return Rates (M6→M7)")
                    
                    display_worsening = worsening_branches[[
                        'Branch', 'Period', 'M7 Return Rate', 'M6→M7 Change', 'Status'
                    ]].copy()
                    display_worsening['M7 Return Rate'] = display_worsening['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    display_worsening['M6→M7 Change'] = display_worsening['M6→M7 Change'].apply(lambda x: f"{x:+.1f}%")
                    
                    st.dataframe(display_worsening, use_container_width=True)
                
                # ===== DELISTED BRANCHES =====
                delisted_df = metrics_df[metrics_df['Active Status'] == 'Delisted'].sort_values('Priority')
                if len(delisted_df) > 0:
                    st.subheader("⚪ Delisted Branches")
                    
                    display_delisted = delisted_df[[
                        'Branch', 'Period', 'M7 Return Rate', 'Overall Trend', 'Status'
                    ]].copy()
                    display_delisted['M7 Return Rate'] = display_delisted['M7 Return Rate'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(display_delisted, use_container_width=True)
                
                # ===== CHARTS =====
                st.subheader("📊 Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    fig_returns = go.Figure()
                    fig_returns.add_trace(go.Bar(
                        x=active_only['Branch'].str[:30],
                        y=active_only['M7 Return Rate'],
                        marker=dict(color=active_only['M7 Return Rate'], colorscale='RdYlGn_r', showscale=True)
                    ))
                    fig_returns.update_layout(title="Month 7 Return Rate (Active Branches)", height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig_returns, use_container_width=True)
                
                with col2:
                    fig_status = go.Figure(data=[
                        go.Pie(labels=['🟢 Active', '⚪ Delisted'],
                               values=[active_branches, delisted_branches],
                               marker=dict(colors=['green', 'gray']))
                    ])
                    st.plotly_chart(fig_status, use_container_width=True)
                
                # ===== TREND ANALYSIS =====
                st.subheader("📈 Trend Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**M6→M7 Trends (Active Branches):**")
                    active_only = metrics_df[metrics_df['Active Status'] == 'Active']
                    improving = len(active_only[active_only['M6→M7 Trend'] == '📉'])
                    worsening = len(active_only[active_only['M6→M7 Trend'] == '📈'])
                    stable = len(active_only[active_only['M6→M7 Trend'] == '➡️'])
                    
                    fig_m6m7 = go.Figure(data=[
                        go.Pie(labels=['📉 Improving', '📈 Worsening', '➡️ Stable'],
                               values=[improving, worsening, stable],
                               marker=dict(colors=['green', 'red', 'gray']))
                    ])
                    st.plotly_chart(fig_m6m7, use_container_width=True)
                
                with col2:
                    st.write("**Overall Trends (All Branches):**")
                    improving_overall = len(metrics_df[metrics_df['Overall Trend'] == '📉'])
                    worsening_overall = len(metrics_df[metrics_df['Overall Trend'] == '📈'])
                    stable_overall = len(metrics_df[metrics_df['Overall Trend'] == '➡️'])
                    
                    fig_overall = go.Figure(data=[
                        go.Pie(labels=['📉 Improving', '📈 Worsening', '➡️ Stable'],
                               values=[improving_overall, worsening_overall, stable_overall],
                               marker=dict(colors=['green', 'red', 'gray']))
                    ])
                    st.plotly_chart(fig_overall, use_container_width=True)

elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis")
    st.info("📊 Coming soon...")

elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis")
    st.info("📊 Coming soon...")

elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Recommendations")
    st.info("💡 Coming soon...")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v17.0\n\nInterval/gap detection with multi-period analysis!")
