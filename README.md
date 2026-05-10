# Autura Data Integration Demo

A small end-to-end data project simulating the core challenge at Autura: pulling customer data from multiple disconnected systems, cleaning and unifying it, and surfacing actionable insights.

## The Problem

Customer data lives in three separate places with no shared view:
- **Salesforce** → customer records and subscription status
- **Zendesk** → support tickets and resolution history  
- **NetSuite** → monthly revenue and payment status

This project stitches them together into a single unified customer health view and visualizes key metrics like churn risk, MRR by plan, and support volume patterns.

## Project Structure

```
autura-data-demo/
├── data/
│   ├── customers.csv          # Simulated CRM data (Salesforce)
│   ├── support_tickets.csv    # Simulated support data (Zendesk)
│   └── revenue.csv            # Simulated finance data (NetSuite)
├── pipeline.py                # Data cleaning, joining, and churn scoring
├── dashboard.py               # Interactive Plotly dashboard with hover tooltips
├── output/
│   ├── unified_customer_view.csv
│   └── customer_health_dashboard.html
└── README.md
```

## How to Run

```bash
pip install pandas plotly
python pipeline.py
python dashboard.py
```

## What the Pipeline Does

1. **Loads** raw CSVs from each simulated source system
2. **Cleans and validates** dates, payment statuses, and ticket fields
3. **Aggregates** per-customer metrics: total tickets, open tickets, high-priority tickets, average MRR, failed payments
4. **Joins** all sources on `customer_id` into a single unified view
5. **Scores** each customer with a churn risk label (Low / Medium / High) based on payment failures, open tickets, and subscription status
6. **Exports** the unified view to CSV and a visual dashboard to PNG

## Dashboard Output

The dashboard is fully interactive and opens in any browser. Hover over any data point to see customer details, click legend items to filter by risk level, and zoom into any chart.

Charts included:
- Churn risk distribution across all customers
- Average MRR broken down by plan and risk level
- Scatter plot of open tickets vs failed payments as churn signals, with full customer details on hover
- Support ticket volume by category

Open `output/customer_health_dashboard.html` in your browser to explore it.

## Key Finding

All three High Risk customers share the same pattern: churned status, 2 failed payments, and 2 unresolved open tickets. This kind of signal would be invisible if the data lived in separate systems with no unified view.