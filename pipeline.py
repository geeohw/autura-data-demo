"""
pipeline.py
-----------
Simulates pulling data from three separate systems (CRM, Support, Finance),
cleaning and validating each source, then unifying them into a single
customer health view - similar to the integration challenge at Autura.

Systems represented:
  - customers.csv   → Salesforce (CRM)
  - support_tickets.csv → Zendesk (Support)
  - revenue.csv     → NetSuite (Finance)
"""

import pandas as pd
import os

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── 1. LOAD RAW DATA ──────────────────────────────────────────────────────────

print("Loading raw data from source systems...")

customers = pd.read_csv("data/customers.csv")
tickets   = pd.read_csv("data/support_tickets.csv")
revenue   = pd.read_csv("data/revenue.csv")

print(f"  Customers loaded:       {len(customers)} rows")
print(f"  Support tickets loaded: {len(tickets)} rows")
print(f"  Revenue records loaded: {len(revenue)} rows")


# ── 2. CLEAN & VALIDATE ───────────────────────────────────────────────────────

print("\nCleaning and validating data...")

# Customers
customers["signup_date"] = pd.to_datetime(customers["signup_date"])
customers["status"] = customers["status"].str.strip().str.lower()

# Support tickets
tickets["created_date"]  = pd.to_datetime(tickets["created_date"])
tickets["resolved_date"] = pd.to_datetime(tickets["resolved_date"])
tickets["is_open"]       = tickets["resolved_date"].isna()
tickets["resolution_days"] = (
    (tickets["resolved_date"] - tickets["created_date"]).dt.days
)

# Revenue
revenue["month"] = pd.to_datetime(revenue["month"])

# Flag payment failures
failed_payments = (
    revenue[revenue["payment_status"] == "failed"]
    .groupby("customer_id")
    .size()
    .reset_index(name="failed_payment_count")
)

print("  Dates parsed, open tickets flagged, failed payments counted.")


# ── 3. AGGREGATE PER CUSTOMER ─────────────────────────────────────────────────

print("\nAggregating metrics per customer...")

# Ticket metrics
ticket_summary = tickets.groupby("customer_id").agg(
    total_tickets    = ("ticket_id", "count"),
    open_tickets     = ("is_open", "sum"),
    high_pri_tickets = ("priority", lambda x: (x == "high").sum()),
    avg_resolution_days = ("resolution_days", "mean")
).reset_index()

# Revenue metrics
revenue_summary = revenue.groupby("customer_id").agg(
    avg_mrr          = ("mrr", "mean"),
    total_revenue    = ("mrr", "sum"),
).reset_index()


# ── 4. UNIFY INTO SINGLE CUSTOMER VIEW ───────────────────────────────────────

print("Joining all sources into unified customer view...")

unified = (
    customers
    .merge(ticket_summary,   on="customer_id", how="left")
    .merge(revenue_summary,  on="customer_id", how="left")
    .merge(failed_payments,  on="customer_id", how="left")
)

# Fill nulls for customers with no tickets or revenue records
unified["total_tickets"]       = unified["total_tickets"].fillna(0).astype(int)
unified["open_tickets"]        = unified["open_tickets"].fillna(0).astype(int)
unified["high_pri_tickets"]    = unified["high_pri_tickets"].fillna(0).astype(int)
unified["failed_payment_count"]= unified["failed_payment_count"].fillna(0).astype(int)
unified["avg_mrr"]             = unified["avg_mrr"].fillna(0)
unified["total_revenue"]       = unified["total_revenue"].fillna(0)


# ── 5. DERIVE CHURN RISK SCORE ────────────────────────────────────────────────

print("Calculating churn risk scores...")

def churn_risk(row):
    score = 0
    if row["status"] == "churned":          score += 3
    if row["failed_payment_count"] >= 2:    score += 3
    elif row["failed_payment_count"] == 1:  score += 2
    if row["open_tickets"] >= 2:            score += 2
    elif row["open_tickets"] == 1:          score += 1
    if row["high_pri_tickets"] >= 2:        score += 2
    elif row["high_pri_tickets"] == 1:      score += 1
    if score >= 6:   return "High"
    elif score >= 3: return "Medium"
    else:            return "Low"

unified["churn_risk"] = unified.apply(churn_risk, axis=1)


# ── 6. EXPORT ─────────────────────────────────────────────────────────────────

out_path = os.path.join(OUTPUT_DIR, "unified_customer_view.csv")
unified.to_csv(out_path, index=False)

print(f"\nUnified customer view saved to: {out_path}")
print(f"\nChurn risk breakdown:")
print(unified["churn_risk"].value_counts().to_string())
print(f"\nFailed payment customers:")
print(unified[unified["failed_payment_count"] > 0][["name", "plan", "failed_payment_count", "churn_risk"]].to_string(index=False))
print("\nPipeline complete.")
