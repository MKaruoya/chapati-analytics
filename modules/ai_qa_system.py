import streamlit as st
from openai import OpenAI
import config

class AIQASystem:
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.OPENAI_MODEL
        self.conversation_history = []
    
    def initialize_system_prompt(self, df_summary, metrics):
        """Initialize system prompt with dataset context"""
        self.system_prompt = f"""You are an expert data analyst for Chapati Analytics, a sales and distribution analysis platform for Chapati products in Kenya.

Dataset Context:
- Total Records: {df_summary['total_rows']}
- Stores: {df_summary['stores']}
- Branches: {df_summary['branches']}
- Products: {df_summary['products']}
- Date Range: {df_summary['date_range']}

Current Metrics:
- Total Sales: {metrics['total_sales']:,.0f} Bales
- Total Returns: {metrics['total_returns']:,.0f} Bales
- Return Rate: {metrics['return_rate']:.2%}

Your role is to:
1. Answer questions about sales performance, trends, and anomalies
2. Provide insights on store and product performance
3. Identify issues and recommend improvements
4. Explain data patterns and correlations
5. Help with business decisions based on data

Always be specific, data-driven, and actionable in your responses."""
    
    def ask_question(self, question):
        """Send question to GPT-4 and get response"""
        try:
            self.conversation_history.append({
                "role": "user",
                "content": question
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            assistant_message = response.choices[0].message.content
            
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_conversation_history(self):
        """Return conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
