"""Dashboard: sidebar filters drive KPIs and three linked charts; narrative insights are
recomputed for whatever subset is selected."""
import plotly.express as px
import streamlit as st

from utils import (
    AUTHOR, DATA_NAME, DATA_URL, ETHICS_NOTE, EXPERIENCE_ORDER, OKABE_ITO, PRIMARY, REMOTE_ORDER,
    SIZE_ORDER, SOURCE_CAPTION, data_file_timestamp, get_data, page_header, sidebar_branding,
    style_fig, usd,
)

st.set_page_config(page_title=f"Dashboard · {AUTHOR}", page_icon="📈", layout="wide")
sidebar_branding()
page_header("📈 Salary Dashboard", "Filter data-job salaries and compare pay across roles, experience, and countries")

df = get_data()

# Reproducibility: data source badge + last refreshed line
st.markdown(
    f"[![Data source: Kaggle](https://img.shields.io/badge/data_source-Kaggle-20BEFF?logo=kaggle&logoColor=white)]({DATA_URL}) "
    f"&nbsp; **[{DATA_NAME}]({DATA_URL})**"
)
st.caption(f"🕒 Last refreshed: data file updated {data_file_timestamp()} · {len(df):,} total records")

# --------------------------------------------------------------------------------------
# Filters (sidebar)
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    years = sorted(df["work_year"].unique())
    sel_years = st.multiselect("Work year", years, default=years)
    sel_exp = st.multiselect("Experience level", EXPERIENCE_ORDER, default=EXPERIENCE_ORDER)
    sel_size = st.multiselect("Company size", SIZE_ORDER, default=SIZE_ORDER)
    sel_remote = st.multiselect("Remote work", REMOTE_ORDER, default=REMOTE_ORDER)
    lo, hi = int(df["salary_in_usd"].min()), int(df["salary_in_usd"].max())
    sel_salary = st.slider("Salary range (USD)", lo, hi, (lo, hi), step=5_000, format="$%d")
    us_only = st.toggle("U.S.-based companies only", value=False)
    st.caption("Tip: remove items from a filter to narrow the view. All KPIs and charts update together.")

mask = (
    df["work_year"].isin(sel_years)
    & df["experience"].isin(sel_exp)
    & df["company_size_label"].isin(sel_size)
    & df["remote"].isin(sel_remote)
    & df["salary_in_usd"].between(*sel_salary)
)
if us_only:
    mask &= df["company_location"].eq("US")
f = df[mask]

if f.empty:
    st.warning("No records match these filters. Try widening your selection in the sidebar.")
    st.stop()

# --------------------------------------------------------------------------------------
# KPIs
# --------------------------------------------------------------------------------------
overall_median = df["salary_in_usd"].median()
k1, k2, k3, k4 = st.columns(4)
k1.metric("Records shown", f"{len(f):,}", f"{len(f)/len(df):.0%} of all", delta_color="off")
k2.metric("Median salary (USD)", usd(f["salary_in_usd"].median()),
          f"{usd(f['salary_in_usd'].median() - overall_median)} vs. all data",
          help="Difference from the median of the full, unfiltered dataset.")
k3.metric("Mean salary (USD)", usd(f["salary_in_usd"].mean()))
k4.metric("Fully remote share", f"{(f['remote_ratio'] == 100).mean():.0%}",
          help="Share of filtered records with remote_ratio = 100.")

# --------------------------------------------------------------------------------------
# Linked visuals
# --------------------------------------------------------------------------------------
top_n = st.slider("Number of job titles to show", 5, 15, 10)
left, right = st.columns(2, gap="large")

with left:
    titles = (
        f.groupby("job_title")["salary_in_usd"].agg(median="median", n="size")
        .query("n >= 3").sort_values("n", ascending=False).head(top_n)
        .sort_values("median")
        .reset_index()
    )
    fig = px.bar(
        titles, x="median", y="job_title", orientation="h", text="n",
        color_discrete_sequence=[PRIMARY],
        labels={"median": "Median salary (USD)", "job_title": "Job title", "n": "Records"},
        title=f"Median salary for the {len(titles)} most common job titles",
    )
    fig.update_traces(texttemplate="n=%{text}", textposition="outside", cliponaxis=False,
                      hovertemplate="%{y}<br>Median: $%{x:,.0f}<br>Records: %{text}<extra></extra>")
    fig.update_xaxes(tickprefix="$", tickformat=",.0f", range=[0, titles["median"].max() * 1.18])
    st.plotly_chart(style_fig(fig, height=460), width="stretch")
    st.caption("Only titles with at least 3 records are shown. Bars start at $0.")

