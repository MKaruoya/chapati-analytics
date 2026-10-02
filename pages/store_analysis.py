import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

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
                        
                        # If net sales is negative, no order was placed (only delayed returns)
                        if net_sales_val < 0:
                            order_qty = 0
                            return_pct = 0
                        else:
                            # Order Qty = Net Sales + Returns
                            order_qty = net_sales_val + returns_val
                            # Return % = Returns / Order Qty
                            return_pct = (returns_val / order_qty * 100) if order_qty > 0 else 0
                        
                        weekly_data.append({
                            'Week': week_num,
                            'Net Sales': net_sales_val,
                            'Returns': returns_val,
                            'Return %': return_pct,
                            'Order Qty': order_qty
                        })
                    week_num += 1
                
                if weekly_data:
                    weekly_df = pd.DataFrame(weekly_data)
                    
                    # Calculate monthly data
                    weeks_per_month = 5
                    monthly_data = []
                    
                    for month_num in range(1, 10):
                        start_week = (month_num - 1) * weeks_per_month
                        end_week = month_num * weeks_per_month
                        month_weeks = weekly_df[(weekly_df['Week'] > start_week) & (weekly_df['Week'] <= end_week)]
                        
                        if len(month_weeks) > 0:
                            month_sales = month_weeks['Net Sales'].sum()
                            month_returns = month_weeks['Returns'].sum()
                            month_order = month_weeks['Order Qty'].sum()
                            # Return % = Total Returns / Total Order Qty
                            month_return_pct = (month_returns / month_order * 100) if month_order > 0 else 0
                            
                            monthly_data.append({
                                'Month': month_num,
                                'Net Sales': month_sales,
                                'Returns': month_returns,
                                'Return %': month_return_pct,
                                'Order Qty': month_order
                            })
                    
                    if monthly_data:
                        monthly_df = pd.DataFrame(monthly_data)
                        
                        # Extract branch name
                        branch_name = selected_branch.split('-')[-1].strip() if '-' in selected_branch else selected_branch
                        
                        # Key Metrics
                        st.subheader("Overview")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        current_month = monthly_df.iloc[-1]
                        avg_return = monthly_df['Return %'].mean()
                        
                        with col1:
                            st.metric("Current Month Return Rate", f"{current_month['Return %']:.1f}%")
                            st.caption("Month 7 performance")
                        
                        with col2:
                            st.metric("Avg Return Rate", f"{avg_return:.1f}%")
                            st.caption("Average across all months")
                        
                        with col3:
                            st.metric("Current Month Sales", f"{current_month['Net Sales']:.0f}")
                            st.caption("Net sales in Month 7")
                        
                        with col4:
                            st.metric("Current Month Orders", f"{current_month['Order Qty']:.0f} bales")
                            st.caption("Total order quantity")
                        
                        # Trend Analysis
                        st.subheader("Monthly Trend")
                        st.caption("Return rate over time (March to September)")
                        
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=monthly_df['Month'],
                            y=monthly_df['Return %'],
                            mode='lines+markers',
                            name='Return Rate %',
                            line=dict(color='#e74c3c', width=3),
                            marker=dict(size=10),
                            fill='tozeroy',
                            fillcolor='rgba(220, 53, 69, 0.1)'
                        ))
                        
                        fig.update_layout(
                            title="Monthly Return Rate Trend",
                            xaxis_title="Month",
                            yaxis_title="Return Rate (%)",
                            hovermode='x unified',
                            height=450,
                            font=dict(size=11),
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Order Quantity Trend
                        st.subheader("Order Quantity Trend")
                        st.caption("Weekly order quantities over time")
                        
                        fig2 = go.Figure()
                        
                        fig2.add_trace(go.Bar(
                            x=weekly_df['Week'],
                            y=weekly_df['Order Qty'],
                            name='Order Quantity',
                            marker_color='#3498db'
                        ))
                        
                        fig2.update_layout(
                            title="Weekly Order Quantities",
                            xaxis_title="Week",
                            yaxis_title="Order Quantity (bales)",
                            height=400,
                            font=dict(size=11),
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig2, use_container_width=True)
                        
                        # Performance Analysis
                        st.subheader("Performance Analysis")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Key Metrics**")
                            
                            # Calculate trend
                            first_month_return = monthly_df.iloc[0]['Return %']
                            last_month_return = monthly_df.iloc[-1]['Return %']
                            trend = "Improving" if last_month_return < first_month_return else "Worsening" if last_month_return > first_month_return else "Stable"
                            trend_color = "#28a745" if trend == "Improving" else "#dc3545" if trend == "Worsening" else "#6c757d"
                            
                            st.markdown(f"<span style='color: {trend_color}; font-weight: bold;'>Trend: {trend}</span>", unsafe_allow_html=True)
                            st.write(f"Started at: {first_month_return:.1f}% | Current: {last_month_return:.1f}%")
                            
                            st.write("")
                            st.markdown("**Best Month**")
                            best_month = monthly_df.loc[monthly_df['Return %'].idxmin()]
                            st.write(f"Month {int(best_month['Month'])}: {best_month['Return %']:.1f}% return rate")
                            
                            st.write("")
                            st.markdown("**Worst Month**")
                            worst_month = monthly_df.loc[monthly_df['Return %'].idxmax()]
                            st.write(f"Month {int(worst_month['Month'])}: {worst_month['Return %']:.1f}% return rate")
                        
                        with col2:
                            st.markdown("**Insights**")
                            
                            # Volatility
                            volatility = monthly_df['Return %'].std()
                            st.write(f"Volatility: {volatility:.1f}%")
                            if volatility > 10:
                                st.caption("High volatility - inconsistent performance")
                            elif volatility > 5:
                                st.caption("Moderate volatility - some fluctuation")
                            else:
                                st.caption("Low volatility - consistent performance")
                            
                            st.write("")
                            
                            # Correlation between order qty and returns
                            if len(monthly_df) > 1:
                                corr = monthly_df['Order Qty'].corr(monthly_df['Return %'])
                                st.write(f"Order Qty vs Return Rate Correlation: {corr:.3f}")
                                if corr > 0.3:
                                    st.caption("Larger orders tend to have higher returns")
                                elif corr < -0.3:
                                    st.caption("Larger orders tend to have lower returns")
                                else:
                                    st.caption("No strong relationship between order size and returns")
                        
                        # Status Box
                        st.subheader("Current Status")
                        
                        if current_month['Return %'] > 30:
                            status_color = "#dc3545"
                            status_text = "CRITICAL"
                        elif current_month['Return %'] > 20:
                            status_color = "#fd7e14"
                            status_text = "HIGH"
                        elif current_month['Return %'] > 15:
                            status_color = "#ffc107"
                            status_text = "MODERATE"
                        else:
                            status_color = "#28a745"
                            status_text = "GOOD"
                        
                        st.markdown(f"""
                        <div style='background: #f8f9fa; padding: 1.5rem; border-left: 4px solid {status_color}; border-radius: 4px;'>
                            <b style='color: {status_color}; font-size: 18px;'>{status_text}</b><br>
                            Return Rate: {current_month['Return %']:.1f}% | Trend: {trend}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detailed Data
                        with st.expander("View Detailed Monthly Data"):
                            display_monthly = monthly_df.copy()
                            display_monthly['Month'] = display_monthly['Month'].apply(lambda x: f"M{int(x)}")
                            display_monthly['Net Sales'] = display_monthly['Net Sales'].apply(lambda x: f"{x:.0f}")
                            display_monthly['Returns'] = display_monthly['Returns'].apply(lambda x: f"{x:.0f}")
                            display_monthly['Return %'] = display_monthly['Return %'].apply(lambda x: f"{x:.1f}%")
                            display_monthly['Order Qty'] = display_monthly['Order Qty'].apply(lambda x: f"{x:.0f}")
                            
                            st.dataframe(display_monthly, use_container_width=True, hide_index=True)
                        
                        with st.expander("View Detailed Weekly Data"):
                            display_weekly = weekly_df.copy()
                            display_weekly['Week'] = display_weekly['Week'].apply(lambda x: f"W{int(x)}")
                            display_weekly['Net Sales'] = display_weekly['Net Sales'].apply(lambda x: f"{x:.0f}")
                            display_weekly['Returns'] = display_weekly['Returns'].apply(lambda x: f"{x:.0f}")
                            display_weekly['Return %'] = display_weekly['Return %'].apply(lambda x: f"{x:.1f}%")
                            display_weekly['Order Qty'] = display_weekly['Order Qty'].apply(lambda x: f"{x:.0f}")
                            
                            st.dataframe(display_weekly, use_container_width=True, hide_index=True)
