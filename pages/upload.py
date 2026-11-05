import streamlit as st
import pandas as pd

def show():
    st.header("Upload Data")
    st.caption("Upload a CSV file with Chapati order data")
    
    uploaded_file = st.file_uploader(
        "Select CSV file", 
        type=['csv'], 
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Try to read the file
            df = pd.read_csv(uploaded_file)
            
            # Check if it's the transformed October format (has M1_Returns, M1_Sales, etc.)
            if 'M1_Returns' in df.columns and 'M1_Sales' in df.columns:
                # Already transformed format
                st.success("✅ Data uploaded successfully (Transformed format)")
            else:
                # Try old format with header=3
                df = pd.read_csv(uploaded_file, header=3)
                df.columns = df.columns.str.strip()
                df = df.loc[:, ~df.columns.str.contains('Unnamed')]
                df = df.rename(columns={df.columns[0]: 'Branch'})
                st.success("✅ Data uploaded successfully (Legacy format)")
            
            # Store in session state
            st.session_state.data = df
            
            # Display metrics
            st.subheader("📊 Data Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Rows", len(df))
            
            with col2:
                st.metric("Columns", len(df.columns))
            
            with col3:
                if 'Branch' in df.columns:
                    st.metric("Branches", df['Branch'].nunique())
                else:
                    st.metric("Branches", "N/A")
            
            with col4:
                numeric_cols = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]
                st.metric("Numeric Cols", len(numeric_cols))
            
            # Show preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
            st.info("Please make sure the file is a valid CSV")
