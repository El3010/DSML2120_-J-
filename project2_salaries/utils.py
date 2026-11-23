"""Shared helpers: data loading (cached), labels, color palette, and sidebar branding.

Every page imports from here so branding, colors, and cleaning stay consistent.
"""
from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# --------------------------------------------------------------------------------------
# Paths & constants
# --------------------------------------------------------------------------------------
ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "ds_salaries.csv"
ASSETS = ROOT / "assets"

AUTHOR = "Jose Lopez"
TAGLINE = "Data Visualization Portfolio · MSU Denver"
EMAIL = "your.email@example.com"            # TODO: replace with your email
LINKEDIN = "https://www.linkedin.com/in/your-profile"  # TODO: replace with your LinkedIn
GITHUB = "https://github.com/your-username"            # TODO: replace with your GitHub

DATA_NAME = "Data Science Job Salaries"
DATA_URL = "https://www.kaggle.com/datasets/ruchi798/data-science-job-salaries"
DATA_ORIGIN = "Kaggle (Ruchi Bhatia), aggregated from ai-jobs.net salary survey"
SOURCE_CAPTION = f"Source: {DATA_NAME} — {DATA_ORIGIN}."

# Okabe-Ito palette: designed to stay distinguishable for the common forms of color blindness.
OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]
PRIMARY = "#0072B2"
ACCENT = "#D55E00"

# Readable labels for the coded columns (ordered from junior to senior / small to large).
EXPERIENCE_LABELS = {"EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive"}
EXPERIENCE_ORDER = list(EXPERIENCE_LABELS.values())
EMPLOYMENT_LABELS = {"FT": "Full-time", "PT": "Part-time", "CT": "Contract", "FL": "Freelance"}
SIZE_LABELS = {"S": "Small (<50)", "M": "Medium (50–250)", "L": "Large (>250)"}
SIZE_ORDER = list(SIZE_LABELS.values())
REMOTE_LABELS = {0: "On-site (0%)", 50: "Hybrid (50%)", 100: "Fully remote (100%)"}
REMOTE_ORDER = list(REMOTE_LABELS.values())

# ISO-3166 alpha-2 codes that appear in the dataset -> country names (unknown codes stay as-is).
COUNTRIES = {
    "US": "United States", "GB": "United Kingdom", "CA": "Canada", "DE": "Germany",
    "IN": "India", "FR": "France", "ES": "Spain", "GR": "Greece", "JP": "Japan",
    "NL": "Netherlands", "PT": "Portugal", "AU": "Australia", "BR": "Brazil",
    "PK": "Pakistan", "AT": "Austria", "TR": "Turkey", "IT": "Italy", "PL": "Poland",
    "MX": "Mexico", "NG": "Nigeria", "DK": "Denmark", "BE": "Belgium", "CH": "Switzerland",
    "LU": "Luxembourg", "AE": "United Arab Emirates", "SG": "Singapore", "IE": "Ireland",
    "CN": "China", "RU": "Russia", "UA": "Ukraine", "VN": "Vietnam", "SI": "Slovenia",
    "CZ": "Czechia", "HU": "Hungary", "RO": "Romania", "CO": "Colombia", "CL": "Chile",
    "AR": "Argentina", "IL": "Israel", "KE": "Kenya", "NZ": "New Zealand", "EE": "Estonia",
    "HR": "Croatia", "MT": "Malta", "MY": "Malaysia", "PH": "Philippines", "IR": "Iran",
    "IQ": "Iraq", "DZ": "Algeria", "HN": "Honduras", "BG": "Bulgaria", "RS": "Serbia",
    "MD": "Moldova", "AS": "American Samoa", "JE": "Jersey", "PR": "Puerto Rico",
    "TN": "Tunisia", "BO": "Bolivia", "HK": "Hong Kong", "FI": "Finland", "SE": "Sweden",
    "NO": "Norway", "LT": "Lithuania", "LV": "Latvia", "ZA": "South Africa", "EG": "Egypt",
}


