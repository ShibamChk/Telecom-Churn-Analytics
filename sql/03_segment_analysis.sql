-- Segment analysis query templates. Adapt optional columns to the final schema.

-- Churn by contract type
SELECT contract_group, COUNT(*) AS customers, SUM(churn_flag) AS churned_customers,
       AVG(CAST(churn_flag AS DECIMAL(10, 4))) AS churn_rate
FROM cleaned_customers GROUP BY contract_group ORDER BY churn_rate DESC;

-- Churn by tenure group
SELECT tenure_group, COUNT(*) AS customers, SUM(churn_flag) AS churned_customers,
       AVG(CAST(churn_flag AS DECIMAL(10, 4))) AS churn_rate
FROM cleaned_customers GROUP BY tenure_group ORDER BY churn_rate DESC;

-- Churn by payment method
SELECT payment_group, COUNT(*) AS customers, SUM(churn_flag) AS churned_customers,
       AVG(CAST(churn_flag AS DECIMAL(10, 4))) AS churn_rate
FROM cleaned_customers GROUP BY payment_group ORDER BY churn_rate DESC;

-- Churn by internet service
SELECT internet_service, COUNT(*) AS customers, SUM(churn_flag) AS churned_customers,
       AVG(CAST(churn_flag AS DECIMAL(10, 4))) AS churn_rate
FROM cleaned_customers GROUP BY internet_service ORDER BY churn_rate DESC;

-- Churn by monthly charge band
SELECT monthly_charge_band, COUNT(*) AS customers, SUM(churn_flag) AS churned_customers,
       AVG(CAST(churn_flag AS DECIMAL(10, 4))) AS churn_rate
FROM cleaned_customers GROUP BY monthly_charge_band ORDER BY churn_rate DESC;

-- Revenue at risk by customer value segment
SELECT customer_value_segment, SUM(revenue_at_risk) AS revenue_at_risk
FROM cleaned_customers GROUP BY customer_value_segment ORDER BY revenue_at_risk DESC;

-- Top churn reasons, only when churn_reason is available
SELECT churn_reason, COUNT(*) AS churned_customers
FROM cleaned_customers
WHERE churn_flag = 1 AND churn_reason IS NOT NULL
GROUP BY churn_reason ORDER BY churned_customers DESC;
