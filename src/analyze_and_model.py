"""
Bank Loan Analysis & Default Prediction
Educational project using a synthetic dataset. Not for real credit decisions.
Run from the repository root: python src/analyze_and_model.py
"""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "synthetic_loan_data.csv"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

RANDOM_STATE = 42
TARGET = "default_flag"
ID_COL = "customer_id"


def load_data(path: Path) -> pd.DataFrame:
    """Load CSV and validate expected columns."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run this script from the project folder "
            "or restore data/synthetic_loan_data.csv."
        )
    data = pd.read_csv(path)
    required = {
        ID_COL, "age", "income", "employment_years", "employment_type",
        "home_ownership", "city", "loan_purpose", "loan_amount",
        "loan_term_months", "existing_debt", "credit_score", TARGET
    }
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    if data[ID_COL].duplicated().any():
        raise ValueError("customer_id must be unique in this dataset.")
    if not set(data[TARGET].dropna().unique()).issubset({0, 1}):
        raise ValueError("default_flag must contain only 0 and 1.")
    return data


def save_eda(data: pd.DataFrame) -> dict:
    """Create summary tables and EDA charts, and return a few key stats."""
    summary = {
        "rows": int(len(data)),
        "columns": int(data.shape[1]),
        "missing_cells": int(data.isna().sum().sum()),
        "duplicate_customer_ids": int(data[ID_COL].duplicated().sum()),
        "default_rate_pct": round(float(data[TARGET].mean() * 100), 2),
    }
    (REPORTS / "data_quality_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    data.describe(include="all").transpose().to_csv(REPORTS / "descriptive_summary.csv")
    data.groupby(TARGET).agg(
        customers=(ID_COL, "count"),
        avg_income=("income", "mean"),
        avg_loan_amount=("loan_amount", "mean"),
        avg_credit_score=("credit_score", "mean"),
    ).round(2).to_csv(REPORTS / "summary_by_default_flag.csv")

    by_purpose = data.groupby("loan_purpose").agg(
        total_records=(ID_COL, "count"),
        total_defaults=(TARGET, "sum"),
        default_rate=(TARGET, "mean"),
    ).sort_values("default_rate", ascending=False)
    by_purpose["default_rate_pct"] = (100 * by_purpose.pop("default_rate")).round(2)
    by_purpose.to_csv(REPORTS / "default_rate_by_loan_purpose.csv")

    # Use Matplotlib's defaults so the script runs across seaborn versions.
    plt.figure(figsize=(8, 5))
    data[TARGET].value_counts().sort_index().plot(kind="bar")
    plt.title("Synthetic loan records by default flag")
    plt.xlabel("Default flag (1 = simulated default)")
    plt.ylabel("Number of records")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(REPORTS / "target_distribution.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    data.boxplot(column="credit_score", by=TARGET)
    plt.title("Credit-score-like values by simulated outcome")
    plt.suptitle("")
    plt.xlabel("Default flag (1 = simulated default)")
    plt.ylabel("Credit score-like value")
    plt.tight_layout()
    plt.savefig(REPORTS / "credit_score_by_outcome.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    plot_data = by_purpose.reset_index()
    plt.bar(plot_data["loan_purpose"], plot_data["default_rate_pct"])
    plt.title("Simulated default rate by loan purpose")
    plt.xlabel("Loan purpose")
    plt.ylabel("Default rate (%)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(REPORTS / "default_rate_by_purpose.png", dpi=160)
    plt.close()
    return summary


def build_preprocessor(numeric_features, categorical_features):
    numeric_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer(transformers=[
        ("numeric", numeric_pipe, numeric_features),
        ("categorical", categorical_pipe, categorical_features),
    ])


def train_and_evaluate(data: pd.DataFrame) -> dict:
    # ID is not a predictive feature. Target is kept separate to avoid leakage.
    numeric_features = [
        "age", "income", "employment_years", "loan_amount",
        "loan_term_months", "existing_debt", "credit_score"
    ]
    categorical_features = [
        "employment_type", "home_ownership", "city", "loan_purpose"
    ]
    X = data[numeric_features + categorical_features]
    y = data[TARGET].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )
    preprocessor = build_preprocessor(numeric_features, categorical_features)
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=RANDOM_STATE
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1
        ),
    }
    results = {}
    report_lines = [
        "MODEL EVALUATION — SYNTHETIC DATA ONLY",
        "These results demonstrate an educational workflow, not real credit-risk performance.",
        f"Train rows: {len(X_train)} | Test rows: {len(X_test)}",
        f"Test default rate: {y_test.mean() * 100:.2f}%",
        "",
    ]
    for name, estimator in models.items():
        pipe = Pipeline(steps=[
            ("preprocessor", build_preprocessor(numeric_features, categorical_features)),
            ("model", estimator),
        ])
        pipe.fit(X_train, y_train)
        predictions = pipe.predict(X_test)
        probabilities = pipe.predict_proba(X_test)[:, 1]
        metrics = {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "precision_default_class": float(precision_score(y_test, predictions, zero_division=0)),
            "recall_default_class": float(recall_score(y_test, predictions, zero_division=0)),
            "f1_default_class": float(f1_score(y_test, predictions, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, probabilities)) if y_test.nunique() == 2 else None,
        }
        results[name] = metrics
        report_lines += [
            f"=== {name} ===",
            json.dumps(metrics, indent=2),
            "Confusion matrix (rows=true [0,1], columns=predicted [0,1]):",
            str(confusion_matrix(y_test, predictions, labels=[0, 1])),
            "Classification report:",
            classification_report(y_test, predictions, labels=[0, 1], zero_division=0),
            "",
        ]
        fig, ax = plt.subplots(figsize=(5, 4))
        matrix = confusion_matrix(y_test, predictions, labels=[0, 1])
        ax.imshow(matrix, interpolation="nearest")
        ax.set_xticks([0, 1], labels=["Predicted 0", "Predicted 1"])
        ax.set_yticks([0, 1], labels=["Actual 0", "Actual 1"])
        for row in range(2):
            for col in range(2):
                ax.text(col, row, str(matrix[row, col]), ha="center", va="center")
        ax.set_title(f"{name}: confusion matrix")
        ax.set_xlabel("Predicted class")
        ax.set_ylabel("Actual class")
        fig.tight_layout()
        safe_name = name.lower().replace(" ", "_")
        fig.savefig(REPORTS / f"confusion_matrix_{safe_name}.png", dpi=160)
        plt.close(fig)

    (REPORTS / "model_metrics.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    (REPORTS / "model_evaluation.txt").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    return results


def main():
    warnings.filterwarnings("ignore", category=FutureWarning)
    data = load_data(DATA_PATH)
    print("DATASET OVERVIEW")
    print(f"Rows: {len(data):,}; columns: {data.shape[1]}")
    print(f"Missing cells: {data.isna().sum().sum()}")
    print(f"Duplicate IDs: {data[ID_COL].duplicated().sum()}")
    print(f"Synthetic default rate: {data[TARGET].mean() * 100:.2f}%")
    print("\nSUMMARY BY DEFAULT FLAG")
    print(data.groupby(TARGET).agg(
        customers=(ID_COL, "count"),
        avg_income=("income", "mean"),
        avg_loan_amount=("loan_amount", "mean"),
        avg_credit_score=("credit_score", "mean"),
    ).round(2))
    summary = save_eda(data)
    metrics = train_and_evaluate(data)
    print("\nDATA QUALITY SUMMARY")
    print(json.dumps(summary, indent=2))
    print("\nMODEL METRICS")
    print(json.dumps(metrics, indent=2))
    print(f"\nCharts and reports saved to: {REPORTS}")
    print("Reminder: this dataset is synthetic and model metrics are educational only.")


if __name__ == "__main__":
    main()
