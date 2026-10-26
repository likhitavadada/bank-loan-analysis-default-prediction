/*
Project: Bank Loan Analysis & Default Prediction
Platform: Microsoft SQL Server
IMPORTANT: Run in SSMS. This creates a separate practice database/table.
The CSV is synthetic. Do not use this dataset for real credit decisions.
*/
IF DB_ID(N'BankLoanProject') IS NULL
BEGIN
    CREATE DATABASE BankLoanProject;
END;
GO

USE BankLoanProject;
GO

IF OBJECT_ID(N'dbo.Loans', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Loans (
        customer_id       VARCHAR(10)  NOT NULL PRIMARY KEY,
        age               TINYINT      NOT NULL,
        income            INT          NOT NULL,
        employment_years  TINYINT      NOT NULL,
        employment_type   VARCHAR(30)  NOT NULL,
        home_ownership    VARCHAR(20)  NOT NULL,
        city              VARCHAR(40)  NOT NULL,
        loan_purpose      VARCHAR(30)  NOT NULL,
        loan_amount       INT          NOT NULL,
        loan_term_months  SMALLINT     NOT NULL,
        existing_debt     INT          NOT NULL,
        credit_score      SMALLINT     NOT NULL,
        default_flag      BIT          NOT NULL,
        CONSTRAINT CK_Loans_Age CHECK (age BETWEEN 18 AND 100),
        CONSTRAINT CK_Loans_Income CHECK (income >= 0),
        CONSTRAINT CK_Loans_LoanAmount CHECK (loan_amount >= 0),
        CONSTRAINT CK_Loans_CreditScore CHECK (credit_score BETWEEN 300 AND 850),
        CONSTRAINT CK_Loans_DefaultFlag CHECK (default_flag IN (0, 1))
    );
END
ELSE
BEGIN
    PRINT 'dbo.Loans already exists; it was not dropped or changed.';
END;
GO

-- Import data/synthetic_loan_data.csv into dbo.Loans using SSMS Import Flat File.
-- The Python script currently reads the CSV directly; it does not connect to SQL Server.
