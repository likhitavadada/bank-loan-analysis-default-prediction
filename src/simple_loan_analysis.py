"""
Bank Loan Analysis & Default Prediction - Beginner Version
This project uses synthetic data for learning only.
Run from the project folder: python src/simple_loan_analysis.py
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Find the project folder and load the dataset.
project_folder = Path(__file__).resolve().parents[1]
data_path = project_folder / "data" / "synthetic_loan_data.csv"

df = pd.read_csv(data_path)

# 1. Explore the data
print("FIRST FIVE ROWS")
print(df.head())

print("\nDATASET SIZE (rows, columns)")
print(df.shape)

print("\nCOLUMN DATA TYPES")
print(df.dtypes)

print("\nMISSING VALUES IN EACH COLUMN")
print(df.isnull().sum())

print("\nDUPLICATE ROWS")
print(df.duplicated().sum())

print("\nSUMMARY OF NUMERICAL COLUMNS")
print(df.describe())

print("\nDEFAULT COUNTS (0 = no simulated default, 1 = simulated default)")
print(df["default_flag"].value_counts())

# 2. Simple visualizations
plt.figure(figsize=(6, 4))
df["default_flag"].value_counts().sort_index().plot(kind="bar")
plt.title("Number of Loans by Default Flag")
plt.xlabel("Default Flag")
plt.ylabel("Number of Records")
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 4))
plt.hist(df["income"], bins=20, edgecolor="black")
plt.title("Distribution of Income")
plt.tight_layout()
plt.show()

plt.figure(figsize=(7, 4))
df.boxplot(column="credit_score", by="default_flag")
plt.title("Credit Score by Default Flag")
plt.tight_layout()
plt.show()

# 3. Prepare data for machine learning
# customer_id is an identifier, so we do not use it to make predictions.
X = df.drop(columns=["customer_id", "default_flag"])
y = df["default_flag"]

# Convert text/category columns into numeric columns.
X = pd.get_dummies(X, drop_first=True)

# Fill any missing values with each column's median (a simple beginner approach).
X = X.fillna(X.median())

# Keep some records for testing and use the rest to train the models.
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 4. Train three beginner-friendly classification models.
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
}

results = []

for model_name, model in models.items():
    print("\n" + "=" * 50)
    print(model_name)
    print("=" * 50)

    # Learn patterns from the training data.
    model.fit(X_train, y_train)

    # Predict the outcomes for data the model has not seen before.
    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    results.append({"Model": model_name, "Accuracy": round(accuracy, 3)})

    print("Accuracy:", round(accuracy, 3))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    print("\nClassification Report:")
    print(classification_report(y_test, predictions, zero_division=0))

# 5. Compare the models using accuracy.
results_df = pd.DataFrame(results).sort_values(by="Accuracy", ascending=False)
print("\nMODEL COMPARISON")
print(results_df.to_string(index=False))

print("\nReminder: this dataset is synthetic. These results are for learning only, "
      "not for real lending or credit decisions.")
