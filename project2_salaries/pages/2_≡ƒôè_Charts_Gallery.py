"""EDA Gallery: four chart types (bar, histogram, box, heatmap), each with a question,
a 'How to read this chart' guide, a source caption, and data-driven observations.

Observations are computed from the loaded data with f-strings, so the numbers always
match the CSV in data/ instead of being typed in by hand.
"""
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    ACCENT, AUTHOR, ETHICS_NOTE, EXPERIENCE_ORDER, OKABE_ITO, PRIMARY, REMOTE_ORDER, SIZE_ORDER,
    SOURCE_CAPTION, get_data, page_header, sidebar_branding, style_fig, usd,
)

st.set_page_config(page_title=f"EDA Gallery · {AUTHOR}", page_icon="📊", layout="wide")
sidebar_branding()
page_header(
    "📊 EDA Gallery",
    "Exploratory analysis of data-job salaries: four chart types, how to read them, and what they show",
)

df = get_data()
st.markdown(
    f"All salaries are converted to **U.S. dollars (salary_in_usd)** so records from different countries "
    f"can be compared. The dataset has **{len(df):,} records** from {df['work_year'].min()} to "
    f"{df['work_year'].max()}. Charts are interactive — hover for exact values, drag to zoom, "
    "double-click to reset."
)
st.info(ETHICS_NOTE)

MIN_N = 10  # groups smaller than this are flagged as unreliable


def how_to_read(points: list[str]) -> None:
    with st.expander("📖 How to read this chart", expanded=True):
        st.markdown("\n".join(f"- {p}" for p in points))


def observations(points: list[str]) -> None:
    st.markdown("**🔎 Observations**")
    st.markdown("\n".join(f"- {p}" for p in points))


# ======================================================================================
# 1. BAR CHART — typical salary by group (interactive: choose grouping & statistic)
# ======================================================================================
st.header("1 · Bar chart: How does typical salary change with experience?")
st.markdown("**Question:** How does the typical salary differ across experience levels and other job attributes?")

GROUPINGS = {
    "Experience level": ("experience", EXPERIENCE_ORDER),
    "Company size": ("company_size_label", SIZE_ORDER),
    "Remote work": ("remote", REMOTE_ORDER),
    "Employment type": ("employment", None),
}
c1, c2 = st.columns(2)
group_label = c1.selectbox("Group salaries by", list(GROUPINGS), index=0)
stat = c2.radio("Statistic", ["Median", "Mean"], horizontal=True,
                help="The median is less affected by a few very high salaries.")
col, order = GROUPINGS[group_label]

g = (
    df.groupby(col, observed=True)["salary_in_usd"]
    .agg(median="median", mean="mean", n="size")
    .reset_index()
)
if order is None:
    g = g.sort_values("median", ascending=False)
g["value"] = g[stat.lower()]
g["label"] = g.apply(lambda r: f"{usd(r['value'])}<br>n={r['n']}", axis=1)

fig = px.bar(
    g, x=col, y="value", text="label",
    category_orders={col: order} if order else None,
    color_discrete_sequence=[PRIMARY],
    labels={col: group_label, "value": f"{stat} salary (USD)", "n": "Records"},
    hover_data={"n": True, "label": False},
    title=f"{stat} salary by {group_label.lower()} (USD)",
)
fig.update_traces(textposition="outside", cliponaxis=False)
fig.update_yaxes(tickprefix="$", tickformat=",.0f", rangemode="tozero")
st.plotly_chart(style_fig(fig), width="stretch")
st.caption(f"{SOURCE_CAPTION} Bars start at $0 so heights are proportional. n = number of salary records.")

how_to_read([
    "Each bar is one group; its **height is the median (or mean) salary in U.S. dollars**. The y-axis starts at $0, so a bar twice as tall means twice the pay.",
    "The label on each bar repeats the value and shows **n**, the number of records behind it — small n means the bar is less reliable.",
    "Use the dropdown to switch grouping and the toggle to compare **median vs. mean**; a mean much higher than the median signals a few very high salaries pulling it up.",
])

