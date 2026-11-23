"""Home page: overview, headline numbers, and links to every section."""
import streamlit as st

from utils import (
    AUTHOR, DATA_NAME, DATA_URL, ETHICS_NOTE, TAGLINE, get_data, sidebar_branding, usd,
)

st.set_page_config(page_title=f"{AUTHOR} · Data Viz Portfolio", page_icon="📊", layout="wide")
sidebar_branding()

st.title(f"{AUTHOR}")
st.subheader("Data Visualization Portfolio & Salary Analytics")
st.caption(TAGLINE)

df = get_data()

st.markdown(
    f"""
Welcome! This app is both my professional portfolio and a small analytics product built on the
**[{DATA_NAME}]({DATA_URL})** dataset ({len(df):,} salary records for data-related jobs,
{df['work_year'].min()}–{df['work_year'].max()}).

The guiding question across the app: **what is associated with higher pay in data jobs —
experience, company size, location, or remote work?**
"""
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Salary records", f"{len(df):,}")
c2.metric("Median salary (USD)", usd(df["salary_in_usd"].median()))
c3.metric("Distinct job titles", df["job_title"].nunique())
c4.metric("Company countries", df["company_location"].nunique())

st.markdown("### Explore the app")
cols = st.columns(4)
pages = [
    ("pages/1_Bio.py", "📄 Bio", "Who I am, my tools, and my visualization philosophy."),
    ("pages/2_Charts_Gallery.py", "📊 EDA Gallery", "Four chart types, each with a reading guide and observations."),
    ("pages/3_Dashboard.py", "📈 Dashboard", "Filter the data and watch KPIs and linked charts update."),
    ("pages/4_Future_Work.py", "🧭 Future Work", "Next steps and how the design evolved from my paper prototype."),
]
for col, (path, label, desc) in zip(cols, pages):
    with col:
        with st.container(border=True):
            st.page_link(path, label=label)
            st.caption(desc)

st.info(ETHICS_NOTE)
