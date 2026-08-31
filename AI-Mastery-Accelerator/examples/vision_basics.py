"""Train and evaluate a small handwritten-digit image classifier."""

from __future__ import annotations

from collections import Counter

import numpy as np
from sklearn.datasets import load_digits
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_SEED = 42


def build_model() -> Pipeline:
    return Pipeline(
        [
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2_000,
                    random_state=RANDOM_SEED,
                ),
            ),
        ]
    )


def main() -> None:
    digits = load_digits()
    image_tensors = digits.images
    labels = digits.target
    images = image_tensors.reshape(len(image_tensors), -1)
    train_x, test_x, train_y, test_y = train_test_split(
        images,
        labels,
        test_size=0.25,
        random_state=RANDOM_SEED,
        stratify=labels,
    )

    most_common_label = Counter(train_y).most_common(1)[0][0]
    baseline_predictions = np.full(test_y.shape, most_common_label)

    model = build_model()
    model.fit(train_x, train_y)
    predictions = model.predict(test_x)
    matrix = confusion_matrix(test_y, predictions)
    errors = np.flatnonzero(predictions != test_y)

    image_height, image_width = image_tensors.shape[1:]
    print(f"Images: {len(image_tensors)}")
    print(f"Image shape: {image_height} x {image_width} pixels")
    print(f"Training images: {len(train_x)}")
    print(f"Test images: {len(test_x)}")
    print(f"Baseline accuracy: {accuracy_score(test_y, baseline_predictions):.3f}")
    print(f"Model accuracy:    {accuracy_score(test_y, predictions):.3f}")
    print(f"Classification errors: {len(errors)}")
    first_error = errors[0]
    print(
        "First error: "
        f"expected={test_y[first_error]}, predicted={predictions[first_error]}"
    )
    print("Confusion matrix:")
    print(matrix)


if __name__ == "__main__":
    main()
