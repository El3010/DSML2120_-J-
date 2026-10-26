import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------- Change this title to test live updates ----------
CHART_TITLE = "How I Spend a Typical Day (hours)"

st.title("🥧 Interactive Pie Chart")
st.write("This page reads `data/pie_demo.csv`. Edit the CSV on GitHub and refresh to see the chart update.")


def find_csv(filename="pie_demo.csv"):
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir.parent / "data" / filename,  # streamlit_DSML/data/pie_demo.csv
        Path("data") / filename,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


csv_path = find_csv()
if csv_path is None:
    st.error("Couldn't find `data/pie_demo.csv`. Make sure the `data` folder is next to `app.py`.")
    st.stop()

# Not cached on purpose, so edits to the CSV show up after a refresh
df = pd.read_csv(csv_path)

# ---------- Widgets ----------
chosen = st.multiselect(
    "Categories to include",
    options=df["Category"].tolist(),
    default=df["Category"].tolist(),
)
donut = st.slider("Donut hole size", 0.0, 0.7, 0.3, 0.05)

view = df[df["Category"].isin(chosen)]

if view.empty:
    st.warning("Pick at least one category.")
else:
    fig = px.pie(view, names="Category", values="Value", title=CHART_TITLE, hole=donut)
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, width="stretch")

with st.expander("See the raw data"):
    st.dataframe(df, width="stretch")
