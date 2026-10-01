import streamlit as st
import pandas as pd

def show():
    st.header("Upload Data")
    uploaded_file = st.file_uploader("Select CSV file", type=['csv'], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, header=3)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            df = df.rename(columns={df.columns[0]: 'Branch'})
            st.session_state.data = df
            st.success("Data uploaded successfully")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Rows", len(df))
            col2.metric("Columns", len(df.columns))
            col3.metric("Branches", df['Branch'].nunique())
            col4.metric("Weeks", (len(df.columns) - 1) // 2)
        except Exception as e:
            st.error(f"Error: {str(e)}")
