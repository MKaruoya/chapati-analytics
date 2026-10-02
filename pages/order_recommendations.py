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
                                qty_change = optimal_qty - current_avg_qty
                                qty_change_pct = ((qty_change) / current_avg_qty * 100) if current_avg_qty > 0 else 0
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
                                
                                # Calculate effort level
                                if abs(qty_change_pct) < 10:
                                    effort = "Low"
                                    effort_color = "#28a745"
                                elif abs(qty_change_pct) < 25:
                                    effort = "Medium"
                                    effort_color = "#ffc107"
                                else:
                                    effort = "High"
                                    effort_color = "#fd7e14"
                                
                                # Calculate impact score (improvement * confidence)
                                impact_score = expected_improvement * confidence
                                
                                recommendations.append({
                                    'Branch': branch,
                                    'Branch Name': branch.split('-')[-1].strip() if '-' in branch else branch,
                                    'Current Qty': current_avg_qty,
                                    'Current Return %': current_avg_return,
                                    'Recommended Qty': optimal_qty,
                                    'Expected Return %': optimal_return_rate,
                                    'Qty Change': qty_change,
                                    'Qty Change %': qty_change_pct,
                                    'Expected Improvement': expected_improvement,
                                    'Confidence': confidence,
                                    'Status': status,
                                    'Priority': priority,
                                    'Effort': effort,
                                    'Effort Color': effort_color,
                                    'Impact Score': impact_score
                                })
            
            if recommendations:
                rec_df = pd.DataFrame(recommendations)
                rec_df = rec_df.sort_values('Priority')
                
                # Outlet-Level Summary
                st.subheader("Outlet Impact Summary")
                st.caption(f"If all recommendations are implemented for {selected_outlet}")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_branches = len(rec_df)
                current_avg_return_all = rec_df['Current Return %'].mean()
                expected_avg_return_all = rec_df['Expected Return %'].mean()
                total_improvement = current_avg_return_all - expected_avg_return_all
                total_improvement_pct = (total_improvement / current_avg_return_all * 100) if current_avg_return_all > 0 else 0
                
                col1.metric("Total Branches", total_branches)
                col2.metric("Current Avg Return %", f"{current_avg_return_all:.1f}%")
                col3.metric("Expected Avg Return %", f"{expected_avg_return_all:.1f}%")
                col4.metric("Total Improvement", f"{total_improvement:.1f}%")
                col5.metric("Improvement %", f"{total_improvement_pct:.1f}%")
                
                # Quick Wins Section
                st.subheader("Quick Wins - High Impact, Low Effort")
                st.caption("Start here for immediate results")
                
                quick_wins = rec_df[(rec_df['Effort'] == 'Low') & (rec_df['Expected Improvement'] > 2)].sort_values('Expected Improvement', ascending=False)
                
                if len(quick_wins) > 0:
                    for idx, row in quick_wins.iterrows():
                        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{row['Branch Name']}**")
                            st.caption(f"Current: {row['Current Qty']:.0f} bales → Recommended: {row['Recommended Qty']:.0f} bales")
                        
                        with col2:
                            st.metric("Return Reduction", f"{row['Expected Improvement']:.1f}%", label_visibility="collapsed")
                        
                        with col3:
                            st.metric("Effort", row['Effort'], label_visibility="collapsed")
                        
                        with col4:
                            st.metric("Confidence", f"{row['Confidence']*100:.0f}%", label_visibility="collapsed")
                else:
                    st.info("No quick wins available - all recommendations require significant effort")
                
                # Implementation Roadmap
                st.subheader("Implementation Roadmap")
                st.caption("Phased approach for rolling out recommendations")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Phase 1: Immediate (Week 1-2)**")
                    st.markdown("Quick wins - low effort, high impact")
                    phase1 = quick_wins
                    if len(phase1) > 0:
                        for idx, row in phase1.iterrows():
                            st.write(f"• {row['Branch Name']}")
                    else:
                        st.caption("None")
                
                with col2:
                    st.markdown("**Phase 2: Short-term (Week 3-4)**")
                    st.markdown("Medium effort, good impact")
                    phase2 = rec_df[(rec_df['Effort'] == 'Medium')].sort_values('Expected Improvement', ascending=False)
                    if len(phase2) > 0:
                        for idx, row in phase2.iterrows():
                            st.write(f"• {row['Branch Name']}")
                    else:
                        st.caption("None")
                
                with col3:
                    st.markdown("**Phase 3: Long-term (Week 5+)**")
                    st.markdown("High effort, requires planning")
                    phase3 = rec_df[(rec_df['Effort'] == 'High')].sort_values('Expected Improvement', ascending=False)
                    if len(phase3) > 0:
                        for idx, row in phase3.iterrows():
                            st.write(f"• {row['Branch Name']}")
                    else:
                        st.caption("None")
                
                # All Recommendations
                st.subheader("All Recommendations")
                
                for idx, row in rec_df.iterrows():
                    # Determine status color
                    if row['Status'] == 'CRITICAL':
                        status_color = '#dc3545'
                    elif row['Status'] == 'HIGH':
                        status_color = '#fd7e14'
                    elif row['Status'] == 'MODERATE':
                        status_color = '#ffc107'
                    else:
                        status_color = '#28a745'
                    
                    with st.expander(f"{row['Branch Name']} | Current: {row['Current Qty']:.0f} → Recommended: {row['Recommended Qty']:.0f} bales | {row['Status']}"):
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown("**Current Pattern**")
                            st.write(f"Order: {row['Current Qty']:.0f} bales/week")
                            st.write(f"Return Rate: {row['Current Return %']:.1f}%")
                        
                        with col2:
                            st.markdown("**Recommended Pattern**")
                            st.write(f"Order: {row['Recommended Qty']:.0f} bales/week")
                            st.write(f"Return Rate: {row['Expected Return %']:.1f}%")
                        
                        with col3:
                            st.markdown("**Change Required**")
                            if row['Qty Change'] > 0:
                                st.write(f"Increase by {row['Qty Change']:.0f} bales")
                                st.write(f"({row['Qty Change %']:+.1f}%)")
                            elif row['Qty Change'] < 0:
                                st.write(f"Decrease by {abs(row['Qty Change']):.0f} bales")
                                st.write(f"({row['Qty Change %']:.1f}%)")
                            else:
                                st.write("No change needed")
                        
                        with col4:
                            st.markdown("**Expected Impact**")
                            st.write(f"Return Reduction: {row['Expected Improvement']:.1f}%")
                            st.write(f"Effort: {row['Effort']}")
                            st.write(f"Confidence: {row['Confidence']*100:.0f}%")
                        
                        st.markdown("---")
                        st.markdown("**Action Steps:**")
                        st.write("1. Review current ordering pattern with store manager")
                        st.write(f"2. Adjust weekly order from {row['Current Qty']:.0f} to {row['Recommended Qty']:.0f} bales")
                        st.write("3. Monitor return rate for 2-3 weeks")
                        st.write(f"4. Expected improvement: {row['Expected Improvement']:.1f}% reduction in returns")
                
                # Visualizations
                st.subheader("Visualizations")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=rec_df['Branch Name'],
                        y=rec_df['Current Qty'],
                        name='Current',
                        marker_color='#95a5a6'
                    ))
                    fig.add_trace(go.Bar(
                        x=rec_df['Branch Name'],
                        y=rec_df['Recommended Qty'],
                        name='Recommended',
                        marker_color='#3498db'
                    ))
                    fig.update_layout(
                        title="Current vs Recommended Order Quantities",
                        barmode='group',
                        height=450,
                        xaxis_tickangle=-45,
                        showlegend=True,
                        font=dict(size=11)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=rec_df['Branch Name'],
                        y=rec_df['Current Return %'],
                        name='Current',
                        marker_color='#e74c3c'
                    ))
                    fig2.add_trace(go.Bar(
                        x=rec_df['Branch Name'],
                        y=rec_df['Expected Return %'],
                        name='Expected',
                        marker_color='#27ae60'
                    ))
                    fig2.update_layout(
                        title="Return Rate: Current vs Expected",
                        barmode='group',
                        height=450,
                        xaxis_tickangle=-45,
                        showlegend=True,
                        font=dict(size=11)
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Export Action Plan
                st.subheader("Export Action Plan")
                
                export_df = rec_df[[
                    'Branch Name', 'Current Qty', 'Recommended Qty', 'Qty Change %',
                    'Current Return %', 'Expected Return %', 'Expected Improvement',
                    'Effort', 'Confidence', 'Status'
                ]].copy()
                
                export_df.columns = [
                    'Branch', 'Current Weekly Qty', 'Recommended Weekly Qty', 'Change %',
                    'Current Return %', 'Expected Return %', 'Expected Improvement %',
                    'Implementation Effort', 'Confidence', 'Status'
                ]
                
                export_df['Current Weekly Qty'] = export_df['Current Weekly Qty'].apply(lambda x: f"{x:.0f}")
                export_df['Recommended Weekly Qty'] = export_df['Recommended Weekly Qty'].apply(lambda x: f"{x:.0f}")
                export_df['Change %'] = export_df['Change %'].apply(lambda x: f"{x:+.1f}%")
                export_df['Current Return %'] = export_df['Current Return %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Return %'] = export_df['Expected Return %'].apply(lambda x: f"{x:.1f}%")
                export_df['Expected Improvement %'] = export_df['Expected Improvement %'].apply(lambda x: f"{x:.1f}%")
                export_df['Confidence'] = export_df['Confidence'].apply(lambda x: f"{x*100:.0f}%")
                
                st.dataframe(export_df, use_container_width=True, hide_index=True)
                
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="Download Action Plan as CSV",
                    data=csv,
                    file_name=f"order_recommendations_{selected_outlet}.csv",
                    mime="text/csv"
                )