# --------------------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading salary data…")
def load_data(path: str = str(DATA_PATH)) -> pd.DataFrame:
    """Read the raw CSV once (cached) and return a cleaned DataFrame with readable labels."""
    df = pd.read_csv(path)

    # The 2022 Kaggle file ships with an unnamed index column; drop any such columns.
    df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

    # Drop exact duplicates and rows missing the fields every chart relies on.
    df = df.drop_duplicates().dropna(subset=["salary_in_usd", "experience_level", "company_size"])

    df["experience"] = pd.Categorical(
        df["experience_level"].map(EXPERIENCE_LABELS), categories=EXPERIENCE_ORDER, ordered=True
    )
    df["employment"] = df["employment_type"].map(EMPLOYMENT_LABELS).fillna(df["employment_type"])
    df["company_size_label"] = pd.Categorical(
        df["company_size"].map(SIZE_LABELS), categories=SIZE_ORDER, ordered=True
    )
    df["remote"] = pd.Categorical(
        df["remote_ratio"].map(REMOTE_LABELS), categories=REMOTE_ORDER, ordered=True
    )
    df["company_country"] = df["company_location"].map(COUNTRIES).fillna(df["company_location"])
    df["residence_country"] = df["employee_residence"].map(COUNTRIES).fillna(df["employee_residence"])
    df["salary_k"] = df["salary_in_usd"] / 1000  # thousands of USD for compact axes
    return df.reset_index(drop=True)


def data_file_timestamp() -> str:
    """Last-modified time of the CSV, used for the 'last refreshed' line."""
    ts = datetime.fromtimestamp(DATA_PATH.stat().st_mtime)
    return ts.strftime("%Y-%m-%d %H:%M")


def get_data() -> pd.DataFrame:
    """Load data or stop the page with a helpful message if the CSV is missing."""
    if not DATA_PATH.exists():
        st.error(
            "**Data file not found.** Download `ds_salaries.csv` from "
            f"[Kaggle]({DATA_URL}) and save it as `data/ds_salaries.csv`."
        )
        st.stop()
    return load_data()


# --------------------------------------------------------------------------------------
# Formatting & layout helpers
# --------------------------------------------------------------------------------------
def usd(x: float) -> str:
    """Format a number as whole US dollars, e.g. $101,570."""
    return f"${x:,.0f}"


def pct(x: float) -> str:
    return f"{x:.0%}"


def style_fig(fig, height: int = 420):
    """Apply one consistent, high-contrast look to every Plotly figure."""
    fig.update_layout(
        height=height,
        font=dict(size=14, color="#1F2937"),
        title=dict(font=dict(size=17)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=60, b=10),
        hoverlabel=dict(font_size=13),
        legend=dict(title_font=dict(size=13)),
    )
    fig.update_xaxes(showgrid=False, linecolor="#9CA3AF", ticks="outside")
    fig.update_yaxes(gridcolor="#E5E7EB", linecolor="#9CA3AF", zeroline=False)
    return fig


def img_with_alt(path: Path, alt: str, width: int = 220) -> str:
    """Return an <img> tag with real alt-text (st.image has no alt attribute)."""
    b64 = base64.b64encode(path.read_bytes()).decode()
    return (
        f'<img src="data:image/png;base64,{b64}" alt="{alt}" width="{width}" '
        'style="border-radius:50%;display:block;margin:auto;">'
    )


def sidebar_branding() -> None:
    """Consistent name/contact block shown in the sidebar of every page."""
    with st.sidebar:
        st.markdown(f"### {AUTHOR}")
        st.caption(TAGLINE)
        st.markdown(f"[LinkedIn]({LINKEDIN}) · [GitHub]({GITHUB}) · [Email](mailto:{EMAIL})")
        st.divider()


def page_header(title: str, subtitle: str) -> None:
    st.title(title)
    st.caption(subtitle)


ETHICS_NOTE = (
    "**Ethics note.** This dataset includes real people, so results must be interpreted carefully. "
    "Because the salaries are self-reported to a public job-board survey (ai-jobs.net), they may include "
    "self-selection bias, over-represent U.S. and English-speaking respondents, and contain only a few "
    "records for some roles and countries, so they do not necessarily represent all data workers. "
    "The visualizations show patterns but should not be used to make individual pay judgments or broad generalizations."
)
