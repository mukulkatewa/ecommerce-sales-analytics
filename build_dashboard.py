"""Build the interactive KPI dashboard (docs/index.html, served by GitHub Pages) and README charts."""
from pathlib import Path

import matplotlib
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).parent
OUT = ROOT / "outputs"
CHARTS = ROOT / "charts"
DOCS = ROOT / "docs"
CHARTS.mkdir(exist_ok=True)
DOCS.mkdir(exist_ok=True)

monthly = pd.read_csv(OUT / "01_monthly_revenue_mom.csv", parse_dates=["month"])
cats = pd.read_csv(OUT / "02_category_revenue_share.csv")
cohort = pd.read_csv(OUT / "03_cohort_retention.csv", parse_dates=["cohort_month"])
repeat = pd.read_csv(OUT / "04_repeat_customer_rate.csv").iloc[0]
delivery = pd.read_csv(OUT / "05_delivery_vs_reviews.csv").set_index("delivery_status")
states = pd.read_csv(OUT / "06_state_performance.csv")
payments = pd.read_csv(OUT / "07_payment_mix.csv")

total_revenue = states["revenue"].sum()
total_orders = states["orders"].sum()
kpis = {
    "Revenue (BRL)": f"{total_revenue / 1e6:.2f}M",
    "Delivered orders": f"{total_orders:,}",
    "Avg order value": f"R$ {total_revenue / total_orders:.0f}",
    "Repeat customers": f"{repeat['repeat_rate_pct']:.1f}%",
    "Late deliveries": f"{delivery.loc['late', 'pct_of_orders']:.1f}%",
    "Avg review": f"{(delivery['avg_review_score'] * delivery['orders']).sum() / delivery['orders'].sum():.2f} / 5",
}

# ---------- interactive dashboard ----------
pivot = cohort.pivot(index="cohort_month", columns="month_number", values="retention_pct").drop(columns=0)
top = cats.head(15)

fig = make_subplots(
    rows=3, cols=2,
    subplot_titles=(
        "Monthly revenue & MoM growth", "Top 15 categories (bars) & cumulative share (line)",
        "Late vs on-time delivery: avg review score", "Cohort retention % (months after first order)",
        "Revenue by state (top 10)", "Payment method mix",
    ),
    specs=[[{"secondary_y": True}, {"secondary_y": True}],
           [{}, {}],
           [{}, {"type": "domain"}]],
    vertical_spacing=0.1, horizontal_spacing=0.1,
)
fig.add_bar(x=monthly["month"], y=monthly["revenue"], name="Revenue", marker_color="#2E6F9E", row=1, col=1)
fig.add_scatter(x=monthly["month"], y=monthly["mom_growth_pct"], name="MoM growth %", mode="lines+markers",
                line_color="#E07A1F", row=1, col=1, secondary_y=True)
fig.add_bar(x=top["category"], y=top["revenue"], name="Category revenue", marker_color="#3C8D6E", row=1, col=2)
fig.add_scatter(x=top["category"], y=top["cumulative_share_pct"], name="Cumulative share %", mode="lines+markers",
                line_color="#B23A48", row=1, col=2, secondary_y=True)
fig.add_bar(x=["On time", "Late"], y=[delivery.loc["on_time", "avg_review_score"], delivery.loc["late", "avg_review_score"]],
            marker_color=["#3C8D6E", "#B23A48"], name="Avg review", text=[f"{v:.2f}" for v in
            [delivery.loc["on_time", "avg_review_score"], delivery.loc["late", "avg_review_score"]]], row=2, col=1)
fig.add_heatmap(z=pivot.values, x=[f"M{c}" for c in pivot.columns], y=pivot.index.strftime("%Y-%m"),
                colorscale="Blues", name="Retention %", colorbar=dict(len=0.3, y=0.5), row=2, col=2)
s10 = states.head(10)
fig.add_bar(x=s10["state"], y=s10["revenue"], name="State revenue", marker_color="#5B5EA6",
            customdata=s10[["aov", "late_delivery_pct"]],
            hovertemplate="%{x}<br>Revenue R$ %{y:,.0f}<br>AOV R$ %{customdata[0]}<br>Late %{customdata[1]}%",
            row=3, col=1)
