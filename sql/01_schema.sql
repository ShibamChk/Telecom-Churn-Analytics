-- Example schema for cleaned customer-level telecom churn data.
-- Adapt column names and data types after validating the selected dataset.

CREATE TABLE cleaned_customers (
    customer_id VARCHAR(100) PRIMARY KEY,
    gender VARCHAR(50),
    age INTEGER,
    senior_citizen INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    contract_group VARCHAR(100),
    payment_group VARCHAR(100),
    internet_service VARCHAR(100),
    phone_service VARCHAR(50),
    tenure_months INTEGER,
    tenure_group VARCHAR(50),
    monthly_charge DECIMAL(12, 2),
    monthly_charge_band VARCHAR(50),
    total_charge DECIMAL(14, 2),
    total_charge_band VARCHAR(50),
    cltv DECIMAL(14, 2),
    customer_value_segment VARCHAR(50),
    customer_status VARCHAR(50),
    churn_flag INTEGER,
    churn_reason VARCHAR(255),
    revenue_at_risk DECIMAL(12, 2)
);

CREATE INDEX idx_cleaned_customers_churn ON cleaned_customers (churn_flag);
CREATE INDEX idx_cleaned_customers_contract ON cleaned_customers (contract_group);
CREATE INDEX idx_cleaned_customers_tenure ON cleaned_customers (tenure_months);
