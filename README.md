# Telecom Customer Churn & Retention Intelligence Dashboard

A business intelligence portfolio project focused on telecom customer churn, retention behavior, customer segmentation, revenue risk, and Power BI dashboard preparation.

## Business Problem

A telecom company wants to understand why customers churn, which segments are most at risk, where revenue exposure is concentrated, when customers are most likely to leave, and which retention actions should be prioritized.

## Project Objective

Build a reproducible, schema-flexible analytics workflow that prepares customer-level churn data and dashboard-ready tables for business analysis in Python, SQL, and Power BI.

This foundation does not build a churn prediction model and does not claim dataset-specific insights before validation.

## Dataset Note

The preferred source is the Maven Telecom Customer Churn dataset or a similar customer-level telecom churn dataset. The scripts support common variations in fields such as customer ID, tenure, charges, contract, payment method, service attributes, churn status, churn reason, location, and CLTV.

Place the selected CSV manually in `data/raw/`. Raw data files are excluded from version control.

## Tools Used

- Python: pandas, NumPy, Matplotlib, Seaborn, Plotly
- Jupyter Notebook
- SQL
- Power BI and DAX
- VS Code

## Project Workflow

1. Add and validate a telecom churn CSV.
2. Run schema-flexible cleaning and derived-field creation.
3. Generate customer-level and dashboard-ready summary tables.
4. Perform exploratory analysis in the starter notebook.
5. Validate KPI definitions with SQL templates.
6. Build and document the Power BI dashboard.
7. Translate validated findings into retention recommendations.

## Folder Structure

```text
telecom-churn-analytics/
|-- data/
|   |-- raw/
|   `-- processed/
|-- notebooks/
|-- sql/
|-- powerbi/
|-- reports/
|   `-- figures/
|-- src/
|-- README.md
|-- requirements.txt
`-- .gitignore
```

## Planned Dashboard Pages

1. Executive Overview
2. Customer Segmentation
3. Service and Contract Analysis
4. Retention Strategy

## Planned KPIs

- Total Customers
- Churned Customers
- Retained Customers
- Churn Rate
- Retention Rate
- Average Tenure
- Average Monthly Charge
- Total Monthly Revenue
- Revenue at Risk
- Average CLTV, if available
- Churned Revenue %
- High Risk Customer Count, if supported

## Custom Visual Concept: Customer Retention Survival Curve

The retention curve shows the approximate percentage of customers retained over tenure months by contract type or another available segment. It is designed to help identify when customer loss is most concentrated.

The generated curve is an approximation based on current customer tenure and churn status, not a true longitudinal survival analysis.

## How to Run

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/clean_data.py
python src/create_model_tables.py
jupyter notebook notebooks/01_eda_telecom_churn.ipynb
```

## Power BI Dashboard Plan

Import `fact_customers.csv`, available summary tables, and `retention_curve_table.csv` from `data/processed/`. Use the planned DAX measures and build notes in `powerbi/` as a starting point. Finalize visuals only after checking column mappings and KPI definitions.

## Limitations

- The exact dataset schema has not yet been validated.
- Optional outputs depend on available columns.
- Derived value bands are relative quantile-based segments.
- The retention curve is approximate and is not based on longitudinal event history.
- No causal claims or business insights should be made before analysis validation.

## Future Improvements

- Finalize schema mappings after dataset review.
- Add tested data-quality checks and a data dictionary.
- Refine Power BI model relationships and visual design.
- Add time-based cohort analysis if historical snapshots become available.
- Consider predictive modeling only as a separate future phase.
