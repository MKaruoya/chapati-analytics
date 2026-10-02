import streamlit as st
import pandas as pd
import os
from openai import OpenAI

def show():
    st.header("Ask Questions")
    st.caption("Ask natural language questions about your Chapati data")
    
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        # Initialize OpenAI client
        api_key = st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            st.error("OpenAI API key not configured. Please add OPENAI_API_KEY to secrets.")
            return
        
        client = OpenAI(api_key=api_key)
        
        df = st.session_state.data.copy()
        
        # Prepare data summary for context
        all_branches = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_branches if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        data_summary = f"""
        Dataset Summary:
        - Total Branches: {len(valid_branches)}
        - Total Data Points: {len(df)}
        - Columns: {', '.join(df.columns.tolist())}
        - Data Structure: Each branch has weekly Net Sales and Returns data
        - Calculation: Order Qty = abs(Net Sales) + Returns, Return % = Returns / Order Qty
        """
        
        # Question input
        st.subheader("Your Question")
        question = st.text_area(
            "Ask a question about the data:",
            placeholder="e.g., Which branches have the highest return rates? What's the average order quantity?",
            height=100,
            label_visibility="collapsed"
        )
        
        if st.button("Get Answer", type="primary"):
            if not question.strip():
                st.warning("Please enter a question")
            else:
                with st.spinner("Analyzing data..."):
                    try:
                        # Prepare context for AI
                        context = f"""
                        You are a data analysis expert for a Chapati distribution company.
                        
                        {data_summary}
                        
                        Available Data:
                        - Branches: {', '.join(valid_branches[:10])}{'...' if len(valid_branches) > 10 else ''}
                        - Date Range: Multiple months of weekly data
                        - Metrics: Net Sales, Returns, Return Rate, Order Quantity
                        
                        Key Insights from Data:
                        - Total branches analyzed: {len(valid_branches)}
                        - Average return rate: {df.iloc[:, 2::2].sum().sum() / (df.iloc[:, 1::2].sum().sum() + df.iloc[:, 2::2].sum().sum()) * 100:.1f}% (approximate)
                        
                        User Question: {question}
                        
                        Please provide:
                        1. A direct answer to the question
                        2. Key insights from the data
                        3. Actionable recommendations if applicable
                        
                        Be specific with numbers and branch names when possible.
                        """
                        
                        # Call OpenAI API
                        response = client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=1024,
                            messages=[
                                {
                                    "role": "user",
                                    "content": context
                                }
                            ]
                        )
                        
                        answer = response.content[0].text
                        
                        # Display answer
                        st.subheader("Answer")
                        st.markdown(answer)
                        
                        # Add follow-up option
                        st.divider()
                        st.caption("Ask another question to dive deeper into the data")
                        
                    except Exception as e:
                        st.error(f"Error processing question: {str(e)}")
        
        # Example questions
        st.subheader("Example Questions")
        st.caption("Click any example to ask it")
        
        examples = [
            "Which branches have the highest return rates?",
            "What's the average order quantity across all branches?",
            "Which branches are improving over time?",
            "Show me branches with return rates above 20%",
            "What's the correlation between order size and returns?",
            "Which branches need immediate attention?",
            "What are the best performing branches?",
            "How many branches have return rates below 10%?"
        ]
        
        col1, col2 = st.columns(2)
        for i, example in enumerate(examples):
            with col1 if i % 2 == 0 else col2:
                if st.button(example, key=f"example_{i}"):
                    st.session_state.question = example
                    st.rerun()
        
        # If a question was selected from examples, process it
        if "question" in st.session_state and st.session_state.question:
            question = st.session_state.question
            st.session_state.question = None
            
            with st.spinner("Analyzing data..."):
                try:
                    context = f"""
                    You are a data analysis expert for a Chapati distribution company.
                    
                    {data_summary}
                    
                    Available Data:
                    - Branches: {', '.join(valid_branches[:10])}{'...' if len(valid_branches) > 10 else ''}
                    - Date Range: Multiple months of weekly data
                    - Metrics: Net Sales, Returns, Return Rate, Order Quantity
                    
                    User Question: {question}
                    
                    Please provide:
                    1. A direct answer to the question
                    2. Key insights from the data
                    3. Actionable recommendations if applicable
                    
                    Be specific with numbers and branch names when possible.
                    """
                    
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1024,
                        messages=[
                            {
                                "role": "user",
                                "content": context
                            }
                        ]
                    )
                    
                    answer = response.content[0].text
                    
                    st.subheader("Answer")
                    st.markdown(answer)
