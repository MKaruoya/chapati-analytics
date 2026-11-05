import streamlit as st
import pandas as pd

def show():
    st.header("Data Upload")
    
    st.markdown("""
    Upload your Chapati order data in Excel format (.xlsx or .xls). 
    CSV files are also supported as a fallback.
    """)
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['xlsx', 'xls', 'csv'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Determine file type
            file_name = uploaded_file.name.lower()
            
            if file_name.endswith(('.xlsx', '.xls')):
                # Read Excel with multi-level headers
                try:
                    df = pd.read_excel(uploaded_file, header=[0, 1, 2])
                    file_format = "Excel (Raw)"
                    is_raw = True
                except:
                    # Try simple header
                    uploaded_file.seek(0)
                    df = pd.read_excel(uploaded_file)
                    file_format = "Excel (Transformed)"
                    is_raw = False
            
            elif file_name.endswith('.csv'):
                # Read CSV with multi-level headers
                try:
                    df = pd.read_csv(uploaded_file, header=[0, 1, 2])
                    file_format = "CSV (Raw)"
                    is_raw = True
                except:
                    # Try simple header
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file)
                    file_format = "CSV (Transformed)"
                    is_raw = False
            else:
                st.error("Unsupported file format")
                return
            
            # Check if already transformed
            if 'M1_Returns' in df.columns and 'M1_Sales' in df.columns:
                df_processed = df
                format_type = "Transformed"
            elif is_raw:
                # Transform raw format
                branch_col = df.iloc[:, 0]
                
                # Extract data columns (Sum of columns)
                data_cols = []
                for i, col in enumerate(df.columns):
                    if 'Sum of' in str(col):
                        data_cols.append(i)
                
                df_clean = df.iloc[:, [0] + data_cols].copy()
                
                # Flatten columns
                new_columns = ['Branch']
                month_map = {
                    'March': 1, 'April': 2, 'May': 3, 'June': 4,
                    'July': 5, 'August': 6, 'September': 7, 'October': 8
                }
                
                for col in df_clean.columns[1:]:
                    col_str = str(col)
                    month_num = None
                    
                    for month_name, num in month_map.items():
                        if month_name in col_str:
                            month_num = num
                            break
                    
                    if month_num:
                        if 'Returns' in col_str:
                            new_columns.append(f'M{month_num}_Returns')
                        elif 'Sales' in col_str:
                            new_columns.append(f'M{month_num}_Sales')
                    else:
                        new_columns.append(f'Other_{len(new_columns)}')
                
                # Ensure column count matches
                if len(new_columns) != len(df_clean.columns):
                    new_columns = new_columns[:len(df_clean.columns)]
                
                df_clean.columns = new_columns
                
                # Remove Other columns
                cols_to_keep = [c for c in df_clean.columns if not c.startswith('Other_')]
                df_clean = df_clean[cols_to_keep]
                
                # Filter branches
                df_clean['Branch'] = df_clean['Branch'].astype(str)
                df_clean = df_clean[~df_clean['Branch'].str.contains(
                    'CHAPATI|SOKO|Row Labels|Unnamed|Column Labels', 
                    case=False, 
                    na=False
                )]
                
                df_clean = df_clean[df_clean['Branch'].notna()]
                df_clean = df_clean[df_clean['Branch'] != '']
                df_clean = df_clean[df_clean['Branch'].str.strip() != '']
                
                df_clean = df_clean.fillna(0)
                df_clean = df_clean.reset_index(drop=True)
                
                df_processed = df_clean
                format_type = "Raw (Auto-transformed)"
            else:
                df_processed = df
                format_type = "Transformed"
            
            # Store in session
            st.session_state.data = df_processed
            
            # Display summary
            st.success(f"Data loaded successfully ({file_format} - {format_type})")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Records", f"{len(df_processed):,}")
            
            with col2:
                st.metric("Columns", len(df_processed.columns))
            
            with col3:
                branches = df_processed['Branch'].nunique() if 'Branch' in df_processed.columns else 0
                st.metric("Branches", branches)
            
            with col4:
                numeric = len([c for c in df_processed.columns if df_processed[c].dtype in ['int64', 'float64']])
                st.metric("Metrics", numeric)
            
            # Data preview
            st.subheader("Data Preview")
            st.dataframe(df_processed.head(10), use_container_width=True)
            
            st.info("Data is ready. Navigate to Dashboard to view analytics.")
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.caption("Please ensure the file is a valid Excel or CSV with Chapati order data.")
