USE BankLoanProject;
GO

-- 1. Portfolio size and overall default rate
SELECT
    COUNT(*) AS total_records,
    SUM(CAST(default_flag AS INT)) AS total_defaults,
    CAST(100.0 * SUM(CAST(default_flag AS INT)) / NULLIF(COUNT(*), 0) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Loans;

-- 2. Compare average loan amount and income by recorded outcome
SELECT
    default_flag,
    COUNT(*) AS customer_count,
    AVG(CAST(loan_amount AS DECIMAL(18,2))) AS avg_loan_amount,
    AVG(CAST(income AS DECIMAL(18,2))) AS avg_income
FROM dbo.Loans
GROUP BY default_flag
ORDER BY default_flag;

-- 3. Default rate by income band (practice band, not a banking standard)
WITH income_bands AS (
    SELECT
        CASE WHEN income < 40000 THEN 'Low income'
             WHEN income < 70000 THEN 'Middle income'
             ELSE 'High income' END AS income_band,
        CAST(default_flag AS INT) AS default_int
    FROM dbo.Loans
)
SELECT
    income_band,
    COUNT(*) AS total_customers,
    SUM(default_int) AS total_defaults,
    CAST(100.0 * SUM(default_int) / NULLIF(COUNT(*), 0) AS DECIMAL(6,2)) AS default_rate_pct
FROM income_bands
GROUP BY income_band
ORDER BY CASE income_band WHEN 'Low income' THEN 1 WHEN 'Middle income' THEN 2 ELSE 3 END;

-- 4. Default rate by credit score band (illustrative cutoffs only)
WITH score_bands AS (
    SELECT
        CASE WHEN credit_score < 600 THEN 'Below 600'
             WHEN credit_score < 700 THEN '600-699'
             ELSE '700+' END AS score_band,
        CAST(default_flag AS INT) AS default_int
    FROM dbo.Loans
)
SELECT
    score_band,
    COUNT(*) AS total_customers,
    SUM(default_int) AS total_defaults,
    CAST(100.0 * SUM(default_int) / NULLIF(COUNT(*), 0) AS DECIMAL(6,2)) AS default_rate_pct
FROM score_bands
GROUP BY score_band
ORDER BY CASE score_band WHEN 'Below 600' THEN 1 WHEN '600-699' THEN 2 ELSE 3 END;

-- 5. Default rate by loan purpose
SELECT
    loan_purpose,
    COUNT(*) AS total_loans,
    SUM(CAST(default_flag AS INT)) AS total_defaults,
    CAST(100.0 * SUM(CAST(default_flag AS INT)) / NULLIF(COUNT(*), 0) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Loans
GROUP BY loan_purpose
ORDER BY default_rate_pct DESC;

-- 6. Highest loan-to-income ratios; ratio is a descriptive flag, not an approval rule
SELECT TOP (20)
    customer_id,
    income,
    loan_amount,
    CAST(1.0 * loan_amount / NULLIF(income, 0) AS DECIMAL(10,2)) AS loan_to_income_ratio,
    credit_score,
    default_flag
FROM dbo.Loans
ORDER BY loan_to_income_ratio DESC;

-- 7. City-level summary
SELECT
    city,
    COUNT(*) AS total_records,
    AVG(CAST(loan_amount AS DECIMAL(18,2))) AS avg_loan_amount,
    SUM(CAST(default_flag AS INT)) AS total_defaults,
    CAST(100.0 * SUM(CAST(default_flag AS INT)) / NULLIF(COUNT(*), 0) AS DECIMAL(6,2)) AS default_rate_pct
FROM dbo.Loans
GROUP BY city
ORDER BY default_rate_pct DESC;

-- 8. Show the 10 largest loans
SELECT TOP (10)
    customer_id, loan_amount, income, credit_score, default_flag
FROM dbo.Loans
ORDER BY loan_amount DESC;
