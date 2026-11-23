"""Professional bio page: summary, photo with alt-text, highlights, visualization philosophy."""
import streamlit as st

from utils import ASSETS, AUTHOR, EMAIL, GITHUB, LINKEDIN, img_with_alt, page_header, sidebar_branding

st.set_page_config(page_title=f"Bio · {AUTHOR}", page_icon="📄", layout="wide")
sidebar_branding()
page_header("📄 Professional Bio", "Who I am and how I approach data visualization")

left, right = st.columns([1, 2.4], gap="large")

with left:
    # TODO: replace assets/profile.png with your own photo (square works best) and update the alt-text.
    alt = "Placeholder avatar: the initials JL in white on a blue circle"
    st.markdown(img_with_alt(ASSETS / "profile.png", alt), unsafe_allow_html=True)
    st.caption(f"{AUTHOR} — Computing student, MSU Denver")
    st.markdown(f"📧 [{EMAIL}](mailto:{EMAIL})  \n🔗 [LinkedIn]({LINKEDIN})  \n💻 [GitHub]({GITHUB})")

with right:
    st.markdown("### Summary")
    st.markdown(
        """
I'm a computing student at Metropolitan State University of Denver who enjoys turning messy data
into clear, honest visuals that help people make decisions. My toolkit centers on **Python** —
Pandas for cleaning and analysis, Plotly for interactive charts, and Streamlit for shipping
small data apps. Alongside data visualization, my coursework covers networking and distributed
computing, applied linear algebra, and computing ethics, which shapes how I think about data at
scale and its impact on people. I'm especially interested in labor-market and tech-industry data,
like the salary analysis in this app.
"""
    )

    st.markdown("### Highlights")
    st.markdown(
        """
- 🐍 **Python data stack:** Pandas, NumPy, Plotly Express, Streamlit (with caching and multipage apps)
- 📊 **Data visualization coursework:** paper prototyping, chart selection, and dashboard design (Labs 4.1–4.3)
- 🧮 **Quantitative foundation:** applied linear algebra (MTH 3130) and networking & distributed computing (CS 3700)
- ⚖️ **Ethics in computing:** applied the ACM Code of Ethics while designing an AI study-buddy project (PHI 3370)
- 🚀 **Shipped this app:** a reproducible, deployed portfolio with an EDA gallery and an interactive dashboard
"""
    )

st.markdown("### My visualization philosophy")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown("**Clarity first**")
        st.write(
            "Every chart answers one question. I pick the simplest chart that answers it, label axes "
            "with units, and remove decoration that doesn't carry information."
        )
with c2:
    with st.container(border=True):
        st.markdown("**Accessible by default**")
        st.write(
            "I use color-blind-safe palettes (Okabe-Ito), high contrast, alt-text, and never rely on "
            "color alone — hover text and labels repeat the key values."
        )
with c3:
    with st.container(border=True):
        st.markdown("**Honest and ethical**")
        st.write(
            "Scales start where they should, small samples get flagged, and I describe what the data "
            "shows — not causes it can't prove. Data about people deserves extra care."
        )
