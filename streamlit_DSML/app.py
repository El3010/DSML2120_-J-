"""
Online Shop 2025 Sales Dashboard
Dataset: data/online_orders.csv (one row per order, 2025)

Goal:     Help the online shop's marketing & merchandising manager plan promotions
          and stock by showing when sales peak, which categories earn and lose
          money to returns, and whether discounts actually grow orders.
Audience: Marketing / merchandising manager, checked weekly (daily in Nov–Dec).

Sections: 1) setup  2) load data  3) sidebar filters  4) KPIs
          5) charts  6) insights
"""

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------------------------------------------
# 1) Page setup
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Online Shop 2025 Dashboard", page_icon="🛒", layout="wide")

DATA_PATH = "data/online_orders.csv"
BAR_COLOR = "#2E6FBA"     # one accessible blue; meaning is carried by labels, not color
ACCENT = "#C2410C"        # used only together with text labels
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------------------
# 2) Load and clean data (cached so filters don't re-read the CSV)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> tuple[pd.DataFrame, int]:
    df = pd.read_csv(path, parse_dates=["order_date"])

    # Blank-value policy: drop any row missing a value we chart or total.
    # (The 2025 file has 0 blanks, but this keeps the app safe if the CSV changes.)
    n_before = len(df)
    df = df.dropna(subset=["order_date", "category", "revenue", "units", "returned"])
    n_dropped = n_before - len(df)

    # Helper columns
    df["month_num"] = df["order_date"].dt.month
    df["month"] = pd.Categorical(df["month_num"].map(lambda m: MONTHS[m - 1]),
                                 categories=MONTHS, ordered=True)
    df["is_returned"] = df["returned"].eq("Yes")
    df["discount_label"] = (df["discount_pct"] * 100).round().astype(int).astype(str) + "%"
    return df, n_dropped


df, n_dropped = load_data(DATA_PATH)


# ---------------------------------------------------------------------------
# 3) Sidebar filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")

min_d, max_d = df["order_date"].min().date(), df["order_date"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(min_d, max_d),
                                   min_value=min_d, max_value=max_d)

categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()),
                                    default=sorted(df["category"].unique()))
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()),
                                 default=sorted(df["region"].unique()))
devices = st.sidebar.multiselect("Device", sorted(df["device"].unique()),
                                 default=sorted(df["device"].unique()))
customer = st.sidebar.selectbox("Customer type", ["All", "New", "Returning"])

st.sidebar.caption(
    f"Data handling: rows with blank values are dropped. "
    f"This file had {n_dropped} blank rows, so all {len(df):,} orders are used."
)

# date_input returns a single date while the user is mid-selection; handle both cases
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start, end = date_range
else:
    start = end = date_range[0] if isinstance(date_range, (tuple, list)) else date_range

mask = (
    df["order_date"].dt.date.between(start, end)
    & df["category"].isin(categories)
    & df["region"].isin(regions)
    & df["device"].isin(devices)
)
if customer != "All":
    mask &= df["customer_type"].eq(customer)
fdf = df[mask]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🛒 Online Shop 2025: Sales, Returns & Discounts")
st.markdown(
    "**Goal:** help the marketing & merchandising manager plan promotions and stock. "
    "Use the filters on the left to focus on a category, region, device or customer type."
)

if fdf.empty:
    st.warning("No orders match these filters. Widen the date range or add categories, regions or devices.")
    st.stop()


# ---------------------------------------------------------------------------
# 4) KPI cards
# ---------------------------------------------------------------------------
total_rev = fdf["revenue"].sum()
n_orders = len(fdf)
aov = fdf["revenue"].mean()
ret_rate = fdf["is_returned"].mean()
avg_rating = fdf["rating_1to5"].mean()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total revenue (USD)", f"${total_rev:,.0f}")
k2.metric("Orders", f"{n_orders:,}")
is_filtered = len(fdf) < len(df)   # only show deltas when a filter is active
k3.metric("Avg order value (USD)", f"${aov:,.2f}",
          delta=f"{aov - df['revenue'].mean():+.2f} vs all orders" if is_filtered else None)
k4.metric("Return rate", f"{ret_rate:.1%}",
          delta=(f"{(ret_rate - df['is_returned'].mean()) * 100:+.1f} pts vs all orders"
                 if is_filtered else None),
          delta_color="inverse")   # higher returns = bad, so an increase shows red
k5.metric("Avg rating (1–5)", f"{avg_rating:.2f}")
st.caption("KPI cards: totals for the filtered orders. When a filter is on, the small arrows compare "
           "the filtered orders with all 2025 orders.")

