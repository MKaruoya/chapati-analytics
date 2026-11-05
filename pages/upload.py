import streamlit as st
import pandas as pd

def show():
    st.header("Data Upload")
    
    st.markdown("""
    Upload your Chapati order data in CSV format. The system supports both 
    transformed and raw data formats.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Try reading as simple format first
            df = pd.read_csv(uploaded_file)
            
            # Check if already transformed (has M1_Returns, M1_Sales, etc.)
            if 'M1_Returns' in df.columns and 'M1_Sales' in df.columns:
                df_processed = df
                format_type = "Transformed"
            else:
                # Try reading as raw format with multi-level headers
                uploaded_file.seek(0)
                df_raw = pd.read_csv(uploaded_file, header=[0, 1, 2])
                
                # Extract data columns (those containing "Sum of")
                data_col_indices = []
                for i, col in enumerate(df_raw.columns):
                    if 'Sum of' in str(col):
                        data_col_indices.append(i)
                
                # Get branch column and data columns
                df_extracted = df_raw.iloc[:, [0] + data_col_indices].copy()
                
                # Create new column names
                new_columns = ['Branch']
                month_map = {
                    'March': 1, 'April': 2, 'May': 3, 'June': 4,
                    'July': 5, 'August': 6, 'September': 7, 'October': 8
                }
                
                for col in df_extracted.columns[1:]:
                    col_str = str(col)
                    month_num = None
                    
                    # Find which month this column belongs to
                    for month_name, num in month_map.items():
                        if month_name in col_str:
                            month_num = num
                            break
                    
                    # Determine if it's Returns or Sales
                    if month_num:
                        if 'Returns' in col_str:
                            new_columns.append(f'M{month_num}_Returns')
                        elif 'Sales' in col_str:
                            new_columns.append(f'M{month_num}_Sales')
                
                # Trim to match actual columns (remove Total columns)
                new_columns = new_columns[:len(df_extracted.columns) - 2]
                df_extracted = df_extracted.iloc[:, :len(new_columns)]
                df_extracted.columns = new_columns
                
                # Clean branch names
                df_extracted['Branch'] = df_extracted['Branch'].astype(str)
                
                # Remove product rows and invalid entries
                invalid_patterns = ['CHAPATI', 'SOKO', 'Row Labels', 'Unnamed', 'Column Labels']
                mask = ~df_extracted['Branch'].str.contains('|'.join(invalid_patterns), case=False, na=False)
                df_extracted = df_extracted[mask]
                
                # Remove empty branches
                df_extracted = df_extracted[df_extracted['Branch'].notna()]
                df_extracted = df_extracted[df_extracted['Branch'] != '']
                df_extracted = df_extracted[df_extracted['Branch'].str.strip() != '']
                
                # Fill missing values
                df_extracted = df_extracted.fillna(0)
                df_extracted = df_extracted.reset_index(drop=True)
                
                df_processed = df_extracted
                format_type = "Raw (Auto-transformed)"
            
            # Store in session state
            st.session_state.data = df_processed
            
            # Display success message
            st.success(f"Data loaded successfully ({format_type} format)")
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Records", f"{len(df_processed):,}")
            
            with col2:
                st.metric("Columns", len(df_processed.columns))
            
            with col3:
                if 'Branch' in df_processed.columns:
                    branches = df_processed['Branch'].nunique()
                    st.metric("Branches", branches)
                else:
                    st.metric("Branches", "N/A")
            
            with col4:
                numeric_cols = [c for c in df_processed.columns if df_processed[c].dtype in ['int64', 'float64']]
                st.metric("Metrics", len(numeric_cols))
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(df_processed.head(10), use_container_width=True)
            
            st.info("Data is ready. Navigate to Dashboard to view analytics.")
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.caption("Please ensure the file is a valid CSV with Chapati order data.")
