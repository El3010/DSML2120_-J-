"""Entry point / router. Defines the sidebar navigation for the multipage app."""
import streamlit as st

pages = [
    st.Page("home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/1_📄_Bio.py", title="Bio", icon="📄"),
    st.Page("pages/2_📊_Charts_Gallery.py", title="EDA Gallery", icon="📊"),
    st.Page("pages/3_📈_Dashboard.py", title="Dashboard", icon="📈"),
    st.Page("pages/4_🧭_Future_Work.py", title="Future Work", icon="🧭"),
]
st.navigation(pages).run()
