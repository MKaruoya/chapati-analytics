import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import calculate_monthly_metrics, extract_outlet_name

def show():
    st.header("Branch Performance Dashboard")
    st.caption("October Analytics - All Branches Overview")
    
    if st.session_state.data is None:
        st.warning("Please upload data first from the Data Upload page")
        return
    
    df = st.session_state.data.copy()
    
    # Calculate metrics for all branches
    all_metrics = []
    
    for _, branch_row in df.iterrows():
        branch_name = branch_row['Branch']
        
        numeric_cols = [col for col in df.columns[1:] if df[col].dtype in ['int64', 'float64']]
        monthly_data = calculate_monthly_metrics(branch_row, numeric_cols)
        monthly_df = pd.DataFrame(monthly_data)
        monthly_df = monthly_df[monthly_df['has_data'] == True]
        
        if len(monthly_df) > 0:
            all_metrics.append({
                'branch': branch_name,
                'outlet': extract_outlet_name(branch_name),
                'total_sales': monthly_df['sales'].sum(),
                'total_returns': monthly_df['returns'].sum(),
                'avg_return_rate': monthly_df['return_rate'].mean(),
                'months_active': len(monthly_df),
                'volatility': monthly_df['return_rate'].std() if len(monthly_df) > 1 else 0,
                'trend': 'Rising' if len(monthly_df) > 1 and monthly_df.iloc[-1]['return_rate'] > monthly_df.iloc[0]['return_rate'] else 'Declining'
            })
    
    metrics_df = pd.DataFrame(all_metrics)
    
    # Summary Stats
    st.subheader("Overall Summary")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Branches", len(metrics_df))
    
    with col2:
        st.metric("Total Sales", f"{metrics_df['total_sales'].sum():.0f}")
    
    with col3:
        st.metric("Total Returns", f"{metrics_df['total_returns'].sum():.0f}")
    
    with col4:
        avg_return = (metrics_df['total_returns'].sum() / (metrics_df['total_sales'].sum() + metrics_df['total_returns'].sum()) * 100)
        st.metric("Overall Return Rate", f"{avg_return:.1f}%")
    
    with col5:
        st.metric("Avg Branch Return Rate", f"{metrics_df['avg_return_rate'].mean():.1f}%")
    
    st.divider()
    
    # Top and Bottom Performers
    st.subheader("Performance Ranking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 10 Performers (Lowest Return Rate)**")
        top_10 = metrics_df.nsmallest(10, 'avg_return_rate')[['outlet', 'total_sales', 'avg_return_rate']]
        top_10['Return Rate'] = top_10['avg_return_rate'].apply(lambda x: f"{x:.1f}%")
        top_10['Sales'] = top_10['total_sales'].apply(lambda x: f"{x:.0f}")
        st.dataframe(top_10[['outlet', 'Sales', 'Return Rate']], use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Bottom 10 Performers (Highest Return Rate)**")
        bottom_10 = metrics_df.nlargest(10, 'avg_return_rate')[['outlet', 'total_sales', 'avg_return_rate']]
        bottom_10['Return Rate'] = bottom_10['avg_return_rate'].apply(lambda x: f"{x:.1f}%")
        bottom_10['Sales'] = bottom_10['total_sales'].apply(lambda x: f"{x:.0f}")
        st.dataframe(bottom_10[['outlet', 'Sales', 'Return Rate']], use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Trend Analysis
    st.subheader("Trend Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Improving Branches (Return Rate Declining)**")
        improving = metrics_df[metrics_df['trend'] == 'Declining'].nsmallest(10, 'avg_return_rate')
        improving_display = improving[['outlet', 'avg_return_rate', 'volatility']]
        improving_display['Return Rate'] = improving_display['avg_return_rate'].apply(lambda x: f"{x:.1f}%")
        improving_display['Volatility'] = improving_display['volatility'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(improving_display[['outlet', 'Return Rate', 'Volatility']], use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Deteriorating Branches (Return Rate Rising)**")
        deteriorating = metrics_df[metrics_df['trend'] == 'Rising'].nlargest(10, 'avg_return_rate')
        deteriorating_display = deteriorating[['outlet', 'avg_return_rate', 'volatility']]
        deteriorating_display['Return Rate'] = deteriorating_display['avg_return_rate'].apply(lambda x: f"{x:.1f}%")
        deteriorating_display['Volatility'] = deteriorating_display['volatility'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(deteriorating_display[['outlet', 'Return Rate', 'Volatility']], use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Distribution Charts
    st.subheader("Distribution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Return Rate Distribution**")
        fig1 = go.Figure()
        fig1.add_trace(go.Histogram(
            x=metrics_df['avg_return_rate'],
            nbinsx=20,
            marker_color='#e74c3c'
        ))
        fig1.update_layout(
            title="Return Rate Distribution",
            xaxis_title="Return Rate (%)",
            yaxis_title="Number of Branches",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.markdown("**Sales Distribution**")
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=metrics_df['total_sales'],
            nbinsx=20,
            marker_color='#3498db'
        ))
        fig2.update_layout(
            title="Sales Distribution",
            xaxis_title="Total Sales",
            yaxis_title="Number of Branches",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    st.divider()
    
    # Scatter Plot: Sales vs Return Rate
    st.subheader("Sales vs Return Rate Analysis")
    
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=metrics_df['total_sales'],
        y=metrics_df['avg_return_rate'],
        mode='markers',
        marker=dict(
            size=8,
            color=metrics_df['avg_return_rate'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="Return Rate %")
        ),
        text=metrics_df['outlet'],
        hovertemplate='<b>%{text}</b><br>Sales: %{x:.0f}<br>Return Rate: %{y:.1f}%<extra></extra>'
    ))
    
    fig3.update_layout(
        title="Sales vs Return Rate",
        xaxis_title="Total Sales",
        yaxis_title="Average Return Rate (%)",
        height=500,
        hovermode='closest'
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    st.divider()
    
    # Full Data Table
    st.subheader("All Branches - Detailed View")
    
    display_metrics = metrics_df.copy()
    display_metrics['Sales'] = display_metrics['total_sales'].apply(lambda x: f"{x:.0f}")
    display_metrics['Returns'] = display_metrics['total_returns'].apply(lambda x: f"{x:.0f}")
    display_metrics['Return Rate'] = display_metrics['avg_return_rate'].apply(lambda x: f"{x:.1f}%")
    display_metrics['Volatility'] = display_metrics['volatility'].apply(lambda x: f"{x:.1f}%")
    display_metrics['Months'] = display_metrics['months_active'].apply(lambda x: f"{int(x)}")
    
    final_display = display_metrics[['outlet', 'Sales', 'Returns', 'Return Rate', 'Volatility', 'Months', 'trend']]
    final_display.columns = ['Outlet', 'Sales', 'Returns', 'Return Rate', 'Volatility', 'Months', 'Trend']
    
    st.dataframe(final_display, use_container_width=True, hide_index=True)
