import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
        * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        h1 { font-size: 24px; font-weight: 600; color: #1a1a1a; margin-bottom: 0.3rem; }
        h2 { font-size: 16px; font-weight: 600; color: #2c3e50; margin-top: 1.2rem; border-bottom: 2px solid #3498db; padding-bottom: 0.4rem; }
        h3 { font-size: 13px; font-weight: 600; color: #34495e; }
        .stMetric { background: #f8f9fa; padding: 0.8rem; border-radius: 4px; border-left: 3px solid #3498db; }
        .stDataFrame { font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)
