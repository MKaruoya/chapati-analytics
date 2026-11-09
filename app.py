import streamlit as st
import pandas as pd
import styles
from pages import upload, dashboard, store_analysis

st.set_page_config(page_title="Chapati Analytics", layout="wide")

styles.apply_styles()

# Load data
if 'data' not in st.session_state:
    try:
        df = pd.read_csv('data/october_weekly_correct.csv')
        st.session_state.data = df
    except FileNotFoundError:
        st.session_state.data = None

# Main title
st.title("Chapati Analytics")
st.caption("Data-driven order optimization for retail distribution")

# Navigation
st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Select Page",
    ["Upload Data", "Dashboard", "Store Analysis"],
    label_visibility="collapsed"
)

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
