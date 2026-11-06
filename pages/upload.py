import streamlit as st
import pandas as pd
import os

def show():
    st.header("Data Upload")
    
    st.markdown("""
    Load your Chapati order data to begin analysis.
    """)
    
    if st.button("📊 Load October Dataset", use_container_width=True):
        try:
            file_path = os.path.join('data', 'october_dataset_with_gross.csv')
            
            if not os.path.exists(file_path):
                st.error(f"File not found: {file_path}")
                st.info("Available files in data folder:")
                if os.path.exists('data'):
                    st.write(os.listdir('data'))
                return
            
            df = pd.read_csv(file_path)
            st.session_state.data = df
            st.success("✅ October dataset loaded!")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records", f"{len(df):,}")
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                branches = df['Branch'].nunique()
                st.metric("Branches", branches)
            with col4:
                numeric = len([c for c in df.columns if df[c].dtype in ['int64', 'float64']])
                st.metric("Metrics", numeric)
            
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            st.info("✨ Data is ready! Navigate to **Dashboard** to view analytics.")
            
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
