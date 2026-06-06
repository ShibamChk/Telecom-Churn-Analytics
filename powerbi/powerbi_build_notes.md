# Power BI Build Notes

## Data Model

- Import `fact_customers.csv` as the primary customer-level table.
- Import available summary CSV files for focused visuals.
- Import `retention_curve_table.csv` for the retention curve.
- Validate data types, sort orders, relationships, and optional fields before building visuals.

## Page 1: Executive Overview

KPIs:

- Total Customers
- Churned Customers
- Churn Rate
- Retained Customers
- Average Tenure
- Average Monthly Charge
- Total Monthly Revenue
- Revenue at Risk

Suggested visuals: KPI cards, churn trend or tenure distribution, contract churn comparison, and revenue-at-risk summary.

## Page 2: Customer Segmentation

- Churn by demographic fields, if available
- Churn by geography, if available
- Churn by monthly charge band
- Churn by customer value segment
- Revenue risk by segment

## Page 3: Service and Contract Analysis

- Churn by contract type
- Churn by payment method
- Churn by internet service
- Churn by add-on services
- Tenure vs churn
- Monthly charges vs churn

## Page 4: Retention Strategy

- Revenue at Risk Matrix
- High-risk segments
- Customer Retention Survival Curve
- Churn reason priority list, if available
- Recommended retention actions grounded in validated findings

## Custom Visual Concept: Customer Retention Survival Curve

This line chart shows the percentage of customers retained over tenure months by segment or contract type. It helps identify the tenure periods when customer loss is most concentrated.

Use `retention_curve_table.csv` with:

- X-axis: `tenure_month`
- Y-axis: `retention_rate`
- Legend: `segment`
- Tooltip: `customers_eligible`, `customers_retained`

Start with a standard Power BI line chart. A Deneb/Vega-Lite version can be considered later if custom formatting or richer annotations are needed.

Important: the generated table is an approximation based on current tenure and current churn status, not a true longitudinal survival dataset.
