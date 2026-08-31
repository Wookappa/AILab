"""Train and evaluate a small churn classifier on synthetic data."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RANDOM_SEED = 42


def create_dataset(size: int = 300) -> tuple[pd.DataFrame, pd.Series]:
    random = np.random.default_rng(RANDOM_SEED)
    features = pd.DataFrame(
        {
            "tenure_months": random.integers(1, 61, size=size),
            "monthly_amount": random.normal(60, 20, size=size).clip(10, 150),
            "support_tickets": random.poisson(2, size=size),
            "country": random.choice(["IT", "FR", "ES"], size=size),
        }
    )
    risk = (
        -0.06 * features["tenure_months"]
        + 0.55 * features["support_tickets"]
        + 0.01 * features["monthly_amount"]
        + random.normal(0, 1, size=size)
    )
    labels = (risk > 0.5).astype(int)
    return features, labels


def build_pipeline() -> Pipeline:
    numeric = Pipeline(
        [
            ("impute", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("impute", SimpleImputer(strategy="most_frequent")),
            ("encode", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    preprocessing = ColumnTransformer(
        [
            ("numeric", numeric, ["tenure_months", "monthly_amount", "support_tickets"]),
            ("categorical", categorical, ["country"]),
        ]
    )
    return Pipeline(
        [
            ("preprocessing", preprocessing),
            ("model", LogisticRegression(max_iter=1_000)),
        ]
    )


def main() -> None:
    features, labels = create_dataset()
    train_x, test_x, train_y, test_y = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=RANDOM_SEED,
        stratify=labels,
    )

    baseline_value = int(train_y.mode()[0])
    baseline_predictions = np.full(len(test_y), baseline_value)

    pipeline = build_pipeline()
    pipeline.fit(train_x, train_y)
    predictions = pipeline.predict(test_x)

    print(f"Baseline accuracy: {accuracy_score(test_y, baseline_predictions):.2f}")
    print(f"Model accuracy:    {accuracy_score(test_y, predictions):.2f}")
    print(f"Model precision:   {precision_score(test_y, predictions):.2f}")
    print(f"Model recall:      {recall_score(test_y, predictions):.2f}")

    new_customer = pd.DataFrame(
        [
            {
                "tenure_months": 3,
                "monthly_amount": 89,
                "support_tickets": 5,
                "country": "IT",
            }
        ]
    )
    probability = pipeline.predict_proba(new_customer)[0, 1]
    print(f"New customer churn probability: {probability:.2f}")


if __name__ == "__main__":
    main()
