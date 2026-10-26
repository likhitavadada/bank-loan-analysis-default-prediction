USE BankLoanProject;
GO

-- Run these checks after importing the CSV.

-- 1. Expected number of records: 1200
SELECT COUNT(*) AS row_count FROM dbo.Loans;

-- 2. Duplicate customer keys (should return zero rows)
SELECT customer_id, COUNT(*) AS copies
FROM dbo.Loans
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 3. Missing values are prevented for required fields by NOT NULL constraints.
-- Check ranges anyway:
SELECT *
FROM dbo.Loans
WHERE age NOT BETWEEN 18 AND 100
   OR income < 0
   OR loan_amount < 0
   OR credit_score NOT BETWEEN 300 AND 850;

-- 4. Target distribution
SELECT
    default_flag,
    COUNT(*) AS records,
    CAST(100.0 * COUNT(*) / SUM(COUNT(*)) OVER () AS DECIMAL(6,2)) AS pct_records
FROM dbo.Loans
GROUP BY default_flag
ORDER BY default_flag;