exp = df.groupby("experience", observed=True)["salary_in_usd"].agg(["median", "size"])
entry_med, senior_med = exp.loc["Entry", "median"], exp.loc["Senior", "median"]
small_groups = g.loc[g["n"] < MIN_N, col].astype(str).tolist()
rising = exp["median"].is_monotonic_increasing
top_level = exp["median"].idxmax()
obs1 = [
    f"Median salary goes from Entry ({usd(entry_med)}) to Mid ({usd(exp.loc['Mid','median'])}) to Senior "
    f"({usd(senior_med)}) to Executive ({usd(exp.loc['Executive','median'])})"
    + (" — rising at every step. " if rising else ". ")
    + f"Senior roles earn about **{senior_med / entry_med:.1f}×** the Entry median.",
    f"**{top_level}** has the highest median. The Executive group has only "
    f"**{exp.loc['Executive','size']} records**, so its bar is the least certain.",
    f"Senior is the largest group ({exp.loc['Senior','size']} of {len(df)} records, "
    f"{exp.loc['Senior','size']/len(df):.0%}), so the overall dataset leans toward experienced workers.",
]
if small_groups:
    obs1.append(f"In the current view, these groups have fewer than {MIN_N} records and should be read with caution: "
                f"{', '.join(small_groups)}.")
observations(obs1)
st.divider()

# ======================================================================================
# 2. HISTOGRAM — distribution of salaries (interactive: bin slider)
# ======================================================================================
st.header("2 · Histogram: What does the overall salary distribution look like?")
st.markdown("**Question:** Are most salaries clustered around a typical value, or spread out with extreme values?")

bin_width = st.slider("Bin width (thousands of USD)", 10, 50, 20, step=5)
med, mean = df["salary_in_usd"].median(), df["salary_in_usd"].mean()
fig = px.histogram(
    df, x="salary_k", color_discrete_sequence=[PRIMARY],
    labels={"salary_k": "Salary (thousands of USD)"},
    title="Distribution of salaries (thousands of USD)",
)
fig.update_traces(xbins=dict(start=0, size=bin_width), marker_line_color="white", marker_line_width=1,
                  hovertemplate="Salary: $%{x}k<br>Records: %{y}<extra></extra>")
fig.add_vline(x=med / 1000, line_dash="dash", line_color=ACCENT, line_width=2,
              annotation_text=f"Median {usd(med)}", annotation_position="top left")
fig.add_vline(x=mean / 1000, line_dash="dot", line_color="#000000", line_width=2,
              annotation_text=f"Mean {usd(mean)}", annotation_position="top right")
fig.update_yaxes(title="Number of records")
fig.update_xaxes(ticksuffix="k", tickprefix="$")
st.plotly_chart(style_fig(fig), width="stretch")
st.caption(f"{SOURCE_CAPTION} Dashed orange line = median; dotted black line = mean.")

how_to_read([
    "The x-axis is salary in **thousands of U.S. dollars**; each bar counts how many records fall in that salary range (the bin).",
    "Taller bars mean more people earn in that range. A long tail stretching to the right means a few people earn much more than everyone else.",
    "The **dashed orange line is the median** (half earn less, half more) and the **dotted black line is the mean**. When the mean sits to the right of the median, high salaries are pulling the average up.",
])

top = df.loc[df["salary_in_usd"].idxmax()]
share_mid = df["salary_in_usd"].between(50_000, 150_000).mean()
over_300 = (df["salary_in_usd"] > 300_000).sum()
under_25 = (df["salary_in_usd"] < 25_000).sum()
observations([
    f"The distribution is **right-skewed**: the mean ({usd(mean)}) is {usd(mean - med)} higher than the median ({usd(med)}).",
    f"About **{share_mid:.0%}** of records fall between $50k and $150k, the dataset's main cluster.",
    f"Only **{over_300} records** exceed $300k; the maximum is {usd(top['salary_in_usd'])} "
    f"({top['job_title']}, {top['experience']} level, company in {top['company_country']}).",
    f"At the low end, **{under_25} records** are below $25k, and "
    f"{(df.loc[df['salary_in_usd'] < 25_000, 'company_location'] != 'US').mean():.0%} of them are at companies outside the U.S. — "
    "a reminder that one global distribution mixes very different labor markets.",
])
st.divider()

