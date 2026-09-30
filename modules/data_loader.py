import streamlit as st
import pandas as pd
from datetime import datetime
import config

@st.cache_resource
def load_dataset():
    """Load and cache the Chapati dataset"""
    try:
        df = pd.read_csv(config.DATA_FILE)
        return df
    except FileNotFoundError:
        st.error(f"❌ Dataset not found at {config.DATA_FILE}")
        return None

@st.cache_data(ttl=config.CACHE_DURATION)
def get_dataset_summary(df):
    """Get dataset summary statistics"""
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "date_range": config.DATE_RANGE,
        "stores": df['Customer Parent Name'].nunique() if 'Customer Parent Name' in df.columns else 0,
        "branches": df['Customer Parent_Branch'].nunique() if 'Customer Parent_Branch' in df.columns else 0,
        "products": df['Item Description'].nunique() if 'Item Description' in df.columns else 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@st.cache_data(ttl=config.CACHE_DURATION)
def get_unique_stores(df):
    """Get list of unique stores"""
    return sorted([x for x in df['Customer Parent Name'].unique() if pd.notna(x)])

@st.cache_data(ttl=config.CACHE_DURATION)
def get_unique_branches(df):
    """Get list of unique branches"""
    return sorted([x for x in df['Customer Parent_Branch'].unique() if pd.notna(x)])

@st.cache_data(ttl=config.CACHE_DURATION)
def get_unique_products(df):
    """Get list of unique products"""
    return sorted([x for x in df['Item Description'].unique() if pd.notna(x)])
