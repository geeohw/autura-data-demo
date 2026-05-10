"""
dashboard.py
------------
Generates a fully interactive HTML dashboard using Plotly.
Replaces analysis.py with hover tooltips, clickable legends, and
a business-ready layout for presenting to stakeholders.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load Data ─────────────────────────────────────────────────────────────────
unified = pd.read_csv("output/unified_customer_view.csv")
tickets  = pd.read_csv("data/support_tickets.csv")

RISK_COLORS = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}

# ── Build Dashboard ───────────────────────────────────────────────────────────
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "Churn Risk Distribution",
        "Avg MRR by Plan & Churn Risk",
        "Churn Signal: Open Tickets vs Failed Payments",
        "Support Ticket Volume by Category"
    ),
    specs=[
        [{"type": "bar"},    {"type": "bar"}],
        [{"type": "scatter"},{"type": "pie"}]
    ],
    vertical_spacing=0.18,
    horizontal_spacing=0.12
)


# ── Chart 1: Churn Risk Distribution ─────────────────────────────────────────
risk_counts = unified["churn_risk"].value_counts().reindex(["Low", "Medium", "High"])

fig.add_trace(
    go.Bar(
        x=risk_counts.index,
        y=risk_counts.values,
        marker_color=[RISK_COLORS[r] for r in risk_counts.index],
        text=risk_counts.values,
        textposition="outside",
        hovertemplate="<b>%{x} Risk</b><br>Customers: %{y}<extra></extra>",
        showlegend=False
    ),
    row=1, col=1
)


# ── Chart 2: Avg MRR by Plan & Risk ──────────────────────────────────────────
mrr_pivot = (
    unified.groupby(["plan", "churn_risk"])["avg_mrr"]
    .mean()
    .reset_index()
)

for risk in ["Low", "Medium", "High"]:
    subset = mrr_pivot[mrr_pivot["churn_risk"] == risk]
    fig.add_trace(
        go.Bar(
            name=risk,
            x=subset["plan"],
            y=subset["avg_mrr"],
            marker_color=RISK_COLORS[risk],
            hovertemplate=f"<b>%{{x}} Plan</b><br>Risk: {risk}<br>Avg MRR: $%{{y:.0f}}<extra></extra>",
            legendgroup=risk,
            showlegend=True
        ),
        row=1, col=2
    )


# ── Chart 3: Scatter - Open Tickets vs Failed Payments ───────────────────────
for risk in ["Low", "Medium", "High"]:
    subset = unified[unified["churn_risk"] == risk]
    fig.add_trace(
        go.Scatter(
            x=subset["failed_payment_count"],
            y=subset["open_tickets"],
            mode="markers",
            name=risk,
            marker=dict(color=RISK_COLORS[risk], size=14,
                        line=dict(width=1.5, color="white")),
            customdata=subset[["name", "plan", "status", "avg_mrr",
                                "total_tickets", "failed_payment_count"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Plan: %{customdata[1]}<br>"
                "Status: %{customdata[2]}<br>"
                "Avg MRR: $%{customdata[3]:.0f}<br>"
                "Total Tickets: %{customdata[4]}<br>"
                "Failed Payments: %{customdata[5]}<br>"
                "<extra></extra>"
            ),
            legendgroup=risk,
            showlegend=False
        ),
        row=2, col=1
    )


# ── Chart 4: Support Ticket Volume by Category ───────────────────────────────
cat_counts = tickets["category"].value_counts()

fig.add_trace(
    go.Pie(
        labels=cat_counts.index,
        values=cat_counts.values,
        hole=0.35,
        hovertemplate="<b>%{label}</b><br>Tickets: %{value}<br>Share: %{percent}<extra></extra>",
        marker=dict(line=dict(color="white", width=2)),
        showlegend=False
    ),
    row=2, col=2
)


# ── Layout ────────────────────────────────────────────────────────────────────
fig.update_layout(
    title=dict(
        text="<b>Autura Customer Health Dashboard</b>",
        font=dict(size=20),
        x=0.5
    ),
    height=750,
    barmode="group",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", size=12),
    legend=dict(
        title="Churn Risk",
        orientation="v",
        x=1.02, y=0.85
    ),
    hoverlabel=dict(bgcolor="white", font_size=12)
)

fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

fig.update_xaxes(title_text="Risk Level", row=1, col=1)
fig.update_yaxes(title_text="Number of Customers", row=1, col=1)
fig.update_xaxes(title_text="Plan", row=1, col=2)
fig.update_yaxes(title_text="Avg MRR ($)", row=1, col=2)
fig.update_xaxes(title_text="Failed Payments", row=2, col=1)
fig.update_yaxes(title_text="Open Tickets", row=2, col=1)


# ── Export ────────────────────────────────────────────────────────────────────
out_path = os.path.join(OUTPUT_DIR, "customer_health_dashboard.html")
fig.write_html(out_path, include_plotlyjs="cdn")
print(f"Interactive dashboard saved to: {out_path}")