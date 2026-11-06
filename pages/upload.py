import streamlit as st
import pandas as pd

def show():
    st.header("Data Upload")
    
    st.markdown("""
    Load your Chapati order data to begin analysis.
    """)
    
    # Dataset selection
    st.subheader("Select Dataset")
    dataset_choice = st.radio(
        "Choose which dataset to load:",
        [
            "October Dataset (with Gross Sales)",
            "October Dataset (Legacy)"
        ],
        label_visibility="collapsed"
    )
    
    if st.button("📊 Load Dataset", use_container_width=True):
        try:
            if dataset_choice == "October Dataset (with Gross Sales)":
                df = pd.read_csv('data/october_dataset_with_gross.csv')
                dataset_name = "October Dataset (with Gross Sales)"
            else:
                df = pd.read_csv('data/october_dataset_transformed.csv')
                dataset_name = "October Dataset (Legacy)"
            
            st.session_state.data = df
            st.success(f"✅ {dataset_name} loaded!")
            
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