fig.add_pie(labels=payments["payment_type"], values=payments["orders"], hole=0.45, name="Payments", row=3, col=2)
fig.update_layout(height=1350, showlegend=False, template="plotly_white", margin=dict(t=40, l=40, r=40, b=40))

kpi_html = "".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{k}</div></div>' for k, v in kpis.items())
html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>E-Commerce Sales Dashboard</title>
<style>body{{font-family:system-ui,sans-serif;margin:0;background:#f6f7f9;color:#1d2433}}
header{{padding:24px 32px 8px}}h1{{margin:0;font-size:24px}}p{{margin:6px 0 0;color:#5a6270}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;padding:16px 32px}}
.kpi{{background:#fff;border-radius:10px;padding:14px 16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.v{{font-size:22px;font-weight:700}}.l{{font-size:13px;color:#5a6270}}.chart{{background:#fff;margin:0 32px 32px;border-radius:10px}}</style>
</head><body><header><h1>Olist E-Commerce Sales &amp; Customer Dashboard</h1>
<p>96k+ delivered orders, Brazil, Jan 2017 – Aug 2018 · built with SQL (DuckDB) + Python + Plotly ·
<a href="https://github.com/mukulkatewa/ecommerce-sales-analytics">source</a></p></header>
<div class="kpis">{kpi_html}</div><div class="chart">{fig.to_html(full_html=False, include_plotlyjs="cdn")}</div></body></html>"""
(DOCS / "index.html").write_text(html)

# ---------- static charts for README ----------
sns.set_theme(style="whitegrid")
fig1, ax = plt.subplots(figsize=(10, 4))
ax.bar(monthly["month"].dt.strftime("%Y-%m"), monthly["revenue"] / 1e3, color="#2E6F9E")
ax.set_ylabel("Revenue (BRL thousands)"); ax.set_title("Monthly revenue (delivered orders)")
plt.xticks(rotation=60); plt.tight_layout(); fig1.savefig(CHARTS / "monthly_revenue.png", dpi=120)

fig2, ax = plt.subplots(figsize=(10, 4))
sns.barplot(data=top, x="category", y="share_pct", color="#3C8D6E", ax=ax)
ax2 = ax.twinx(); ax2.plot(range(len(top)), top["cumulative_share_pct"], color="#B23A48", marker="o")
ax.set_ylabel("Share of revenue %"); ax2.set_ylabel("Cumulative %"); ax.set_xlabel("")
ax.set_title("Revenue concentration by category"); plt.setp(ax.get_xticklabels(), rotation=60, ha="right")
plt.tight_layout(); fig2.savefig(CHARTS / "category_pareto.png", dpi=120)

fig3, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(pivot.iloc[:, :6], annot=True, fmt=".2f", cmap="Blues", ax=ax,
            yticklabels=pivot.index.strftime("%Y-%m"))
ax.set_title("Cohort retention % (months after first purchase)"); ax.set_xlabel("Month"); ax.set_ylabel("Cohort")
plt.tight_layout(); fig3.savefig(CHARTS / "cohort_retention.png", dpi=120)

fig4, ax = plt.subplots(figsize=(6, 4))
d = delivery.reset_index()
sns.barplot(data=d, x="delivery_status", y="avg_review_score", hue="delivery_status",
            palette={"late": "#B23A48", "on_time": "#3C8D6E"}, legend=False, ax=ax)
ax.set_ylim(0, 5); ax.set_title("Avg review score: late vs on-time"); ax.set_xlabel("")
plt.tight_layout(); fig4.savefig(CHARTS / "delivery_vs_reviews.png", dpi=120)

print(kpis)
print("SP share of revenue: %.1f%%" % (100 * states.loc[states.state == "SP", "revenue"].iloc[0] / total_revenue))
print("Top10 categories cum share:", cats.loc[9, "cumulative_share_pct"], "of", len(cats), "categories")
print("Nov-2017 MoM:", monthly.loc[monthly.month == "2017-11-01", "mom_growth_pct"].iloc[0])
print("Month-1 retention median: %.2f%%" % pivot[1].median())
print("neg review ratio: %.1fx" % (delivery.loc["late", "pct_negative_reviews"] / delivery.loc["on_time", "pct_negative_reviews"]))
