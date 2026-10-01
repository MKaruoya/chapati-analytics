import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_weekly_metrics, find_optimal_quantity, extract_outlet_name

def show():
    st.header("Order Recommendations")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        outlet_names = sorted(set([extract_outlet_name(b) for b in valid_branches if extract_outlet_name(b)]))
        if not outlet_names:
            st.error("No outlets found")
        else:
            selected_outlet = st.selectbox("Select outlet", outlet_names, label_visibility="collapsed")
            outlet_branches = [b for b in valid_branches if extract_outlet_name(b) == selected_outlet]
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
                                if current_avg_return > 25:
                                    status = "CRITICAL"
                                    priority = 1
                                elif current_avg_return > 20:
                                    status = "HIGH"
                                    priority = 2
                                elif current_avg_return > 15:
                                    status = "MODERATE"
                                    priority = 3
                                else:
                                    status = "GOOD"
                                    priority = 4
                                recommendations.append({'Branch': branch, 'Current Qty': current_avg_qty, 'Current Return %': current_avg_return, 'Recommended Qty': optimal_qty, 'Expected Return %': optimal_return_rate, 'Qty Change %': qty_change_pct, 'Expected Improvement': expected_improvement, 'Confidence': confidence, 'Status': status, 'Priority': priority})
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                rec_df = rec_df.sort_values('Priority')
                st.subheader("Summary")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Branches", len(rec_df))
                col2.metric("Avg Current Qty", f"{rec_df['Current Qty'].mean():.0f} bales")
                col3.metric("Avg Recommended Qty", f"{rec_df['Recommended Qty'].mean():.0f} bales")
                col4.metric("Avg Current Return %", f"{rec_df['Current Return %'].mean():.1f}%")
                col5.metric("Avg Expected Return %", f"{rec_df['Expected Return %'].mean():.1f}%")
                st.subheader("Recommendations")
                for idx, row in rec_df.iterrows():
                    with st.expander(f"{row['Branch']} - {row['Status']} | {row['Current Qty']:.0f} bales ({row['Current Return %']:.1f}%)"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown("**Current**")
                            st.metric("Weekly Order", f"{row['Current Qty']:.0f} bales", label_visibility="collapsed")
                            st.metric("Return Rate", f"{row['Current Return %']:.1f}%", label_visibility="collapsed")
                        with col2:
                            st.markdown("**Recommended**")
                            st.metric("Weekly Order", f"{row['Recommended Qty']:.0f} bales", label_visibility="collapsed")
                            st.metric("Return Rate", f"{row['Expected Return %']:.1f}%", label_visibility="collapsed")
                        with col3:
                            st.markdown("**Impact**")
                            st.metric("Qty Change", f"{row['Qty Change %']:.1f}%", label_visibility="collapsed")
                            st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%", label_visibility="collapsed")
                        st.caption(f"Confidence: {row['Confidence']*100:.0f}%")
                st.subheader("Visualizations")
                col1, col2 = st.columns(2)
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Current Qty'], name='Current', marker_color='#95a5a6'))
                    fig.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Recommended Qty'], name='Recommended', marker_color='#3498db'))
                    fig.update_layout(title="Current vs Recommended", barmode='group', height=450, xaxis_tickangle=-45, showlegend=True, font=dict(size=11))
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Current Return %'], name='Current', marker_color='#e74c3c'))
                    fig2.add_trace(go.Bar(x=rec_df['Branch'], y=rec_df['Expected Return %'], name='Expected', marker_color='#27ae60'))
                    fig2.update_layout(title="Return Rate Comparison", barmode='group', height=450, xaxis_tickangle=-45, showlegend=True, font=dict(size=11))
                    st.plotly_chart(fig2, use_container_width=True)
                st.subheader("Export")
                export_df = rec_df[['Branch', 'Current Qty', 'Recommended Qty', 'Qty Change %', 'Current Return %', 'Expected Return %', 'Expected Improvement', 'Confidence', 'Status']].copy()
                export_df.columns = ['Branch', 'Current Qty', 'Recommended Qty', 'Change %', 'Current Return %', 'Expected Return %', 'Improvement %', 'Confidence', 'Status']
                st.dataframe(export_df, use_container_width=True, hide_index=True)