st.divider()


# ---------------------------------------------------------------------------
# 5) Charts
# ---------------------------------------------------------------------------

# --- Q1: How do sales change across the year? (interactive line) -----------
st.subheader("Q1. How do sales change across the year?")
monthly = (fdf.groupby("month", observed=False)
              .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
              .reset_index())
fig1 = px.line(monthly, x="month", y="revenue", markers=True, text="revenue",
               labels={"month": "Month (2025)", "revenue": "Revenue (USD)"},
               hover_data={"orders": True, "revenue": ":$,.0f"})
fig1.update_traces(line_color=BAR_COLOR, texttemplate="$%{y:,.0f}",
                   textposition="top center", textfont_size=12)
fig1.update_layout(yaxis_tickprefix="$", yaxis_tickformat=",", font_size=14,
                   height=420, margin=dict(t=30))
# Mark the two sale periods with light shaded bands + text labels (not color alone)
for m, label in [("Jul", "July sale"), ("Dec", "Holiday peak")]:
    i = MONTHS.index(m)
    fig1.add_vrect(x0=i - 0.4, x1=i + 0.4, fillcolor=ACCENT, opacity=0.10,
                   line_width=0, layer="below")
    fig1.add_annotation(x=m, y=1.07, yref="paper", text=label, showarrow=False,
                        font=dict(color=ACCENT, size=13))
st.plotly_chart(fig1, width="stretch")
st.caption("Line chart: total revenue (USD) per month in 2025, with each month's value labeled. "
           "Shaded bands mark the July sale and the December holiday season. Hover for order counts.")

c1, c2 = st.columns(2)

# --- Q2: Which category earns the most? -------------------------------------
with c1:
    st.subheader("Q2. Which category earns the most?")
    cat = (fdf.groupby("category")
              .agg(revenue=("revenue", "sum"), orders=("order_id", "count"))
              .sort_values("revenue").reset_index())
    fig2 = px.bar(cat, x="revenue", y="category", orientation="h", text="revenue",
                  labels={"revenue": "Revenue (USD)", "category": "Category"},
                  hover_data={"orders": True})
    fig2.update_traces(marker_color=BAR_COLOR, texttemplate="$%{x:,.0f}",
                       textposition="outside", textfont_size=13)
    fig2.update_layout(xaxis_tickprefix="$", xaxis_tickformat=",", font_size=14,
                       height=360, margin=dict(t=10, r=20),
                       xaxis_range=[0, cat["revenue"].max() * 1.3])
    st.plotly_chart(fig2, width="stretch")
    st.caption("Bar chart: total revenue (USD) by product category, sorted, with exact values on each bar.")

# --- Q3: Where do returns happen? -------------------------------------------
with c2:
    st.subheader("Q3. Where do returns happen?")
    level = st.radio("Show return rate by", ["Category", "Product (top 8)"], horizontal=True)
    key = "category" if level == "Category" else "product"
    ret = (fdf.groupby(key)
              .agg(return_rate=("is_returned", "mean"), returns=("is_returned", "sum"),
                   orders=("order_id", "count"))
              .sort_values("return_rate").reset_index())
    if key == "product":
        ret = ret.tail(8)
    ret["label"] = ret.apply(lambda r: f"{r.return_rate:.1%} ({int(r.returns):,} of {r.orders:,})", axis=1)
    fig3 = px.bar(ret, x="return_rate", y=key, orientation="h", text="label",
                  labels={"return_rate": "Return rate (% of orders)", key: key.title()})
    fig3.update_traces(marker_color=ACCENT, textposition="outside", textfont_size=13)
    fig3.update_layout(xaxis_tickformat=".0%", font_size=14, height=360,
                       margin=dict(t=10, r=110),
                       xaxis_range=[0, ret["return_rate"].max() * 1.9])
    st.plotly_chart(fig3, width="stretch")
    st.caption("Bar chart: share of orders returned, by category or product. "
               "Labels show the rate and the count of returned orders out of all orders.")

# --- Q4: Do discounts bring bigger orders? ----------------------------------
st.subheader("Q4. Do discounts bring bigger orders?")
disc = (fdf.groupby("discount_label")
           .agg(avg_units=("units", "mean"), avg_revenue=("revenue", "mean"),
                orders=("order_id", "count"))
           .reindex(["0%", "10%", "20%", "30%"]).dropna().reset_index())
