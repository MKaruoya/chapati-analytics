import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import config

class Visualizer:
    @staticmethod
    def create_sales_trend_chart(trends_data):
        """Create monthly sales trend line chart"""
        fig = go.Figure()
        
        months = list(trends_data.keys())
        sales = list(trends_data.values())
        
        fig.add_trace(go.Scatter(
            x=months, y=sales,
            mode='lines+markers',
            name='Sales',
            line=dict(color=config.COLOR_PALETTE['primary'], width=3),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="Monthly Sales Trend",
            xaxis_title="Month",
            yaxis_title="Sales (Bales)",
            hovermode='x unified',
            template='plotly_white'
        )
        return fig
    
    @staticmethod
    def create_store_performance_chart(performance_df):
        """Create store performance bar chart"""
        fig = px.bar(
            performance_df.reset_index(),
            x='store',
            y='sales',
            color='return_rate',
            color_continuous_scale='RdYlGn_r',
            title="Top Stores by Sales",
            labels={'sales': 'Total Sales (Bales)', 'return_rate': 'Return Rate'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        return fig
    
    @staticmethod
    def create_product_mix_chart(product_sales):
        """Create product mix pie chart"""
        fig = px.pie(
            values=product_sales.values,
            names=product_sales.index,
            title="Product Mix by Sales",
            hole=0.3
        )
        return fig
    
    @staticmethod
    def create_kpi_cards(metrics):
        """Create KPI metric cards"""
        return {
            'Total Sales': f"{metrics['total_sales']:,.0f} Bales",
            'Total Returns': f"{metrics['total_returns']:,.0f} Bales",
            'Net Sales': f"{metrics['net_sales']:,.0f} Bales",
            'Return Rate': f"{metrics['return_rate']:.2%}",
            'Avg Sales/Store': f"{metrics['average_sales_per_store']:,.0f} Bales"
        }
