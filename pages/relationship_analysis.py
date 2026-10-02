import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_weekly_metrics, find_optimal_quantity, extract_outlet_name

def show():
    st.header("Relationship Analysis")
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        df = st.session_state.data.copy()
        all_names = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_names if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        if valid_branches:
            selected_branch = st.selectbox("Select branch", sorted(valid_branches), label_visibility="collapsed")
            branch_row = df[df['Branch'] == selected_branch]
            
            if len(branch_row) > 0:
                numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
                weekly_data = calculate_weekly_metrics(branch_row, numeric_cols)
                
                if weekly_data:
                    weekly_df = pd.DataFrame(weekly_data)
                    
                    # Filter out weeks with no orders
                    active_weeks = weekly_df[weekly_df['order_quantity'] > 0]
                    
                    if len(active_weeks) > 0:
                        optimal_qty, optimal_return_rate, corr, best_quartile, confidence = find_optimal_quantity(weekly_data)
                        
                        # Extract branch name
                        branch_name = selected_branch.split('-')[-1].strip() if '-' in selected_branch else selected_branch
                        
                        # Key Metrics
                        st.subheader("Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        current_avg_qty = active_weeks['order_quantity'].mean()
                        current_avg_return = active_weeks['return_pct'].mean()
                        
                        with col1:
                            st.metric("Avg Weekly Order", f"{current_avg_qty:.0f} bales")
                            st.caption("Current pattern")
                        
                        with col2:
                            st.metric("Avg Return Rate", f"{current_avg_return:.1f}%")
                            st.caption("Current performance")
                        
                        with col3:
                            st.metric("Correlation", f"{corr:.3f}")
                            st.caption("Order Qty vs Returns")
                        
                        with col4:
                            st.metric("Data Confidence", f"{confidence*100:.0f}%")
                            st.caption("Based on weeks analyzed")
                        
                        # Correlation Explanation
                        st.subheader("What Does This Mean?")
                        
                        if corr > 0.5:
                            st.markdown("""
                            <div style='background: #f8d7da; padding: 1rem; border-left: 4px solid #dc3545; border-radius: 4px;'>
                                <b style='color: #dc3545;'>Strong Positive Correlation (0.5+)</b><br>
                                Larger weekly orders are strongly associated with higher return rates.<br>
                                <b>Implication:</b> This branch struggles with larger orders - quality issues, handling problems, or demand mismatch.
                            </div>
                            """, unsafe_allow_html=True)
                        elif corr > 0.2:
                            st.markdown("""
                            <div style='background: #fff3cd; padding: 1rem; border-left: 4px solid #ffc107; border-radius: 4px;'>
                                <b style='color: #ffc107;'>Moderate Positive Correlation (0.2-0.5)</b><br>
                                Larger orders tend to have somewhat higher return rates.<br>
                                <b>Implication:</b> Some relationship exists - monitor order sizes carefully.
                            </div>
                            """, unsafe_allow_html=True)
                        elif corr < -0.3:
                            st.markdown("""
                            <div style='background: #d4edda; padding: 1rem; border-left: 4px solid #28a745; border-radius: 4px;'>
                                <b style='color: #28a745;'>Negative Correlation (-0.3 or lower)</b><br>
                                Larger orders actually have LOWER return rates.<br>
                                <b>Implication:</b> This is good! Larger orders are handled better. Consider increasing order sizes.
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style='background: #e2e3e5; padding: 1rem; border-left: 4px solid #6c757d; border-radius: 4px;'>
                                <b style='color: #6c757d;'>Weak/No Correlation (-0.2 to 0.2)</b><br>
                                Order size doesn't strongly affect return rates.<br>
                                <b>Implication:</b> Returns are driven by other factors (quality, handling, demand, etc).
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Scatter Plot
                        st.subheader("Order Quantity vs Return Rate")
                        st.caption("Each point represents one week of data")
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=weekly_df['order_quantity'],
                            y=weekly_df['return_pct'],
                            mode='markers',
                            marker=dict(
                                size=10,
                                color=weekly_df['return_pct'],
                                colorscale='RdYlGn_r',
                                line=dict(color='#2c3e50', width=1),
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
                                line=dict(color='#e74c3c', dash='dash', width=2)
                            ))
                        
                        fig.update_layout(
                            title="Weekly Order Quantity vs Return Rate",
                            xaxis_title="Order Quantity (bales)",
                            yaxis_title="Return Rate (%)",
                            height=500,
                            font=dict(size=11),
                            hovermode='closest'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Optimal Recommendation
                        st.subheader("Optimal Order Pattern")
                        st.caption("Based on historical data analysis")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**Current Pattern**")
                            st.metric("Weekly Order", f"{current_avg_qty:.0f} bales")
                            st.metric("Return Rate", f"{current_avg_return:.1f}%")
                        
                        with col2:
                            st.markdown("**Recommended Pattern**")
                            st.metric("Weekly Order", f"{optimal_qty:.0f} bales")
                            st.metric("Return Rate", f"{optimal_return_rate:.1f}%")
                        
                        with col3:
                            st.markdown("**Expected Impact**")
                            qty_change = optimal_qty - current_avg_qty
                            qty_change_pct = (qty_change / current_avg_qty * 100) if current_avg_qty > 0 else 0
                            return_improvement = current_avg_return - optimal_return_rate
                            
                            if qty_change > 0:
                                st.metric("Qty Change", f"+{qty_change:.0f} bales", delta=f"{qty_change_pct:+.1f}%")
                            elif qty_change < 0:
                                st.metric("Qty Change", f"{qty_change:.0f} bales", delta=f"{qty_change_pct:.1f}%")
                            else:
                                st.metric("Qty Change", "0 bales", delta="Maintain")
                            
                            st.metric("Return Reduction", f"{return_improvement:.1f}%")
                        
                        # Recommendation Box
                        st.subheader("Recommendation")
                        
                        if optimal_qty > current_avg_qty:
                            rec_color = "#28a745"
                            rec_text = "INCREASE ORDER SIZE"
                            rec_reason = f"Ordering {optimal_qty:.0f} bales per week (instead of {current_avg_qty:.0f}) should reduce returns from {current_avg_return:.1f}% to {optimal_return_rate:.1f}%."
                        elif optimal_qty < current_avg_qty:
                            rec_color = "#fd7e14"
                            rec_text = "DECREASE ORDER SIZE"
                            rec_reason = f"Ordering {optimal_qty:.0f} bales per week (instead of {current_avg_qty:.0f}) should reduce returns from {current_avg_return:.1f}% to {optimal_return_rate:.1f}%."
                        else:
                            rec_color = "#6c757d"
                            rec_text = "MAINTAIN CURRENT SIZE"
                            rec_reason = f"Current order size of {current_avg_qty:.0f} bales is already optimal."
                        
                        st.markdown(f"""
                        <div style='background: #f8f9fa; padding: 1.5rem; border-left: 4px solid {rec_color}; border-radius: 4px;'>
                            <b style='color: {rec_color}; font-size: 16px;'>{rec_text}</b><br><br>
                            {rec_reason}<br><br>
                            <b>Confidence Level:</b> {confidence*100:.0f}%
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Risk/Benefit Analysis
                        st.subheader("Risk & Benefit Analysis")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Benefits of Following This Recommendation**")
                            st.write(f"✓ Reduce return rate by {return_improvement:.1f}%")
                            st.write(f"✓ Improve inventory efficiency")
                            st.write(f"✓ Better match between supply and demand")
                            st.write(f"✓ Reduce waste and losses")
                        
                        with col2:
                            st.markdown("**Risks to Consider**")
                            if optimal_qty > current_avg_qty:
                                st.write("⚠ Larger orders may strain storage capacity")
                                st.write("⚠ Higher upfront cost")
                                st.write("⚠ May need better handling/training")
                            elif optimal_qty < current_avg_qty:
                                st.write("⚠ Smaller orders may lead to stockouts")
                                st.write("⚠ More frequent ordering (higher logistics cost)")
                                st.write("⚠ May miss sales opportunities")
                            else:
                                st.write("✓ No major risks - maintain current approach")
                        
                        # Quartile Analysis
                        st.subheader("Performance by Order Size")
                        st.caption("How does return rate vary by order quantity quartile?")
                        
                        q1 = active_weeks['order_quantity'].quantile(0.25)
                        q3 = active_weeks['order_quantity'].quantile(0.75)
                        
                        q1_data = active_weeks[active_weeks['order_quantity'] <= q1]
                        q2_data = active_weeks[(active_weeks['order_quantity'] > q1) & (active_weeks['order_quantity'] <= q3)]
                        q3_data = active_weeks[active_weeks['order_quantity'] > q3]
                        
                        quartile_analysis = pd.DataFrame({
                            'Quartile': ['Q1 (Small Orders)', 'Q2 (Medium Orders)', 'Q3 (Large Orders)'],
                            'Avg Order Size': [q1_data['order_quantity'].mean(), q2_data['order_quantity'].mean(), q3_data['order_quantity'].mean()],
                            'Avg Return Rate': [q1_data['return_pct'].mean(), q2_data['return_pct'].mean(), q3_data['return_pct'].mean()],
                            'Weeks': [len(q1_data), len(q2_data), len(q3_data)]
                        })
                        
                        fig_quartile = go.Figure()
                        fig_quartile.add_trace(go.Bar(
                            x=quartile_analysis['Quartile'],
                            y=quartile_analysis['Avg Return Rate'],
                            marker_color=['#e74c3c', '#ffc107', '#28a745'],
                            text=quartile_analysis['Avg Return Rate'].apply(lambda x: f"{x:.1f}%"),
                            textposition='auto',
                            hovertemplate='%{x}<br>Avg Return Rate: %{y:.1f}%<extra></extra>'
                        ))
                        fig_quartile.update_layout(
                            title="Average Return Rate by Order Size Quartile",
                            xaxis_title="Order Size Category",
                            yaxis_title="Return Rate (%)",
                            height=400,
                            showlegend=False,
                            font=dict(size=11)
                        )
                        st.plotly_chart(fig_quartile, use_container_width=True)
                        
                        # Detailed Data
                        with st.expander("View Detailed Weekly Data"):
                            display_weekly = weekly_df.copy()
                            display_weekly['Week'] = display_weekly['week'].apply(lambda x: f"W{int(x)}")
                            display_weekly['Order Qty'] = display_weekly['order_quantity'].apply(lambda x: f"{x:.0f}")
                            display_weekly['Return %'] = display_weekly['return_pct'].apply(lambda x: f"{x:.1f}%")
                            display_weekly['Net Sales'] = display_weekly['net_sales'].apply(lambda x: f"{x:.0f}")
                            display_weekly['Returns'] = display_weekly['returns'].apply(lambda x: f"{x:.0f}")
                            
                            st.dataframe(display_weekly[['Week', 'Order Qty', 'Net Sales', 'Returns', 'Return %']], use_container_width=True, hide_index=True)