with right:
    fig = px.box(
        f, x="experience", y="salary_k", color="experience",
        category_orders={"experience": EXPERIENCE_ORDER}, color_discrete_sequence=OKABE_ITO,
        points="outliers", hover_data={"job_title": True, "company_country": True},
        labels={"experience": "Experience level", "salary_k": "Salary (thousands of USD)",
                "job_title": "Job title", "company_country": "Company country"},
        title="Salary spread by experience level",
    )
    fig.update_layout(showlegend=False)
    fig.update_yaxes(tickprefix="$", ticksuffix="k")
    st.plotly_chart(style_fig(fig, height=460), width="stretch")
    st.caption("Box = middle 50% of salaries; line = median; dots = outliers (hover for details).")

countries = (
    f.groupby("company_country")["salary_in_usd"].agg(median="median", n="size")
    .sort_values("n", ascending=False).head(10).reset_index()
)
fig = px.scatter(
    countries, x="n", y="median", size="n", text="company_country", size_max=45,
    color_discrete_sequence=[OKABE_ITO[2]], log_x=True,
    labels={"n": "Number of records (log scale)", "median": "Median salary (USD)",
            "company_country": "Company country"},
    title="Top 10 company countries: sample size vs. median salary",
)
fig.update_traces(textposition="top center", marker=dict(line=dict(color="#1F2937", width=1)),
                  hovertemplate="%{text}<br>Records: %{x}<br>Median: $%{y:,.0f}<extra></extra>")
fig.update_yaxes(tickprefix="$", tickformat=",.0f", range=[0, countries["median"].max() * 1.4])
fig.update_xaxes(tickvals=[1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000], tickformat="d")
st.plotly_chart(style_fig(fig, height=430), width="stretch")
st.caption(f"{SOURCE_CAPTION} Bubble size = number of records. The x-axis is logarithmic because one country dominates the sample.")

# --------------------------------------------------------------------------------------
# Narrative insights (recomputed for the current filter)
# --------------------------------------------------------------------------------------
st.subheader("💡 Insights for the current selection")
exp_med = f.groupby("experience", observed=True)["salary_in_usd"].median()
best_title = titles.loc[titles["median"].idxmax()] if not titles.empty else None
us_share = f["company_location"].eq("US").mean()
insights = []
if len(exp_med) >= 2:
    insights.append(
        f"Within this selection, the median ranges from {usd(exp_med.min())} ({exp_med.idxmin()}) to "
        f"{usd(exp_med.max())} ({exp_med.idxmax()}) across experience levels."
    )
if best_title is not None:
    insights.append(
        f"Among the most common titles shown, **{best_title['job_title']}** has the highest median "
        f"({usd(best_title['median'])}, n={best_title['n']})."
    )
insights.append(
    f"**{us_share:.0%}** of the selected records are at U.S. companies, so overall figures largely reflect the U.S. market; "
    "toggle *U.S.-based companies only* to compare."
)
insights.append(
    f"The mean ({usd(f['salary_in_usd'].mean())}) is "
    + ("above" if f["salary_in_usd"].mean() > f["salary_in_usd"].median() else "at or below")
    + f" the median ({usd(f['salary_in_usd'].median())}), "
    + ("so a few high salaries pull the average up — the median is the better 'typical' value."
       if f["salary_in_usd"].mean() > f["salary_in_usd"].median() else "so the selection is not skewed by high earners.")
)
insights.append(
    "**Limitations:** salaries are self-reported, many filter combinations leave fewer than 10 records, and the data "
    "do not include cost of living, benefits, or equity. These are associations, not causes — e.g., remote work is "
    "not shown to *raise* pay."
)
st.markdown("\n".join(f"- {i}" for i in insights))

with st.expander("🔍 View and download the filtered data"):
    cols = ["work_year", "job_title", "experience", "employment", "salary_in_usd",
            "company_country", "company_size_label", "remote"]
    st.dataframe(f[cols], width="stretch", hide_index=True,
                 column_config={"salary_in_usd": st.column_config.NumberColumn("Salary (USD)", format="$%d")})
    st.download_button("Download filtered CSV", f[cols].to_csv(index=False), "filtered_salaries.csv", "text/csv")

st.info(ETHICS_NOTE)
