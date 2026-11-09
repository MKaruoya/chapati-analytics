import streamlit as st
import pandas as pd
import styles
from pages import upload, dashboard, store_analysis

st.set_page_config(page_title="Chapati Analytics", layout="wide")

styles.apply_styles()

st.title("Chapati Analytics")
st.caption("Data-driven order optimization for retail distribution")

# Sidebar Navigation
st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Select Page",
    ["Upload Data", "Dashboard", "Store Analysis"],
    label_visibility="collapsed"
)

# Load data
if 'data' not in st.session_state:
    try:
        # Load October data (corrected - all weeks with complete data)
        df = pd.read_csv('data/october_weekly_correct.csv')
        st.session_state.data = df
    except FileNotFoundError:
        st.warning("October data not found. Please upload data first.")
        st.session_state.data = None

# Route to pages
if page == "Upload Data":
    upload.show()
elif page == "Dashboard":
    dashboard.show()
elif page == "Store Analysis":
    store_analysis.show()

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("Chapati Analytics v1.0")
