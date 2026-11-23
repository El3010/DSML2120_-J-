"""Future Work page: concrete next steps and a reflection on the Lab 4.3 paper prototype."""
import streamlit as st

from utils import AUTHOR, page_header, sidebar_branding

st.set_page_config(page_title=f"Future Work · {AUTHOR}", page_icon="🧭", layout="wide")
sidebar_branding()
page_header("🧭 Future Work & Reflection", "Where I'd take this project next, and how the design evolved")

st.markdown("### Next steps")
steps = [
    ("📅 Extend the time range with newer data",
     "Swap in the updated ai-jobs.net salary file (2020–present, thousands of records) to check whether the "
     "patterns here hold with a larger, more recent sample, and add a proper year-over-year trend chart."),
    ("🌍 Adjust for cost of living",
     "Join a cost-of-living or purchasing-power (PPP) index by country so salaries can be compared in real terms, "
     "not just converted dollars. This would make the country comparison much fairer."),
    ("🏷️ Group job titles into role families",
     "The dataset has dozens of near-duplicate titles (e.g., *ML Engineer* vs. *Machine Learning Engineer*). "
     "Mapping them into families like Analyst, Engineer, Scientist, and Manager would make comparisons more reliable."),
    ("📈 Add a simple salary model",
     "Fit an interpretable regression (experience, company size, remote ratio, region) with confidence intervals, "
     "and present it as an estimate range rather than a single number to avoid over-claiming precision."),
    ("♿ Run an accessibility audit",
     "Test the app with a screen reader and keyboard-only navigation, check contrast with an automated tool, "
     "and add data-table alternatives under each chart for users who can't see the visuals."),
]
for title, body in steps:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.write(body)

st.markdown("### Reflection: from paper prototype (Lab 4.3) to final build")
# TODO: edit these to match what your actual Lab 4.3 paper prototype looked like.
st.markdown(
    """
- **Filters moved to the sidebar.** My sketch placed filters above the charts; in the build they crowded the
  KPIs, so I moved them to the sidebar where they stay visible while scrolling.
- **Median replaced mean as the headline number.** After seeing how right-skewed salaries are, I made the median
  the main KPI and added the mean only for comparison.
- **Sample sizes became visible everywhere.** The prototype showed only averages; the build adds *n* labels and
  flags small groups, because some categories (like Executive) have very few records.
- **Fewer, clearer charts.** I dropped a planned pie chart and a world map in favor of bar, box, and bubble charts
  that compare values more accurately and read well for color-blind users.
"""
)
