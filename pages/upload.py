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
            # First, try to read as transformed format (simple header)
            df = pd.read_csv(uploaded_file)
            
            # Check if it's already the transformed October format
            if 'M1_Returns' in df.columns and 'M1_Sales' in df.columns:
                st.success("✅ Data uploaded successfully (Transformed format)")
                st.session_state.data = df
            else:
                # If not, it might be the raw October file with multi-level headers
                # Reset file pointer and try again
                uploaded_file.seek(0)
                
                try:
                    # Try reading with multi-level headers
                    df = pd.read_csv(uploaded_file, header=[0, 1, 2])
                    
                    # This is the raw October format - need to transform it
                    st.info("ℹ️ Detected raw October format - transforming...")
                    
                    # Use the transformation logic
                    from utils import extract_outlet_name
                    
                    # Get the first column (Branch names)
                    branch_col = df.iloc[:, 0]
                    
                    # Extract only columns that contain "Sum of" (actual data columns)
                    data_cols = []
                    for i, col in enumerate(df.columns):
                        col_str = str(col)
                        if 'Sum of' in col_str:
                            data_cols.append(i)
                    
                    # Extract branch and data columns
                    df_clean = df.iloc[:, [0] + data_cols].copy()
                    
                    # Flatten the multi-index columns
                    new_columns = ['Branch']
                    month_map = {
                        'March': 1, 'April': 2, 'May': 3, 'June': 4,
                        'July': 5, 'August': 6, 'September': 7, 'October': 8
                    }
                    
                    for col in df_clean.columns[1:]:
                        col_str = str(col)
                        
                        # Find month
                        month_num = None
                        for month_name, num in month_map.items():
                            if month_name in col_str:
                                month_num = num
                                break
                        
                        # Find metric type
                        if month_num:
                            if 'Returns' in col_str:
                                new_columns.append(f'M{month_num}_Returns')
                            elif 'Sales' in col_str:
                                new_columns.append(f'M{month_num}_Sales')
                        else:
                            new_columns.append(str(col))
                    
                    df_clean.columns = new_columns
                    
                    # Remove the Total columns (last 2)
                    df_clean = df_clean.iloc[:, :-2]
                    
                    # Filter: Keep only rows that contain branch identifiers
                    df_clean['Branch'] = df_clean['Branch'].astype(str)
                    df_clean = df_clean[~df_clean['Branch'].str.contains('CHAPATI|SOKO|Row Labels|Unnamed|Column Labels', case=False, na=False)]
                    
                    # Remove rows with no branch name
                    df_clean = df_clean[df_clean['Branch'].notna()]
                    df_clean = df_clean[df_clean['Branch'] != '']
                    df_clean = df_clean[df_clean['Branch'].str.strip() != '']
                    
                    # Fill NaN with 0
                    df_clean = df_clean.fillna(0)
                    
                    # Reset index
                    df_clean = df_clean.reset_index(drop=True)
                    
                    df = df_clean
                    st.success("✅ Data uploaded and transformed successfully")
                    st.session_state.data = df
                    
                except Exception as e2:
                    st.error(f"❌ Could not parse file format: {str(e2)}")
                    return
            
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
            
            st.info("✅ Data is ready! Go to Dashboard to view analytics")
            
        except Exception as e:
            st.error(f"❌ Error uploading file: {str(e)}")
            st.info("Please make sure the file is a valid CSV with Chapati data")