# ======================================================================================
# 3. BOX PLOT — salary spread by company size, split by year
# ======================================================================================
st.header("3 · Box plot: Do larger companies pay more, and has that changed over time?")
st.markdown("**Question:** How do salary ranges compare across company sizes, and how do they shift from year to year?")

years = sorted(df["work_year"].unique())
show_points = st.checkbox("Show every record as a dot", value=False)
fig = px.box(
    df, x="company_size_label", y="salary_k", color=df["work_year"].astype(str),
    category_orders={"company_size_label": SIZE_ORDER, "color": [str(y) for y in years]},
    color_discrete_sequence=OKABE_ITO,
    points="all" if show_points else "outliers",
    labels={"company_size_label": "Company size (employees)", "salary_k": "Salary (thousands of USD)",
            "color": "Work year"},
    hover_data={"job_title": True, "experience": True},
    title="Salary range by company size and year (thousands of USD)",
)
fig.update_yaxes(tickprefix="$", ticksuffix="k")
st.plotly_chart(style_fig(fig, height=460), width="stretch")
st.caption(f"{SOURCE_CAPTION} Colors use the color-blind-safe Okabe-Ito palette; hover shows exact quartiles.")

how_to_read([
    "Each box shows the **middle 50% of salaries** for one company size in one year; the line inside is the **median**.",
    "The whiskers reach the typical minimum and maximum; **dots beyond them are outliers** — unusually high or low salaries. Hover any dot to see the job title.",
    "Colors are **work years**; compare same-colored boxes across sizes, or different colors within one size to see change over time.",
])

size = df.groupby("company_size_label", observed=True)["salary_in_usd"].agg(
    median="median", q1=lambda s: s.quantile(.25), q3=lambda s: s.quantile(.75), n="size")
size["iqr"] = size["q3"] - size["q1"]
widest = size["iqr"].idxmax()
yr = df.groupby("work_year")["salary_in_usd"].median()
q1, q3 = df["salary_in_usd"].quantile([.25, .75])
n_out = (df["salary_in_usd"] > q3 + 1.5 * (q3 - q1)).sum()
observations([
    "Overall medians — " + ", ".join(f"{k}: {usd(v)} (n={size.loc[k,'n']})" for k, v in size["median"].items()) + ".",
    f"Small companies have the **lowest median** ({usd(size.loc[SIZE_ORDER[0],'median'])}); the gap between small and the "
    f"best-paying size is {usd(size['median'].max() - size.loc[SIZE_ORDER[0],'median'])}.",
    f"**{widest}** companies have the widest middle-50% range ({usd(size.loc[widest,'iqr'])}), meaning pay there varies the most.",
    f"The overall median moved from {usd(yr.iloc[0])} in {yr.index[0]} to {usd(yr.iloc[-1])} in {yr.index[-1]}; "
    f"note that {yr.index[0]} has far fewer records ({(df['work_year']==yr.index[0]).sum()}) than {yr.index[-1]} "
    f"({(df['work_year']==yr.index[-1]).sum()}), so the change mixes real trends with who answered the survey.",
    f"**{n_out} records** sit above the overall upper whisker (1.5 × IQR rule): " + ", ".join(
        f"{k} {v}" for k, v in df.loc[df["salary_in_usd"] > q3 + 1.5 * (q3 - q1)]
        .groupby("company_size_label", observed=False).size().items()) + ".",
])
st.divider()

