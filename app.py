import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import io
import re

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
if 'headers' not in st.session_state:
    st.session_state.headers = None

# ============================================================================
# PAGE 1: UPLOAD DATA
# ============================================================================
if page == "📤 Upload Data":
    st.header("Upload Chapati Order Data (CSV)")
    
    st.info("""
    📋 **Expected Format:**
    - CSV file with multi-row headers
    - Data starts from row 4
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            # Read the entire file as bytes
            file_content = uploaded_file.read()
            
            # Read header rows
            header_rows = pd.read_csv(io.BytesIO(file_content), header=None, nrows=3)
            
            # Read data starting from row 4 (index 3)
            df = pd.read_csv(io.BytesIO(file_content), header=3)
            df.columns = df.columns.str.strip()
            
            st.session_state.data = df
            st.session_state.headers = header_rows
            
            st.success("✅ Data uploaded successfully!")
            
            st.subheader("Header Structure")
            st.write("**Row 2 (Months & Metrics):**")
            st.write(header_rows.iloc[1].tolist()[:25])
            st.write("**Row 3 (Weeks):**")
            st.write(header_rows.iloc[2].tolist()[:25])
            
            st.subheader("Data Preview")
            st.dataframe(df.head(20))
            
            st.subheader("Data Summary")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Rows", len(df))
            col2.metric("Total Columns", len(df.columns))
            col3.metric("Data Shape", f"{len(df)} x {len(df.columns)}")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.write(traceback.format_exc())

# ============================================================================
# PAGE 2: STORE ANALYSIS
# ============================================================================
elif page == "📈 Store Analysis":
    st.header("Store-Level Analysis - Week by Week & Month by Month")
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
    else:
        df = st.session_state.data.copy()
        headers = st.session_state.headers
        
        # Get first column name (contains customer/product names)
        first_col = df.columns[0]
        
        # Get unique customer/branch names
        all_names = df[first_col].dropna().unique()
        
        # Filter for branch-level entries
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if not branches:
            st.warning("⚠️ No branches found in data")
        else:
            selected_branch = st.selectbox("Select Branch", sorted(branches))
            
            # Get the branch row (exact match)
            branch_row = df[df[first_col] == selected_branch]
            
            if len(branch_row) > 0:
                st.subheader(f"Performance Analysis for {selected_branch}")
                
                # Extract header information
                months_metrics_row = headers.iloc[1].tolist()
                weeks_row = headers.iloc[2].tolist()
                
                # Parse the structure
                month_weeks = {}
                current_month = None
                
                for col_idx in range(1, len(df.columns)):  # Skip first column (names)
                    month_metric = months_metrics_row[col_idx] if col_idx < len(months_metrics_row) else None
                    week = weeks_row[col_idx] if col_idx < len(weeks_row) else None
                    
                    # Extract month from the month_metric string
                    if pd.notna(month_metric) and month_metric != '' and month_metric != 'NaN':
                        # Check if it contains "Sum of"
                        if 'Sum of' in str(month_metric):
                            # Extract month and metric type
                            match = re.search(r'(\d{2}\s\w+)\s(Sum of.*)', str(month_metric))
                            if match:
                                current_month = match.group(1)
                                metric_type = match.group(2)
                        else:
                            # Just a month name
                            current_month = month_metric
                    
                    # Create week key if we have month and week
                    if current_month and pd.notna(week) and week != '' and week != 'NaN':
                        week_key = f"{current_month} - W{week}"
                        if week_key not in month_weeks:
                            month_weeks[week_key] = {'sales_col': None, 'returns_col': None}
                        
                        # Determine if this is Sales or Returns
                        if 'Returns' in str(month_metric):
                            month_weeks[week_key]['returns_col'] = df.columns[col_idx]
                        elif 'Sales' in str(month_metric):
                            month_weeks[week_key]['sales_col'] = df.columns[col_idx]
                
                # Build weekly performance table
                weekly_data = []
                for week_key, cols in sorted(month_weeks.items()):
                    if cols['sales_col'] and cols['returns_col']:
                        sales_val = pd.to_numeric(branch_row[cols['sales_col']].values[0], errors='coerce')
                        returns_val = pd.to_numeric(branch_row[cols['returns_col']].values[0], errors='coerce')
                        
                        if pd.notna(sales_val) or pd.notna(returns_val):
                            sales_val = sales_val if pd.notna(sales_val) else 0
                            returns_val = returns_val if pd.notna(returns_val) else 0
                            return_pct = (returns_val / sales_val * 100) if sales_val > 0 else 0
                            
                            weekly_data.append({
                                'Week': week_key,
                                'Sales': f"{sales_val:.0f}",
                                'Returns': f"{returns_val:.0f}",
                                'Net': f"{sales_val - returns_val:.0f}",
                                'Return %': f"{return_pct:.1f}%"
                            })
                
                if weekly_data:
                    st.subheader("📅 Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    st.dataframe(weekly_df, use_container_width=True)
                    
                    # Monthly summary
                    st.subheader("📊 Monthly Summary")
                    monthly_summary = {}
                    
                    for week_key, cols in month_weeks.items():
                        month = week_key.split(' - ')[0]
                        if month not in monthly_summary:
                            monthly_summary[month] = {'sales': 0, 'returns': 0}
                        
                        if cols['sales_col'] and cols['returns_col']:
                            sales_val = pd.to_numeric(branch_row[cols['sales_col']].values[0], errors='coerce')
                            returns_val = pd.to_numeric(branch_row[cols['returns_col']].values[0], errors='coerce')
                            
                            if pd.notna(sales_val):
                                monthly_summary[month]['sales'] += sales_val
                            if pd.notna(returns_val):
                                monthly_summary[month]['returns'] += returns_val
                    
                    monthly_data = []
                    for month, values in sorted(monthly_summary.items()):
                        sales = values['sales']
                        returns = values['returns']
                        return_pct = (returns / sales * 100) if sales > 0 else 0
                        
                        monthly_data.append({
                            'Month': month,
                            'Sales': f"{sales:.0f}",
                            'Returns': f"{returns:.0f}",
                            'Net': f"{sales - returns:.0f}",
                            'Return %': f"{return_pct:.1f}%"
                        })
                    
                    monthly_df = pd.DataFrame(monthly_data)
                    st.dataframe(monthly_df, use_container_width=True)
                    
                    # Charts
                    st.subheader("📈 Trends")
                    
                    # Convert for plotting
                    weekly_df_plot = weekly_df.copy()
                    weekly_df_plot['Sales'] = pd.to_numeric(weekly_df_plot['Sales'])
                    weekly_df_plot['Returns'] = pd.to_numeric(weekly_df_plot['Returns'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Sales'], name='Sales', marker_color='green'))
                    fig.add_trace(go.Bar(x=weekly_df_plot['Week'], y=weekly_df_plot['Returns'], name='Returns', marker_color='red'))
                    fig.update_layout(title="Weekly Sales vs Returns", barmode='group', height=400, xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ No data found for this branch")
            else:
                st.error(f"❌ No data found for {selected_branch}")

# ============================================================================
# PAGE 3: AI RELATIONSHIP ANALYSIS
# ============================================================================
elif page == "🤖 AI Relationship Analysis":
    st.header("AI: Relationship Analysis - Quantity, Interval & Returns")
    st.info("📊 Analysis features coming soon.")

# ============================================================================
# PAGE 4: OPTIMAL ORDER RECOMMENDATIONS
# ============================================================================
elif page == "💡 Optimal Order Recommendations":
    st.header("AI: Optimal Order Pattern Recommendations")
    st.info("💡 Recommendation features coming soon.")

st.sidebar.markdown("---")
st.sidebar.info("🍞 **Chapati Analytics Agent** v9.2\n\nWeek-by-week & month-by-month analysis.")
