import streamlit as st
import pandas as pd
from modules.data_loader import load_dataset, get_dataset_summary, get_unique_stores
from modules.data_processor import DataProcessor
from modules.analysis_engine import AnalysisEngine
from modules.visualization import Visualizer
from modules.ai_qa_system import AIQASystem
import config

# Page configuration
st.set_page_config(**config.PAGE_CONFIG)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'ai_system' not in st.session_state:
    st.session_state.ai_system = None

# Load data
st.title("🥙 Chapati Analytics")
st.markdown("Comprehensive Sales & Distribution Analysis Platform")

# Sidebar
with st.sidebar:
    st.header("📊 Navigation")
    page = st.radio("Select Page", ["Dashboard", "Store Analysis", "Q&A System", "Recommendations"])
    
    st.divider()
    st.subheader("📁 Data Info")
    
    # Load dataset
    df = load_dataset()
    if df is not None:
        st.session_state.df = df
        summary = get_dataset_summary(df)
        
        st.metric("Total Rows", summary['total_rows'])
        st.metric("Stores", summary['stores'])
        st.metric("Branches", summary['branches'])
        st.metric("Products", summary['products'])
        st.caption(f"Last Updated: {summary['last_updated']}")

# Main content
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Process data
    processor = DataProcessor(df)
    processed_df = processor.process()
    
    # Initialize analysis engine
    analysis_engine = AnalysisEngine(processed_df)
    
    # Initialize AI system
    if st.session_state.ai_system is None:
        st.session_state.ai_system = AIQASystem()
        metrics = analysis_engine.calculate_sales_metrics()
        summary = get_dataset_summary(df)
        st.session_state.ai_system.initialize_system_prompt(summary, metrics)
    
    # PAGE 1: DASHBOARD
    if page == "Dashboard":
        st.header("📈 Dashboard")
        
        # KPI Cards
        metrics = analysis_engine.calculate_sales_metrics()
        kpi_cards = Visualizer.create_kpi_cards(metrics)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Sales", kpi_cards['Total Sales'])
        with col2:
            st.metric("Total Returns", kpi_cards['Total Returns'])
        with col3:
            st.metric("Net Sales", kpi_cards['Net Sales'])
        with col4:
            st.metric("Return Rate", kpi_cards['Return Rate'])
        with col5:
            st.metric("Avg/Store", kpi_cards['Avg Sales/Store'])
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            trends = analysis_engine.calculate_monthly_trends()
            fig_trend = Visualizer.create_sales_trend_chart(trends)
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            performance = analysis_engine.get_store_performance_ranking()
            fig_performance = Visualizer.create_store_performance_chart(performance.head(10))
            st.plotly_chart(fig_performance, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_sales = analysis_engine.get_product_performance_ranking()['sales']
            fig_product = Visualizer.create_product_mix_chart(product_sales)
            st.plotly_chart(fig_product, use_container_width=True)
        
        with col2:
            st.subheader("Top 10 Stores")
            top_stores = analysis_engine.get_store_performance_ranking().head(10)
            st.dataframe(top_stores, use_container_width=True)
    
    # PAGE 2: STORE ANALYSIS
    elif page == "Store Analysis":
        st.header("🏪 Store Analysis")
        
        stores = get_unique_stores(df)
        selected_store = st.selectbox("Select Store", stores)
        
        if selected_store:
            store_data = processed_df[processed_df['store'] == selected_store]
            
            col1, col2, col3, col4 = st.columns(4)
            
            sales_cols = [col for col in store_data.columns if 'Sum of Net Bales Sales' in col]
            returns_cols = [col for col in store_data.columns if 'Sum of Bales Returns' in col]
            
            total_sales = store_data[sales_cols].sum().sum()
            total_returns = store_data[returns_cols].sum().sum()
            
            with col1:
                st.metric("Total Sales", f"{total_sales:,.0f}")
            with col2:
                st.metric("Total Returns", f"{total_returns:,.0f}")
            with col3:
                st.metric("Branches", store_data['branch'].nunique())
            with col4:
                st.metric("Products", store_data['product'].nunique())
            
            st.divider()
            
            # Store-specific charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Sales by Product")
                products = store_data.groupby('product')[sales_cols].sum().sum(axis=1).sort_values(ascending=False)
                st.bar_chart(products)
            
            with col2:
                st.subheader("Sales by Branch (Top 10)")
                branches = store_data.groupby('branch')[sales_cols].sum().sum(axis=1).sort_values(ascending=False).head(10)
                st.bar_chart(branches)
            
            # Detailed table
            st.subheader("Detailed Data")
            st.dataframe(store_data, use_container_width=True)
    
    # PAGE 3: Q&A SYSTEM
    elif page == "Q&A System":
        st.header("🤖 AI Q&A System")
        st.markdown("Ask questions about your sales data and get AI-powered insights")
        
        # Display conversation history
        for message in st.session_state.ai_system.get_conversation_history():
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
        
        # Input for new question
        user_question = st.chat_input("Ask a question about your data...")
        
        if user_question:
            st.chat_message("user").write(user_question)
            
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.ai_system.ask_question(user_question)
            
            st.chat_message("assistant").write(response)
        
        # Clear history button
        if st.button("Clear Conversation"):
            st.session_state.ai_system.clear_history()
            st.rerun()
        
        # Example questions
        st.divider()
        st.subheader("💡 Example Questions")
        examples = [
            "Which stores have the highest return rates?",
            "What's the sales trend for each product?",
            "Which branches are underperforming?",
            "How can we reduce returns?",
            "What's the product mix by sales?"
        ]
        for example in examples:
            st.caption(f"• {example}")
    
    # PAGE 4: RECOMMENDATIONS
    elif page == "Recommendations":
        st.header("💡 Recommendations & Insights")
        
        metrics = analysis_engine.calculate_sales_metrics()
        
        # Alerts
        st.subheader("🚨 Key Alerts")
        
        if metrics['return_rate'] > 0.15:
            st.warning(f"⚠️ Overall return rate is {metrics['return_rate']:.2%} - investigate quality issues")
        
        high_returns = analysis_engine.identify_high_returns()
        if high_returns:
            st.error(f"🔴 {len(high_returns)} product-store combinations have high return rates (>15%)")
        
        # Performance rankings
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top 10 Performing Stores")
            top_stores = analysis_engine.get_store_performance_ranking().head(10)
            st.dataframe(top_stores, use_container_width=True)
        
        with col2:
            st.subheader("📊 Top 10 Performing Products")
            top_products = analysis_engine.get_product_performance_ranking().head(10)
            st.dataframe(top_products, use_container_width=True)
        
        st.divider()
        
        st.subheader("📈 Recommendations")
        st.info("""
        **Based on the analysis:**
        
        1. **Focus on High-Return Products** - Investigate quality issues for products with return rates >15%
        2. **Support Low-Performing Stores** - Provide additional training and resources
        3. **Replicate Success** - Study top-performing stores and branches for best practices
        4. **Monitor Trends** - Track monthly trends to identify seasonal patterns
        5. **Optimize Inventory** - Adjust stock levels based on sales patterns
        """)

else:
    st.error("❌ Unable to load dataset. Please check the data file path.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    Chapati Analytics v1.0 | Data Period: March - September 2024
</div>
""", unsafe_allow_html=True)