# ======================================================================================
# 4. HEATMAP — median salary by experience x remote work
# ======================================================================================
st.header("4 · Heatmap: How do experience and remote work combine?")
st.markdown("**Question:** For each experience level, does the typical salary differ between on-site, hybrid, and fully remote work?")

pivot = df.pivot_table(index="experience", columns="remote", values="salary_in_usd",
                       aggfunc="median", observed=True).reindex(index=EXPERIENCE_ORDER, columns=REMOTE_ORDER)
counts = df.pivot_table(index="experience", columns="remote", values="salary_in_usd",
                        aggfunc="size", observed=True).reindex(index=EXPERIENCE_ORDER, columns=REMOTE_ORDER).fillna(0)
text = np.where(
    counts.values == 0, "no data",
    [[f"${v/1000:,.0f}k{'*' if n < MIN_N else ''}<br>n={int(n)}" for v, n in zip(rv, rn)]
     for rv, rn in zip(pivot.values, counts.values)],
)
fig = px.imshow(
    pivot / 1000, color_continuous_scale="Cividis", aspect="auto",
    labels=dict(x="Remote work", y="Experience level", color="Median salary ($k)"),
    title="Median salary by experience level and remote work (thousands of USD)",
)
fig.update_traces(text=text, texttemplate="%{text}", textfont=dict(size=14),
                  hovertemplate="%{y} · %{x}<br>Median: $%{z:,.0f}k<extra></extra>")
fig.update_coloraxes(colorbar_tickprefix="$", colorbar_ticksuffix="k")
st.plotly_chart(style_fig(fig, height=440), width="stretch")
st.caption(f"{SOURCE_CAPTION} Cividis is a perceptually uniform, color-blind-safe scale. "
           f"* = fewer than {MIN_N} records (interpret with caution).")

how_to_read([
    "Rows are **experience levels** (junior at top, senior at bottom) and columns are **remote-work arrangements**.",
    "Each cell's **color shows the median salary**: darker blue is lower, brighter yellow is higher (see the color bar). The number in the cell repeats the value, so you don't need to rely on color.",
    f"**n** is how many records are in the cell; an asterisk (*) marks cells with fewer than {MIN_N} records.",
])

flat = pivot.stack().rename("median").to_frame().join(counts.stack().rename("n"))
reliable = flat[flat["n"] >= MIN_N]
hi, lo = reliable["median"].idxmax(), reliable["median"].idxmin()
remote_med = df.groupby("remote", observed=True)["salary_in_usd"].agg(["median", "size"])
n_small = int((flat["n"] < MIN_N).sum())
small_rows = flat[flat["n"] < MIN_N].index.get_level_values(0).value_counts()
# Does Senior out-earn Entry within every remote arrangement? (computed, not assumed)
sen_vs_ent = [(c, pivot.loc["Senior", c] > pivot.loc["Entry", c]) for c in REMOTE_ORDER
              if counts.loc["Senior", c] > 0 and counts.loc["Entry", c] > 0]
n_holds = sum(ok for _, ok in sen_vs_ent)
observations([
    f"Among cells with at least {MIN_N} records, the highest median is **{hi[0]} · {hi[1]}** "
    f"({usd(reliable.loc[hi,'median'])}) and the lowest is **{lo[0]} · {lo[1]}** ({usd(reliable.loc[lo,'median'])}).",
    "Across all experience levels, medians are " + ", ".join(
        f"{k}: {usd(r['median'])} (n={int(r['size'])})" for k, r in remote_med.iterrows()) + ".",
    f"Senior medians exceed Entry medians in **{n_holds} of {len(sen_vs_ent)}** remote arrangements, so the "
    "experience pattern from Chart 1 " + ("holds within every column." if n_holds == len(sen_vs_ent)
                                          else "does not hold everywhere — worth a closer look."),
    f"**{n_small} of {flat.shape[0]} cells** have fewer than {MIN_N} records"
    + (f" (most often in the {small_rows.index[0]} row)" if n_small else "")
    + ", so differences in those cells could easily change with more data.",
])