d1, d2 = st.columns(2)
with d1:
    fig4 = px.bar(disc, x="discount_label", y="avg_units", text="avg_units",
                  labels={"discount_label": "Discount", "avg_units": "Avg units per order"},
                  hover_data={"orders": True})
    fig4.update_traces(marker_color=BAR_COLOR, texttemplate="%{y:.2f} units",
                       textposition="outside", textfont_size=13)
    fig4.update_layout(font_size=14, height=340, margin=dict(t=10),
                       yaxis_range=[0, disc["avg_units"].max() * 1.25],
                       xaxis_type="category")   # keep "0%".."30%" as labels, not numbers
    st.plotly_chart(fig4, width="stretch")
    st.caption("Bar chart: average number of units per order at each discount level.")
with d2:
    fig5 = px.bar(disc, x="discount_label", y="avg_revenue", text="avg_revenue",
                  labels={"discount_label": "Discount", "avg_revenue": "Avg revenue per order (USD)"},
                  hover_data={"orders": True})
    fig5.update_traces(marker_color=BAR_COLOR, texttemplate="$%{y:.2f}",
                       textposition="outside", textfont_size=13)
    fig5.update_layout(font_size=14, height=340, margin=dict(t=10), yaxis_tickprefix="$",
                       yaxis_range=[0, disc["avg_revenue"].max() * 1.25],
                       xaxis_type="category")
    st.plotly_chart(fig5, width="stretch")
    st.caption("Bar chart: average revenue (USD) per order at each discount level, after the discount.")

st.divider()


# ---------------------------------------------------------------------------
# 6) Insights panel — computed from the filtered data so numbers stay correct
# ---------------------------------------------------------------------------
st.subheader("💡 Key insights")

def pct_diff(a: float, b: float) -> float:
    return (a - b) / b * 100 if b else 0.0

insights = []

# Q1: peak month vs average month
if monthly["revenue"].gt(0).sum() >= 2:
    active = monthly[monthly["revenue"] > 0]
    peak = active.loc[active["revenue"].idxmax()]
    others = active[active["month"] != peak["month"]]["revenue"].mean()
    insights.append(
        f"**Seasonality:** {peak['month']} is the top month with **${peak['revenue']:,.0f}** "
        f"from {int(peak['orders'])} orders, **{pct_diff(peak['revenue'], others):.0f}% above** "
        f"the average of the other months (${others:,.0f}). Stock up and staff support before it."
    )

# Q2: top category share
top_cat = cat.iloc[-1]
insights.append(
    f"**Top earner:** {top_cat['category']} brings in **${top_cat['revenue']:,.0f}**, "
    f"**{top_cat['revenue'] / total_rev:.0%}** of filtered revenue, from {int(top_cat['orders']):,} orders."
)

# Q3: worst return rate category
cat_ret = fdf.groupby("category")["is_returned"].agg(["mean", "sum", "count"])
worst = cat_ret["mean"].idxmax()
insights.append(
    f"**Returns:** {worst} has the highest return rate at **{cat_ret.loc[worst, 'mean']:.1%}** "
    f"({int(cat_ret.loc[worst, 'sum']):,} of {int(cat_ret.loc[worst, 'count']):,} orders), versus "
    f"{ret_rate:.1%} overall. Returned orders average a **{fdf.loc[fdf.is_returned, 'rating_1to5'].mean():.1f}** "
    f"rating vs **{fdf.loc[~fdf.is_returned, 'rating_1to5'].mean():.1f}** for kept orders — better sizing info could help."
    if fdf["is_returned"].any() else
    f"**Returns:** none of the filtered orders were returned."
)

# Q4: discount effect on units and revenue
if {"0%", "30%"}.issubset(set(disc["discount_label"])):
    u0, u30 = disc.set_index("discount_label").loc[["0%", "30%"], "avg_units"]
    r0, r30 = disc.set_index("discount_label").loc[["0%", "30%"], "avg_revenue"]
    insights.append(
        f"**Discounts:** orders at 30% off average **{u30:.2f} units** vs **{u0:.2f}** at full price "
        f"({pct_diff(u30, u0):+.0f}%), "
        + ("so discounts do **not** make baskets meaningfully bigger — and "
           if abs(pct_diff(u30, u0)) < 5 else "a real change in basket size, and ")
        + f"revenue per order goes from **${r0:.2f} to ${r30:.2f}** ({pct_diff(r30, r0):+.0f}%)."
    )

for line in insights:
    st.markdown(f"- {line}")

st.caption("Insights are recalculated from the current filters. Source: online_orders.csv (2025, 3,548 orders).")
