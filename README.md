# 📊 Sales Intelligence Dashboard
A dynamic, interactive data visualization web app built with Python and Streamlit to explore, filter, and analyze multi-year sales performance across products and regions.

---

## 🗂️ Short Description / Purpose

The Sales Intelligence Dashboard is a fully interactive analytics tool built in Python using Streamlit, designed to help business users explore sales data across multiple years, products, and regions — all from a simple CSV file.

The dashboard is intended for use by sales analysts, business intelligence teams, product managers, and anyone seeking to understand revenue trends, seasonal patterns, and product-level performance without needing a BI tool license.

---

## 🛠️ Tech Stack

The dashboard was built using the following tools and technologies:

- 🐍 **Python 3.8+** — Core programming language
- 🌐 **Streamlit** — Web application framework for turning Python scripts into interactive dashboards
- 🐼 **Pandas** — Data loading, filtering, transformation, and aggregation
- 📊 **Matplotlib** — Chart rendering for all 10 visualizations
- 🔢 **NumPy** — Numerical operations and array handling
- 📐 **SciPy** — Statistical functions (linear regression, distributions)
- 📁 **File Format** — `.py` for app logic, `.csv` for data input

---

## 📂 Data Source

**Source:** Synthetic sales transaction dataset (`sales_data.csv`)

The dataset contains **5,226 sales transactions** spanning **2020–2024**, including details on:

| Column | Description |
|--------|-------------|
| `Date` | Transaction date (YYYY-MM-DD) |
| `Product` | Product name (Laptop, Phone, Tablet, Monitor, etc.) |
| `Region` | Sales region (North, South, East, West) |
| `Quantity` | Units sold per transaction |
| `Price` | Unit price ($) |
| `Total` | Total transaction value ($) |

---

## ✨ Features / Highlights

### 📌 Business Problem
Sales teams and managers often struggle to get quick, visual answers to questions like:
- Which products are growing or declining year over year?
- Which region is performing best this quarter?
- How does this month compare to the same month last year?
- What is the spread and distribution of order values per product?

Answering these from raw CSV data is slow and error-prone without a proper tool.

---

### 🎯 Goal of the Dashboard
To deliver a self-serve interactive analytics tool that:
- Enables instant filtering by product, region, and year
- Supports sales reviews, quarterly business reviews (QBRs), and strategy discussions
- Uncovers trends in revenue, seasonality, and product performance
- Requires **zero BI tool license** — runs entirely in Python

---

### 🖼️ Walkthrough of Key Visuals

**Executive KPIs (Top Section)**
- 💰 Total Revenue — with YoY delta (▲/▼ %)
- 🛒 Total Orders — with YoY delta
- 📦 Average Order Value — with YoY delta
- 🏆 Top Product & 🌍 Top Region
- Highest sale, Lowest sale, Median order, Std Deviation

**Chart 1 — Annual Revenue + YoY Growth %**
Bar chart showing total revenue per year with growth percentage labels above each bar. Instantly shows whether the business is growing or shrinking.

**Chart 2 — Monthly Revenue (All Years Overlaid)**
Line chart overlaying all years on the same axis to reveal seasonal patterns. The most recent year is highlighted with a solid bold line.

**Chart 3 — Head-to-Head YoY Comparison**
Side-by-side monthly bars comparing any two selected years. Controlled via the sidebar — pick any base year vs compare year.

**Chart 4 — Product Revenue by Year**
Grouped bar chart showing revenue per product across all years. Quickly identifies which products are growing and which are declining.

**Chart 5 — Region Revenue by Year**
Same grouped structure but broken down by region — North, South, East, West. Shows regional expansion or contraction over time.

**Chart 6 — Quarterly Revenue by Year**
Q1–Q4 bars for every year, labeled with dollar values. Useful for quarterly business reviews and seasonal planning.

**Chart 7 — Revenue Heatmap (Product × Year)**
Color-coded matrix where darker = higher revenue. Instantly highlights the highest-performing product/year combinations at a glance.

**Chart 8 — Monthly Order Volume by Year**
Line chart tracking transaction count (not revenue) per month. Separates volume trends from pricing/value trends.

**Chart 9 — Order Value Distribution (Box Plot)**
Box plots per product showing median, spread, and outliers. Identifies which products have consistent pricing vs high variance.

**Chart 10 — Top 5 vs Bottom 5 Products**
Side-by-side horizontal bar charts showing the performance gap between best and worst products across all selected years.

---

### 💡 Business Impact & Insights

- **Sales Strategy** — Identify top-performing products and double down on what works
- **Regional Planning** — Spot underperforming regions and investigate root causes
- **Seasonal Forecasting** — Use monthly overlays to predict peak and off-peak periods
- **Inventory Management** — Understand order volume patterns to optimize stock levels
- **Executive Reporting** — KPI cards provide instant snapshot for leadership reviews

---

## 🖼️ Screenshots

### Executive KPIs + Annual Revenue
![KPIs](screenshots/kpis.png)

### Monthly Revenue — All Years Overlaid
![Monthly](screenshots/monthly_overlay.png)

### Head-to-Head YoY Comparison
![YoY](screenshots/yoy_comparison.png)

### Revenue Heatmap
![Heatmap](screenshots/heatmap.png)

### Top 5 vs Bottom 5 Products
![Top Bottom](screenshots/top_bottom.png)

---

## ⚡ Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sales-intelligence-dashboard.git
cd sales-intelligence-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run dashboard_app.py
```

Opens automatically at `http://localhost:8501`


---

*Built with ❤️ using Python & Streamlit*
