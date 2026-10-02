import streamlit as st
import styles
from pages import upload, dashboard, store_analysis, relationship_analysis, order_recommendations, ask_questions

st.set_page_config(page_title="Chapati Analytics", layout="wide")
styles.apply_styles()

st.title("Chapati Analytics")
st.caption("Data-driven order optimization for retail distribution")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Select", ["Upload Data", "Dashboard", "Store Analysis", "Relationship Analysis", "Order Recommendations", "Ask Questions"], label_visibility="collapsed")

if 'data' not in st.session_state:
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
elif page == "Ask Questions":
    ask_questions.show()

st.sidebar.markdown("---")
st.sidebar.caption("Chapati Analytics v34.0 | AI-Powered")
