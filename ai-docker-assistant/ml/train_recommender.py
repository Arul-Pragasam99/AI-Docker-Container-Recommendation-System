"""
Phase 2 — Train the Docker image recommendation model
──────────────────────────────────────────────────────
Run:  python ml/train_recommender.py

This script:
  1. Builds a labelled training dataset (project_type, users, gpu → base_image)
  2. Trains a Scikit-learn pipeline (OneHotEncoder + RandomForestClassifier)
  3. Saves the trained pipeline to ml/recommender_model.pkl
  4. Prints a classification report

After training, set env var USE_ML_MODEL=true to activate the model in the API.
"""

import pickle
import pathlib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

# ── Training data ─────────────────────────────────────────────────────────────
# Format: [project_type, expected_users, has_gpu, base_image]
# Expand this dataset with real-world observations for better accuracy.

TRAINING_DATA = [
    # fastapi
    ["fastapi", 100,    0, "python:3.12-slim"],
    ["fastapi", 500,    0, "python:3.12-slim"],
    ["fastapi", 1000,   0, "python:3.12-slim"],
    ["fastapi", 5000,   0, "python:3.12-slim"],
    ["fastapi", 10000,  0, "python:3.12-slim"],
    ["fastapi", 50000,  0, "python:3.12-slim"],
    ["fastapi", 100000, 0, "python:3.12"],
    ["fastapi", 500000, 0, "python:3.12"],
    # django
    ["django",  100,    0, "python:3.12-slim"],
    ["django",  5000,   0, "python:3.12-slim"],
    ["django",  50000,  0, "python:3.12-slim"],
    ["django",  200000, 0, "python:3.12"],
    # flask
    ["flask",   100,    0, "python:3.12-slim"],
    ["flask",   5000,   0, "python:3.12-slim"],
    ["flask",   100000, 0, "python:3.12"],
    # node
    ["node",    100,    0, "node:20-alpine"],
    ["node",    1000,   0, "node:20-alpine"],
    ["node",    50000,  0, "node:20-alpine"],
    ["node",    200000, 0, "node:20"],
    # react
    ["react",   100,    0, "node:20-alpine"],
    ["react",   5000,   0, "node:20-alpine"],
    ["react",   100000, 0, "node:20"],
    # nextjs
    ["nextjs",  100,    0, "node:20-alpine"],
    ["nextjs",  10000,  0, "node:20-alpine"],
    ["nextjs",  100000, 0, "node:20"],
    # ml — cpu
    ["ml",      10,     0, "python:3.12-slim"],
    ["ml",      100,    0, "python:3.12-slim"],
    ["ml",      500,    0, "python:3.12"],
    # ml — gpu
    ["ml",      10,     1, "pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime"],
    ["ml",      100,    1, "pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime"],
    ["ml",      1000,   1, "pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime"],
    # postgres
    ["postgres", 100,   0, "postgres:16-alpine"],
    ["postgres", 5000,  0, "postgres:16-alpine"],
    ["postgres", 50000, 0, "postgres:16"],
    # redis
    ["redis",   100,    0, "redis:7-alpine"],
    ["redis",   10000,  0, "redis:7-alpine"],
    ["redis",   100000, 0, "redis:7"],
    # go
    ["go",      100,    0, "golang:1.22-alpine"],
    ["go",      10000,  0, "golang:1.22-alpine"],
    ["go",      200000, 0, "golang:1.22"],
    # rust
    ["rust",    100,    0, "rust:1.78-slim"],
    ["rust",    10000,  0, "rust:1.78-slim"],
    ["rust",    200000, 0, "rust:1.78"],
    # nginx
    ["nginx",   100,    0, "nginx:alpine"],
    ["nginx",   50000,  0, "nginx:alpine"],
    ["nginx",   500000, 0, "nginx:latest"],
]

# ── Feature engineering ───────────────────────────────────────────────────────

def build_features(data: list[list]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    X_text  = np.array([[row[0]] for row in data])          # project_type (categorical)
    X_num   = np.array([[row[1], row[2]] for row in data])  # users, gpu (numeric)
    y       = np.array([row[3] for row in data])
    return X_text, X_num, y


def build_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), [0]),
            ("num", StandardScaler(), [1, 2]),
        ]
    )
    # Combine categorical and numeric into a single feature matrix
    # ColumnTransformer expects a 2D array — we concatenate text + num cols
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight="balanced",
    )
    return Pipeline([("prep", preprocessor), ("clf", clf)])


# ── Train ─────────────────────────────────────────────────────────────────────

def train():
    X_text, X_num, y = build_features(TRAINING_DATA)
    # Concatenate for ColumnTransformer
    X = np.concatenate([X_text, X_num], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    # Evaluation
    y_pred = pipeline.predict(X_test)
    print("=" * 60)
    print("Recommender Model — Classification Report")
    print("=" * 60)
    print(classification_report(y_test, y_pred))

    cv_scores = cross_val_score(pipeline, X, y, cv=3, scoring="accuracy")
    print(f"3-fold CV accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    # Save
    out = pathlib.Path("ml/recommender_model.pkl")
    out.parent.mkdir(exist_ok=True)
    with open(out, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"\nModel saved to {out}")
    print("Set USE_ML_MODEL=true to activate it in the API.")


if __name__ == "__main__":
    train()
