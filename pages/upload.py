import streamlit as st
import pandas as pd

def show():
    st.header("Data Upload")
    
    st.markdown("""
    Upload your Chapati order data in CSV format.
    """)
    
    # Option 1: Load pre-processed data
    st.subheader("Quick Load")
    
    if st.button("📊 Load October Dataset"):
        try:
            df = pd.read_csv('data/october_dataset_transformed.csv')
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
            
            st.dataframe(df.head(10), use_container_width=True)
            st.info("Ready to analyze. Go to Dashboard!")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # Option 2: Upload custom CSV
    st.subheader("Upload Custom Data")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Try with multi-level headers first
            try:
                df = pd.read_csv(uploaded_file, header=[0, 1, 2])
                file_format = "Raw (Multi-level headers)"
                is_raw = True
            except:
                # Try simple header
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file)
                file_format = "Transformed"
                is_raw = False
            
            # Check if already transformed
            if 'M1_Returns' in df.columns and 'M1_Sales' in df.columns:
                df_processed = df
                format_type = "Transformed"
            elif is_raw:
                # Transform raw format
                data_cols = []
                for i, col in enumerate(df.columns):
                    if 'Sum of' in str(col):
                        data_cols.append(i)
                
                df_clean = df.iloc[:, [0] + data_cols].copy()
                
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
                
                if len(new_columns) != len(df_clean.columns):
                    new_columns = new_columns[:len(df_clean.columns)]
                
                df_clean.columns = new_columns
                cols_to_keep = [c for c in df_clean.columns if not c.startswith('Other_')]
                df_clean = df_clean[cols_to_keep]
                
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
            
            st.session_state.data = df_processed
            
            st.success(f"✅ Data loaded ({format_type})")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records", f"{len(df_processed):,}")
            with col2:
                st.metric("Columns", len(df_processed.columns))
            with col3:
                branches = df_processed['Branch'].nunique()
                st.metric("Branches", branches)
            with col4:
                numeric = len([c for c in df_processed.columns if df_processed[c].dtype in ['int64', 'float64']])
                st.metric("Metrics", numeric)
            
            st.dataframe(df_processed.head(10), use_container_width=True)
            st.info("Ready to analyze. Go to Dashboard!")
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
