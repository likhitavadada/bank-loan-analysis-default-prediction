# Bank Loan Analysis & Default Prediction

A beginner-friendly portfolio project combining **SQL Server analysis** with **Python exploratory data analysis and machine learning** on 1,200 synthetic loan records.

> **Important:** This dataset is synthetic and generated for learning. It is not real customer or bank data. Model results are educational only and must not be used for real lending or credit decisions.

## Project scope

- SQL Server: portfolio summaries, default-rate analysis, validation checks, and loan comparisons.
- Python: data quality checks, exploratory analysis, charts, and summary reports using pandas and matplotlib.
- Machine learning: Logistic Regression and Random Forest classification models evaluated with precision, recall, F1-score, ROC-AUC, and confusion matrices.

**Data flow note:** The SQL scripts query data imported into `BankLoanProject.dbo.Loans`. The Python script currently reads `data/synthetic_loan_data.csv` directly. Both are intended to use the same CSV dataset, but Python does **not** currently connect directly to SQL Server.

## Repository structure

```text
bank-loan-analysis-default-prediction/
├── data/
│   └── synthetic_loan_data.csv
├── sql/
│   ├── 01_create_database_and_table.sql
│   ├── 02_analysis_queries.sql
│   └── 03_validation_checks.sql
├── src/
│   ├── simple_loan_analysis.py  # Beginner version to start with
│   ├── analyze_and_model.py    # Older, more advanced version
│   └── requirements.txt
├── reports/
│   └── README.md
├── .gitignore
└── README.md
```

## Dataset

The CSV contains 1,200 synthetic records and 13 columns.

| Column | Description |
|---|---|
| `customer_id` | Synthetic customer identifier |
| `age` | Simulated age |
| `income` | Simulated annual income |
| `employment_years` | Simulated years employed |
| `employment_type` | Employment category |
| `home_ownership` | Home ownership category |
| `city` | Synthetic city category |
| `loan_purpose` | Purpose of the loan |
| `loan_amount` | Simulated loan amount |
| `loan_term_months` | Loan term in months |
| `existing_debt` | Simulated existing debt |
| `credit_score` | Simulated credit-score-like value |
| `default_flag` | Target: `1` = simulated default, `0` = no simulated default |

In the included dataset, 142 of 1,200 records have `default_flag = 1` (11.83%).

## Requirements

- Python 3.10 or later
- SQL Server and SSMS for the SQL scripts
- Python packages listed in `src/requirements.txt`

## Run the Python analysis

Run commands from the repository root (the folder containing `data`, `sql`, and `src`).

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r src/requirements.txt
python src/simple_loan_analysis.py
```

If PowerShell blocks environment activation, you can run the environment's Python directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r src/requirements.txt
.\.venv\Scripts\python.exe src/analyze_and_model.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r src/requirements.txt
python src/simple_loan_analysis.py
```

The beginner script prints the data checks, shows three simple charts, trains Logistic Regression, Decision Tree, and Random Forest, and prints a model comparison. Start with `src/simple_loan_analysis.py`. The older `src/analyze_and_model.py` is retained for reference, but you do not need it for the beginner version.

## Run the SQL analysis

1. Open SSMS and connect to your SQL Server instance.
2. Open and execute `sql/01_create_database_and_table.sql`. It creates `BankLoanProject` if needed and creates `dbo.Loans` only if the table does not already exist; it will not drop an existing table.
3. Import `data/synthetic_loan_data.csv` into `BankLoanProject.dbo.Loans` using SSMS's Import Flat File wizard. Check the column mapping and data types before finishing. If the table already contains the data, do not import it a second time.
4. Verify the import:

```sql
USE BankLoanProject;
SELECT COUNT(*) AS total_rows FROM dbo.Loans;
SELECT SUM(CAST(default_flag AS int)) AS defaulted_customers FROM dbo.Loans;
```

Expected checks for the provided dataset: 1,200 rows and 142 defaulted records.

5. Execute `sql/02_analysis_queries.sql` for the portfolio analysis.
6. Execute `sql/03_validation_checks.sql` for validation checks.

The SQL scripts and Python script are separate parts of the project at this stage; there is no direct Python-to-SQL Server connection.

## Model results and interpretation

The beginner script uses a train/test split, `pd.get_dummies()` to convert category columns to numbers, and three models: Logistic Regression, Decision Tree, and Random Forest. It reports accuracy, a confusion matrix, and a classification report. No pipelines or hyperparameter tuning are used.

Do not compare models using accuracy alone. The default class is a minority class, so inspect precision, recall, F1-score, ROC-AUC, and the confusion matrix. In a lending context, false negatives and false positives have different costs.

## Limitations

- Data is synthetic; observed patterns and model metrics are not evidence of real-world credit-risk performance.
- The target is simulated, so models may learn artifacts of the data-generation process.
- This is an educational project, not a production credit-decision system.
- A real lending model would require appropriate real-world validation, leakage review, fairness assessment, explainability, calibration, governance, privacy controls, and human oversight.


