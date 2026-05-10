"""
analysis.py
-----------
Reads the unified customer view produced by pipeline.py and generates
business-ready visualizations similar to what ThoughtSpot would surface.

Charts produced:
  1. Churn risk distribution
  2. Average MRR by plan and churn risk
  3. Open tickets vs failed payments (churn signal scatter)
  4. Support ticket volume by category breakdown
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="muted")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load unified data
unified = pd.read_csv("output/unified_customer_view.csv")
tickets = pd.read_csv("data/support_tickets.csv")

RISK_COLORS = {"Low": "#4CAF50", "Medium": "#FF9800", "High": "#F44336"}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Autura Customer Health Dashboard", fontsize=16, fontweight="bold", y=1.01)


# ── Chart 1: Churn Risk Distribution ─────────────────────────────────────────
ax1 = axes[0, 0]
risk_counts = unified["churn_risk"].value_counts().reindex(["Low", "Medium", "High"])
bars = ax1.bar(risk_counts.index, risk_counts.values,
               color=[RISK_COLORS[r] for r in risk_counts.index], width=0.5)
ax1.set_title("Churn Risk Distribution", fontweight="bold")
ax1.set_ylabel("Number of Customers")
ax1.set_xlabel("Risk Level")
for bar, val in zip(bars, risk_counts.values):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             str(val), ha="center", va="bottom", fontweight="bold")


# ── Chart 2: Avg MRR by Plan and Risk ────────────────────────────────────────
ax2 = axes[0, 1]
mrr_pivot = unified.groupby(["plan", "churn_risk"])["avg_mrr"].mean().unstack(fill_value=0)
mrr_pivot = mrr_pivot.reindex(columns=["Low", "Medium", "High"])
mrr_pivot.plot(kind="bar", ax=ax2,
               color=[RISK_COLORS[c] for c in mrr_pivot.columns],
               width=0.6, edgecolor="white")
ax2.set_title("Avg MRR by Plan & Churn Risk", fontweight="bold")
ax2.set_ylabel("Average MRR ($)")
ax2.set_xlabel("Plan")
ax2.tick_params(axis="x", rotation=0)
ax2.legend(title="Risk", labels=["Low", "Medium", "High"])


# ── Chart 3: Open Tickets vs Failed Payments ──────────────────────────────────
ax3 = axes[1, 0]
for risk, group in unified.groupby("churn_risk"):
    ax3.scatter(group["failed_payment_count"], group["open_tickets"],
                color=RISK_COLORS[risk], label=risk, s=120, edgecolors="white", linewidths=0.8)
    for _, row in group.iterrows():
        ax3.annotate(row["name"].split()[0],
                     (row["failed_payment_count"], row["open_tickets"]),
                     textcoords="offset points", xytext=(6, 4), fontsize=7, color="#555")
ax3.set_title("Churn Signal: Open Tickets vs Failed Payments", fontweight="bold")
ax3.set_xlabel("Failed Payments")
ax3.set_ylabel("Open Tickets")
patches = [mpatches.Patch(color=RISK_COLORS[r], label=r) for r in ["Low", "Medium", "High"]]
ax3.legend(handles=patches, title="Risk")


# ── Chart 4: Support Ticket Volume by Category ───────────────────────────────
ax4 = axes[1, 1]
cat_counts = tickets["category"].value_counts()
wedges, texts, autotexts = ax4.pie(
    cat_counts.values, labels=cat_counts.index, autopct="%1.0f%%",
    startangle=140, colors=sns.color_palette("muted", len(cat_counts)),
    wedgeprops={"edgecolor": "white", "linewidth": 1.5}
)
for t in autotexts:
    t.set_fontsize(9)
ax4.set_title("Support Ticket Volume by Category", fontweight="bold")


plt.tight_layout()
out_path = os.path.join(OUTPUT_DIR, "customer_health_dashboard.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"Dashboard saved to: {out_path}")

# ── Summary Table ─────────────────────────────────────────────────────────────
print("\nHigh Risk Customers:")
high_risk = unified[unified["churn_risk"] == "High"][[
    "name", "plan", "status", "total_tickets", "open_tickets",
    "failed_payment_count", "avg_mrr"
]]
print(high_risk.to_string(index=False))
