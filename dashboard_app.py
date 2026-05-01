import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
from scipy.stats import linregress


# ═══════════════════════════════════════════════════════════════
# CONFIG & THEME
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Sales Intelligence Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

NAVY       = "#0a1628"
MID_BLUE   = "#1a5491"
CORE_BLUE  = "#2166ac"
LIGHT_BLUE = "#4a9fd4"
SKY_BLUE   = "#9ecfec"
CHART_BG   = "#ffffff"
CHART_TEXT = "#111111"
CHART_GRID = "#e0e0e0"
TEXT       = "#cce4f7"

PALETTE = [
    "#0d2240", "#1a5491", "#2166ac", "#2e7ec2",
    "#4a9fd4", "#6db8e0", "#9ecfec", "#b8ddf2"
]

YEAR_COLORS = {
    2020: "#b8ddf2",
    2021: "#6db8e0",
    2022: "#4a9fd4",
    2023: "#2166ac",
    2024: "#0d2240"
}

st.markdown(f"""
<style>
  section[data-testid="stSidebar"] {{
      background: linear-gradient(180deg, #0a1628 0%, #0d2240 100%);
  }}
  section[data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
  span[data-baseweb="tag"] {{
      background-color: {MID_BLUE} !important;
      border: 1px solid {LIGHT_BLUE} !important;
      color: white !important;
      border-radius: 4px !important;
  }}
  span[data-baseweb="tag"] button {{ color: {SKY_BLUE} !important; }}
  .stApp {{ background-color: #f4f6fa; }}
  [data-testid="stMetricValue"] {{
      font-size: 1.6rem !important;
      font-weight: 700 !important;
      color: {CORE_BLUE} !important;
  }}
  [data-testid="stMetricLabel"] {{
      font-size: 0.78rem !important;
      color: #444444 !important;
      text-transform: uppercase;
      letter-spacing: 0.06em;
  }}
  hr {{ border-color: #cccccc !important; }}
  .stDownloadButton > button {{
      background-color: {MID_BLUE};
      color: white;
      border: 1px solid {LIGHT_BLUE};
      border-radius: 6px;
  }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════
def apply_chart_style(fig, ax):
    fig.patch.set_facecolor(CHART_BG)
    ax.set_facecolor(CHART_BG)
    ax.tick_params(colors=CHART_TEXT, labelsize=9)
    ax.xaxis.label.set_color(CHART_TEXT)
    ax.yaxis.label.set_color(CHART_TEXT)
    ax.title.set_color(CHART_TEXT)
    ax.title.set_fontsize(12)
    ax.title.set_fontweight("bold")
    for spine in ax.spines.values():
        spine.set_edgecolor("#cccccc")
    ax.grid(True, color=CHART_GRID, alpha=0.7, linewidth=0.6)
    fig.tight_layout()

def fmt_currency(ax, axis="x"):
    fmt = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    if axis == "x":
        ax.xaxis.set_major_formatter(fmt)
    else:
        ax.yaxis.set_major_formatter(fmt)

def get_palette(n):
    idx = np.linspace(0, len(PALETTE) - 1, n, dtype=int)
    return [PALETTE[i] for i in idx]

def safe_delta(curr, prev):
    if prev and prev != 0:
        pct = (curr - prev) / abs(prev) * 100
        return f"{pct:+.1f}%"
    return None


# ═══════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════
REQUIRED_COLS = {"Date", "Product", "Region", "Total"}

@st.cache_data(show_spinner="Loading sales data...")
def load_data():
    try:
        df = pd.read_csv("sales_data.csv")
        missing = REQUIRED_COLS - set(df.columns)
        if missing:
            st.error(f"Missing columns: {missing}")
            st.stop()
        df["Date"]      = pd.to_datetime(df["Date"], errors="coerce")
        df["Total"]     = pd.to_numeric(df["Total"], errors="coerce")
        df              = df.dropna(subset=["Date", "Total", "Region"])
        df["DateClean"] = df["Date"].dt.strftime("%Y-%m-%d")
        df["Month"]     = df["Date"].dt.month
        df["Quarter"]   = df["Date"].dt.quarter
        df["Year"]      = df["Date"].dt.year
        return df
    except FileNotFoundError:
        st.error("sales_data.csv not found.")
        st.stop()

df_raw = load_data()
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun",
                "Jul","Aug","Sep","Oct","Nov","Dec"]


# ═══════════════════════════════════════════════════════════════
# SIDEBAR FILTERS
# ═══════════════════════════════════════════════════════════════
st.sidebar.markdown("## 🔍 Filters")
st.sidebar.markdown("---")

all_products = sorted(df_raw["Product"].dropna().unique())
all_regions  = sorted(df_raw["Region"].dropna().unique())
all_years    = sorted(df_raw["Year"].unique())

sel_products = st.sidebar.multiselect("📦 Products", all_products, default=all_products)
sel_regions  = st.sidebar.multiselect("🌍 Regions",  all_regions,  default=all_regions)
sel_years    = st.sidebar.multiselect("📅 Years",     all_years,    default=all_years)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚔️ YoY Comparison")
yoy_year1 = st.sidebar.selectbox("Base Year",    all_years, index=len(all_years)-2)
yoy_year2 = st.sidebar.selectbox("Compare Year", all_years, index=len(all_years)-1)
st.sidebar.markdown("---")

df = df_raw[
    df_raw["Product"].isin(sel_products) &
    df_raw["Region"].isin(sel_regions)   &
    df_raw["Year"].isin(sel_years)
]

if df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

sorted_years = sorted(df["Year"].unique())


# ═══════════════════════════════════════════════════════════════
# KPI — compare latest vs prior year in selection
# ═══════════════════════════════════════════════════════════════
if len(sorted_years) >= 2:
    ly, py    = sorted_years[-1], sorted_years[-2]
    rev_curr  = df[df["Year"] == ly]["Total"].sum()
    rev_prev  = df[df["Year"] == py]["Total"].sum()
    ord_curr  = len(df[df["Year"] == ly])
    ord_prev  = len(df[df["Year"] == py])
    aov_curr  = df[df["Year"] == ly]["Total"].mean()
    aov_prev  = df[df["Year"] == py]["Total"].mean()
else:
    ly = sorted_years[0]
    rev_curr = rev_prev = df["Total"].sum()
    ord_curr = ord_prev = len(df)
    aov_curr = aov_prev = df["Total"].mean()


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown(f"""
<h1 style='color:{CORE_BLUE}; font-size:2rem; margin-bottom:0;'>
    📊 Sales Intelligence Dashboard
</h1>
<p style='color:#555555; margin-top:4px; font-size:0.9rem;'>
    <b style='color:{CORE_BLUE};'>{len(df):,}</b> transactions |
    Years selected: <b style='color:{CORE_BLUE};'>{", ".join(map(str, sorted_years))}</b>
</p>
""", unsafe_allow_html=True)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📌 Executive KPIs</h3>", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
k1.metric("💰 Total Revenue",   f"${df['Total'].sum():,.0f}",  safe_delta(rev_curr, rev_prev))
k2.metric("🛒 Total Orders",    f"{len(df):,}",                safe_delta(ord_curr, ord_prev))
k3.metric("📦 Avg Order Value", f"${df['Total'].mean():,.0f}", safe_delta(aov_curr, aov_prev))
k4.metric("🏆 Top Product",     df.groupby("Product")["Total"].sum().idxmax())
k5.metric("🌍 Top Region",      df.groupby("Region")["Total"].sum().idxmax())

k6,k7,k8,k9,k10 = st.columns(5)
k6.metric("📅 Latest Year",    str(ly))
k7.metric("⬆️ Highest Sale",   f"${df['Total'].max():,.0f}")
k8.metric("⬇️ Lowest Sale",    f"${df['Total'].min():,.0f}")
k9.metric("📊 Median Order",   f"${df['Total'].median():,.0f}")
k10.metric("📉 Std Deviation", f"${df['Total'].std():,.0f}")
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 1 — Annual Revenue with YoY Growth %
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📅 Annual Revenue + YoY Growth %</h3>",
            unsafe_allow_html=True)
st.caption("Bar = total revenue per year. % label = growth vs previous year.")

yearly = df.groupby("Year")["Total"].sum().reset_index()
yearly.columns = ["Year", "Revenue"]

fig, ax = plt.subplots(figsize=(14, 4))
x_pos  = np.arange(len(yearly))
colors = [YEAR_COLORS.get(y, CORE_BLUE) for y in yearly["Year"]]
bars   = ax.bar(x_pos, yearly["Revenue"].values, color=colors, width=0.5)

for i, (bar, val, yr) in enumerate(zip(bars, yearly["Revenue"].values, yearly["Year"].values)):
    prev = yearly[yearly["Year"] == yr - 1]["Revenue"].values
    growth_str = ""
    if len(prev) > 0:
        g = (val - prev[0]) / prev[0] * 100
        growth_str = f"\n▲{g:.1f}%" if g >= 0 else f"\n▼{abs(g):.1f}%"
    ax.text(bar.get_x() + bar.get_width() / 2,
            val + yearly["Revenue"].max() * 0.02,
            f"${val:,.0f}{growth_str}",
            ha="center", color=CHART_TEXT, fontsize=9, fontweight="bold")

ax.set_xticks(x_pos)
ax.set_xticklabels(yearly["Year"].astype(str).values, fontsize=10)
ax.set_xlim(-0.6, len(yearly) - 0.4)
ax.set_ylim(0, yearly["Revenue"].max() * 1.28)
fmt_currency(ax, "y")
apply_chart_style(fig, ax)
ax.set_title("Annual Revenue by Year")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 2 — Monthly Revenue All Years Overlaid
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📈 Monthly Revenue — All Years Overlaid</h3>",
            unsafe_allow_html=True)
st.caption("Compare seasonal patterns across years. Solid line = most recent year.")

fig, ax = plt.subplots(figsize=(14, 5))
for year in sorted_years:
    monthly = df[df["Year"] == year].groupby("Month")["Total"].sum()
    monthly = monthly.reindex(range(1, 13), fill_value=0)
    color   = YEAR_COLORS.get(year, CORE_BLUE)
    lw      = 2.8 if year == max(sorted_years) else 1.6
    ls      = "-" if year == max(sorted_years) else "--"
    ax.plot(range(1, 13), monthly.values, marker="o", markersize=5,
            color=color, linewidth=lw, linestyle=ls, label=str(year))

ax.set_xticks(range(1, 13))
ax.set_xticklabels(MONTH_LABELS)
fmt_currency(ax, "y")
ax.set_ylabel("Monthly Revenue ($)")
ax.legend(title="Year", facecolor=CHART_BG, labelcolor=CHART_TEXT, fontsize=9)
apply_chart_style(fig, ax)
ax.set_title("Monthly Revenue by Year")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 3 — Head to Head YoY (Two years, grouped monthly bars)
# ═══════════════════════════════════════════════════════════════
st.markdown(f"<h3 style='color:#1a1a2e;'>⚔️ Head-to-Head: {yoy_year1} vs {yoy_year2}</h3>",
            unsafe_allow_html=True)
st.caption(f"Monthly revenue side by side — {yoy_year1} (base) vs {yoy_year2} (compare).")

y1 = df_raw[df_raw["Year"]==yoy_year1].groupby("Month")["Total"].sum().reindex(range(1,13),fill_value=0)
y2 = df_raw[df_raw["Year"]==yoy_year2].groupby("Month")["Total"].sum().reindex(range(1,13),fill_value=0)

x     = np.arange(12)
w     = 0.35
fig, ax = plt.subplots(figsize=(14, 5))
ax.bar(x - w/2, y1.values, w, label=str(yoy_year1),
       color=YEAR_COLORS.get(yoy_year1, LIGHT_BLUE), alpha=0.85)
ax.bar(x + w/2, y2.values, w, label=str(yoy_year2),
       color=YEAR_COLORS.get(yoy_year2, CORE_BLUE), alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(MONTH_LABELS)
fmt_currency(ax, "y")
ax.set_ylabel("Revenue ($)")
ax.legend(facecolor=CHART_BG, labelcolor=CHART_TEXT, fontsize=10)
apply_chart_style(fig, ax)
ax.set_title(f"Monthly Revenue: {yoy_year1} vs {yoy_year2}")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 4 — Product Revenue by Year (Grouped Bar)
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📦 Product Revenue by Year</h3>",
            unsafe_allow_html=True)
st.caption("Which products grew or declined year over year?")

prod_year   = df.groupby(["Product","Year"])["Total"].sum().unstack(fill_value=0)
prods_list  = prod_year.index.tolist()
years_list  = prod_year.columns.tolist()
x           = np.arange(len(prods_list))
n_yr        = len(years_list)
w           = 0.8 / n_yr

fig, ax = plt.subplots(figsize=(14, 5))
for i, yr in enumerate(years_list):
    offset = (i - n_yr/2 + 0.5) * w
    color  = YEAR_COLORS.get(yr, PALETTE[i % len(PALETTE)])
    ax.bar(x + offset, prod_year[yr].values, w * 0.9,
           label=str(yr), color=color, alpha=0.88)

ax.set_xticks(x)
ax.set_xticklabels(prods_list, rotation=20, ha="right")
fmt_currency(ax, "y")
ax.legend(title="Year", facecolor=CHART_BG, labelcolor=CHART_TEXT, fontsize=9)
apply_chart_style(fig, ax)
ax.set_title("Product Revenue Across Years")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 5 — Region Revenue by Year
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>🌍 Region Revenue by Year</h3>",
            unsafe_allow_html=True)
st.caption("Which region is growing fastest year over year?")

reg_year = df.groupby(["Region","Year"])["Total"].sum().unstack(fill_value=0)
reg_list = reg_year.index.tolist()
x        = np.arange(len(reg_list))
w        = 0.8 / n_yr

fig, ax = plt.subplots(figsize=(14, 4))
for i, yr in enumerate(years_list):
    offset = (i - n_yr/2 + 0.5) * w
    color  = YEAR_COLORS.get(yr, PALETTE[i % len(PALETTE)])
    ax.bar(x + offset, reg_year[yr].values, w * 0.9,
           label=str(yr), color=color, alpha=0.88)

ax.set_xticks(x)
ax.set_xticklabels(reg_list)
fmt_currency(ax, "y")
ax.legend(title="Year", facecolor=CHART_BG, labelcolor=CHART_TEXT, fontsize=9)
apply_chart_style(fig, ax)
ax.set_title("Region Revenue Across Years")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 6 — Quarterly Revenue by Year
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📅 Quarterly Revenue by Year</h3>",
            unsafe_allow_html=True)
st.caption("Quarter-over-quarter performance across all selected years.")

q_year = df.groupby(["Year","Quarter"])["Total"].sum().reset_index()
q_year["Label"] = q_year["Year"].astype(str) + " Q" + q_year["Quarter"].astype(str)

fig, ax = plt.subplots(figsize=(14, 4))
x_pos   = np.arange(len(q_year))
colors  = [YEAR_COLORS.get(y, CORE_BLUE) for y in q_year["Year"]]
bars    = ax.bar(x_pos, q_year["Total"].values, color=colors, width=0.6)
for bar, val in zip(bars, q_year["Total"].values):
    ax.text(bar.get_x() + bar.get_width() / 2,
            val + q_year["Total"].max() * 0.01,
            f"${val/1000:.0f}K",
            ha="center", color=CHART_TEXT, fontsize=7, fontweight="bold")
ax.set_xticks(x_pos)
ax.set_xticklabels(q_year["Label"].values, rotation=45, ha="right", fontsize=7)
ax.set_xlim(-0.6, len(q_year) - 0.4)
ax.set_ylim(0, q_year["Total"].max() * 1.18)
fmt_currency(ax, "y")
legend_patches = [mpatches.Patch(color=YEAR_COLORS.get(y, CORE_BLUE), label=str(y))
                  for y in sorted_years]
ax.legend(handles=legend_patches, facecolor=CHART_BG, labelcolor=CHART_TEXT, fontsize=9)
apply_chart_style(fig, ax)
ax.set_title("Quarterly Revenue by Year")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 7 — Heatmap: Product × Year
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>🗓️ Revenue Heatmap — Product × Year</h3>",
            unsafe_allow_html=True)
st.caption("Which products grew the most across years?")

pivot_yr       = df.pivot_table(values="Total", index="Product",
                                columns="Year", aggfunc="sum", fill_value=0)
n_rows, n_cols = pivot_yr.values.shape
fig, ax        = plt.subplots(figsize=(max(10, n_cols * 1.8), max(5, n_rows * 0.7)))
im = ax.imshow(pivot_yr.values, cmap="Blues", aspect="auto",
               extent=[-0.5, n_cols-0.5, n_rows-0.5, -0.5])
plt.colorbar(im, ax=ax, format=mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_xticks(range(n_cols))
ax.set_xticklabels(pivot_yr.columns.astype(str), color=CHART_TEXT, fontsize=10)
ax.set_yticks(range(n_rows))
ax.set_yticklabels(pivot_yr.index, color=CHART_TEXT, fontsize=9)
for i in range(n_rows):
    for j in range(n_cols):
        val = pivot_yr.values[i, j]
        ax.text(j, i, f"${val:,.0f}", ha="center", va="center",
                color="white" if val > pivot_yr.values.max() * 0.5 else CHART_TEXT,
                fontsize=8)
apply_chart_style(fig, ax)
ax.set_title("Revenue Heatmap: Product × Year")
ax.grid(False)
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 8 — Monthly Order Volume by Year
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>🛒 Monthly Order Volume by Year</h3>",
            unsafe_allow_html=True)
st.caption("Transaction count per month — compare activity across years.")

fig, ax = plt.subplots(figsize=(14, 4))
for year in sorted_years:
    mo    = df[df["Year"]==year].groupby("Month")["Total"].count()
    mo    = mo.reindex(range(1,13), fill_value=0)
    color = YEAR_COLORS.get(year, CORE_BLUE)
    lw    = 2.5 if year == max(sorted_years) else 1.5
    ls    = "-" if year == max(sorted_years) else "--"
    ax.plot(range(1,13), mo.values, marker="o", markersize=4,
            color=color, linewidth=lw, linestyle=ls, label=str(year))
ax.set_xticks(range(1,13))
ax.set_xticklabels(MONTH_LABELS)
ax.set_ylabel("Number of Orders")
ax.legend(title="Year", facecolor=CHART_BG, labelcolor=CHART_TEXT, fontsize=9)
apply_chart_style(fig, ax)
ax.set_title("Monthly Order Count by Year")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 9 — Box Plot
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📉 Order Value Distribution by Product</h3>",
            unsafe_allow_html=True)
st.caption("Box plot shows spread and outliers per product across all selected years.")

prod_order   = df.groupby("Product")["Total"].median().sort_values().index.tolist()
data_by_prod = [df[df["Product"]==p]["Total"].values for p in prod_order]

fig, ax = plt.subplots(figsize=(14, 5))
bp = ax.boxplot(data_by_prod, labels=prod_order, patch_artist=True,
                medianprops=dict(color=CORE_BLUE, linewidth=2),
                whiskerprops=dict(color=CORE_BLUE),
                capprops=dict(color=CORE_BLUE),
                flierprops=dict(marker="o", color=LIGHT_BLUE, alpha=0.4, markersize=4))
for patch, color in zip(bp["boxes"], get_palette(len(prod_order))):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
fmt_currency(ax, "y")
ax.set_ylabel("Order Value ($)")
apply_chart_style(fig, ax)
ax.set_title("Order Value Spread per Product")
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# CHART 10 — Top 5 vs Bottom 5
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>🏆 Top 5 vs Bottom 5 Products</h3>",
            unsafe_allow_html=True)
st.caption("Performance gap between best and worst products across all selected years.")

prod_total = df.groupby("Product")["Total"].sum().sort_values(ascending=False)
top5 = prod_total.head(5).sort_values()
bot5 = prod_total.tail(5).sort_values()

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(14, 4))
ax_l.barh(top5.index, top5.values, color=get_palette(5))
for i, (idx, val) in enumerate(top5.items()):
    ax_l.text(val*0.01, i, f"${val:,.0f}", va="center", color=CHART_TEXT, fontsize=8)
ax_l.set_title("🏆 Top 5 Products", color=CHART_TEXT, fontweight="bold")
fmt_currency(ax_l, "x")

bot_colors = ["#4a9fd4","#6db8e0","#9ecfec","#b8ddf2","#daeefa"]
ax_r.barh(bot5.index, bot5.values, color=bot_colors)
for i, (idx, val) in enumerate(bot5.items()):
    ax_r.text(val*0.01, i, f"${val:,.0f}", va="center", color=CHART_TEXT, fontsize=8)
ax_r.set_title("⚠️ Bottom 5 Products", color=CHART_TEXT, fontweight="bold")
fmt_currency(ax_r, "x")
for a in [ax_l, ax_r]:
    apply_chart_style(fig, a)
st.pyplot(fig); plt.close(fig)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════
# DATA TABLE
# ═══════════════════════════════════════════════════════════════
st.markdown("<h3 style='color:#1a1a2e;'>📋 Raw Data Table</h3>", unsafe_allow_html=True)

display_df = df.copy()
display_df["Date"] = display_df["DateClean"]
display_df = display_df.drop(
    columns=["DateClean","Month","Quarter","Year"], errors="ignore"
)
st.dataframe(
    display_df.sort_values("Date", ascending=False).reset_index(drop=True),
    use_container_width=True,
    height=400
)
csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Filtered Data",
    data=csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv"
)

