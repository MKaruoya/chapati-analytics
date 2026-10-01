import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def show():
    st.header("Store Analysis")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        if branches:
            selected_branch = st.selectbox("Select branch", sorted(branches), label_visibility="collapsed")
            branch_row = df[df['Branch'] == selected_branch]
            if len(branch_row) > 0:
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                weekly_data = []
                week_num = 1
                for i in range(0, len(numeric_cols) - 1, 2):
                    net_sales_val = pd.to_numeric(branch_row[numeric_cols[i]].values[0], errors='coerce')
                    returns_val = pd.to_numeric(branch_row[numeric_cols[i + 1]].values[0], errors='coerce')
                    if pd.notna(net_sales_val) or pd.notna(returns_val):
                        net_sales_val = net_sales_val if pd.notna(net_sales_val) else 0
                        returns_val = returns_val if pd.notna(returns_val) else 0
                        original_order = abs(net_sales_val) + returns_val
                        return_pct = (returns_val / original_order * 100) if original_order > 0 else 0
                        weekly_data.append({'Week': f"W{week_num}", 'Net Sales': f"{net_sales_val:.0f}", 'Returns': f"{returns_val:.0f}", 'Return %': f"{return_pct:.1f}%", 'net_sales_numeric': net_sales_val, 'returns_numeric': returns_val, 'return_pct_numeric': return_pct})
                    week_num += 1
                if weekly_data:
                    st.subheader("Weekly Performance")
                    weekly_df = pd.DataFrame(weekly_data)
                    st.dataframe(weekly_df[['Week', 'Net Sales', 'Returns', 'Return %']], use_container_width=True, hide_index=True)
                    st.subheader("Monthly Performance")
                    weeks_per_month = 5
                    monthly_data = []
                    for month_num in range(1, 10):
                        start_week = (month_num - 1) * weeks_per_month
                        end_week = month_num * weeks_per_month
                        month_weeks = weekly_data[start_week:end_week]
                        if month_weeks:
                            month_sales = sum([w['net_sales_numeric'] for w in month_weeks])
                            month_returns = sum([w['returns_numeric'] for w in month_weeks])
                            month_original = abs(month_sales) + month_returns
                            month_return_pct = (month_returns / month_original * 100) if month_original > 0 else 0
                            monthly_data.append({'Month': f"M{month_num}", 'Net Sales': f"{month_sales:.0f}", 'Returns': f"{month_returns:.0f}", 'Return %': f"{month_return_pct:.1f}%", 'net_sales_numeric': month_sales, 'returns_numeric': month_returns, 'return_pct_numeric': month_return_pct})
                    if monthly_data:
                        monthly_df = pd.DataFrame(monthly_data)
                        st.dataframe(monthly_df[['Month', 'Net Sales', 'Returns', 'Return %']], use_container_width=True, hide_index=True)
                        st.subheader("Trend")
                        monthly_df_plot = monthly_df.copy()
                        monthly_df_plot['Net Sales'] = pd.to_numeric(monthly_df_plot['net_sales_numeric'])
                        monthly_df_plot['Returns'] = pd.to_numeric(monthly_df_plot['returns_numeric'])
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Net Sales'], name='Net Sales', marker_color='#27ae60'))
                        fig.add_trace(go.Bar(x=monthly_df_plot['Month'], y=monthly_df_plot['Returns'], name='Returns', marker_color='#e74c3c'))
                        fig.update_layout(title="Monthly Net Sales vs Returns", barmode='group', height=450, showlegend=True, font=dict(size=11))
                        st.plotly_chart(fig, use_container_width=True)
