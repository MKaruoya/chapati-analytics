import streamlit as st
import pandas as pd
import styles
from pages import upload, dashboard, store_analysis, relationship_analysis, order_recommendations

st.set_page_config(page_title="Chapati Analytics", layout="wide")

styles.apply_styles()

st.title("Chapati Analytics")

st.caption("Data-driven order optimization for retail distribution")

st.sidebar.header("Navigation")

page = st.sidebar.radio("Select", ["Upload Data", "Dashboard", "Store Analysis", "Relationship Analysis", "Order Recommendations"], label_visibility="collapsed")
# Load data
if 'data' not in st.session_state:
    try:
        # Load October data (transformed - March to October)
        df_oct = pd.read_csv('data/october_dataset_transformed.csv')
        st.session_state.data = df_oct
    except FileNotFoundError:
        st.warning("October data not found. Please run transform_october.py first")
        st.session_state.data = None


if page == "Upload Data":
    upload.show()

elif page == "Dashboard":
    dashboard.show()

elif page == "Store Analysis":
    store_analysis.show()

elif page == "Relationship Analysis":
    relationship_analysis.show()

elif page == "Order Recommendations":
    order_recommendations.show()

st.sidebar.markdown("---")

st.sidebar.caption("Chapati Analytics v35.0")
