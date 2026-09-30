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
    st.header("Store-Level Analysis - Week by Week & Month by Month")
    
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
                
                # Define the structure: Month, Weeks, and column pairs
                # Based on the data: columns c-k are March (weeks 10-14)
                # columns m-v are April (weeks 14-18), etc.
                
                structure = {
                    '03 March': {
                        10: ('column_c', 'column_d'),
                        11: ('column_e', 'column_f'),
                        12: ('column_g', 'column_h'),
                        13: ('column_i', 'column_j'),
                        14: ('column_k', 'column_l'),
                    },
                    '04 April': {
                        14: ('column_m', 'column_n'),
                        15: ('column_o', 'column_p'),
                        16: ('column_q', 'column_r'),
                        17: ('column_s', 'column_t'),
                        18: ('column_u', 'column_v'),
                    },
                    '05 May': {
                        18: ('column_w', 'column_x'),
                        19: ('column_y', 'column_z'),
                        20: ('column_aa', 'column_ab'),
                        21: ('column_ac', 'column_ad'),
                        22: ('column_ae', 'column_af'),
                    },
                    '06 June': {
                        23: ('column_ag', 'column_ah'),
                        24: ('column_ai', 'column_aj'),
                        25: ('column_ak', 'column_al'),
                        26: ('column_am', 'column_an'),
                        27: ('column_ao', 'column_ap'),
                    }
                }
                
                # Build weekly data
                weekly_data = []
                monthly_summary = {}
                
                for month, weeks in structure.items():
                    if month not in monthly_summary:
                        monthly_summary[month] = {'sales': 0, 'returns': 0}
                    
                    for week, (sales_col, returns_col) in weeks.items():
                        if sales_col in df.columns and returns_col in df.columns:
                            sales_val = pd.to_numeric(branch_row[sales_col].values[0], errors='coerce')
                            returns_val = pd.to_numeric(branch_row[returns_col].values[0], errors='coerce')
                            
                            if pd.notna(sales_val) or pd.notna(returns_val):
                                sales_val = sales_val if pd.notna(sales_val) else 0
                                returns_val = returns_val if pd.notna(returns_val) else 0
                                return_pct = (returns_val / sales_val * 100) if sales_val > 0 else 0
                                
                                weekly_data.append({
                                    'Week': f"{month} - W{week}",
                                    'Sales': f"{sales_val:.0f}",
                                    'Returns': f"{returns_val:.0f}",
                                    'Net': f"{sales_val - returns_val:.0f}",
                                    'Return %': f"{return_pct:.1f}%"
                                })
                                
                                monthly_summary[month]['sales'] += sales_val
                                monthly_summary[month]['returns'] += returns_val
                
                if weekly_data:
                    st.subheader("📅 Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    st.dataframe(weekly_df, use_container_width=True)
                    
                    # Monthly summary
                    st.subheader("📊 Monthly Summary")
                    monthly_data = []
                    for month in ['03 March', '04 April', '05 May', '06 June']:
                        if month in monthly_summary:
                            sales = monthly_summary[month]['sales']
                            returns = monthly_summary[month]['returns']
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
st.sidebar.info("🍞 **Chapati Analytics Agent** v11.0\n\nFocused on actual data analysis.")
