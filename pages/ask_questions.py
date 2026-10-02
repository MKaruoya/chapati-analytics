import streamlit as st
import pandas as pd
from openai import OpenAI

def show():
    st.header("Ask Questions")
    st.caption("Ask natural language questions about your Chapati data")
    
    if st.session_state.data is None:
        st.warning("Please upload data first")
    else:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
            if not api_key:
                st.error("OpenAI API key not configured. Please add OPENAI_API_KEY to secrets.")
                return
            
            client = OpenAI(api_key=api_key)
        except Exception as e:
            st.error(f"Error initializing OpenAI: {str(e)}")
            return
        
        df = st.session_state.data.copy()
        
        all_branches = df['Branch'].dropna().unique()
        valid_branches = [name for name in all_branches if isinstance(name, str) and '-' in name and 'CHAPATI' not in name.upper()]
        
        data_summary = f"Dataset has {len(valid_branches)} branches with weekly Net Sales and Returns data."
        
        st.subheader("Your Question")
        question = st.text_area(
            "Ask a question about the data:",
            placeholder="e.g., Which branches have the highest return rates?",
            height=100,
            label_visibility="collapsed"
        )
        
        if st.button("Get Answer", type="primary"):
            if not question.strip():
                st.warning("Please enter a question")
            else:
                with st.spinner("Analyzing data..."):
                    try:
                        context = f"""You are a data analysis expert for a Chapati distribution company.
                        
{data_summary}

Available branches: {', '.join(valid_branches[:5])}{'...' if len(valid_branches) > 5 else ''}

User Question: {question}

Please provide a direct answer with specific insights."""
                        
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
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        st.subheader("Example Questions")
        examples = [
            "Which branches have the highest return rates?",
            "What's the average order quantity?",
            "Which branches are improving?",
            "Show branches with return rates above 20%",
            "What's the correlation between order size and returns?"
        ]
        
        col1, col2 = st.columns(2)
        for i, example in enumerate(examples):
            with col1 if i % 2 == 0 else col2:
                if st.button(example, key=f"example_{i}"):
                    st.session_state.selected_question = example
