# Planned DAX Measures

These measures assume the primary Power BI table is named `fact_customers`. Adjust field names after validating the dataset.

```DAX
Total Customers =
COUNTROWS(fact_customers)

Churned Customers =
CALCULATE([Total Customers], fact_customers[churn_flag] = 1)

Retained Customers =
CALCULATE([Total Customers], fact_customers[churn_flag] = 0)

Churn Rate =
DIVIDE([Churned Customers], [Total Customers])

Retention Rate =
DIVIDE([Retained Customers], [Total Customers])

Total Monthly Revenue =
SUM(fact_customers[monthly_charge])

Revenue at Risk =
SUM(fact_customers[revenue_at_risk])

Average Monthly Charge =
AVERAGE(fact_customers[monthly_charge])

Average Tenure =
AVERAGE(fact_customers[tenure])

Average CLTV =
AVERAGE(fact_customers[cltv])

Churned Revenue % =
DIVIDE([Revenue at Risk], [Total Monthly Revenue])

High Risk Customer Count =
CALCULATE(
    [Total Customers],
    fact_customers[churn_flag] = 1,
    fact_customers[customer_value_segment] = "High Value"
)
```

`Average CLTV` and `High Risk Customer Count` are optional and should only be added when their source columns exist. Replace `monthly_charge` and `tenure` with the validated cleaned column names if needed.
