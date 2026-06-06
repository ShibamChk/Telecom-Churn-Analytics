-- KPI query templates. Update table and column names after schema validation.

-- Total customers
SELECT COUNT(*) AS total_customers FROM cleaned_customers;

-- Churned customers
SELECT SUM(churn_flag) AS churned_customers FROM cleaned_customers;

-- Churn rate
SELECT AVG(CAST(churn_flag AS DECIMAL(10, 4))) AS churn_rate FROM cleaned_customers;

-- Retained customers
SELECT SUM(CASE WHEN churn_flag = 0 THEN 1 ELSE 0 END) AS retained_customers
FROM cleaned_customers;

-- Average tenure
SELECT AVG(tenure_months) AS average_tenure FROM cleaned_customers;

-- Average monthly charge
SELECT AVG(monthly_charge) AS average_monthly_charge FROM cleaned_customers;

-- Total monthly revenue
SELECT SUM(monthly_charge) AS total_monthly_revenue FROM cleaned_customers;

-- Revenue at risk
SELECT SUM(revenue_at_risk) AS revenue_at_risk FROM cleaned_customers;
