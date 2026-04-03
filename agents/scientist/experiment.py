import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
from itertools import combinations_with_replacement
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, TargetEncoder
from sklearn.metrics import balanced_accuracy_score
from sklearn.utils.class_weight import compute_sample_weight


EXPERIMENT_NAME = "mlp_64_32_tanh_multiseed3_targetenc_s079"

# Top-4 numerics for poly3 expansion
TOP4 = [
    "Soil_Moisture",
    "Temperature_C",
    "Rainfall_mm",
    "Wind_Speed_kmh",
]

# Remaining 7 raw numerics (passthrough as raw)
REMAINING_NUMERICS = [
    "Humidity",
    "Soil_pH",
    "Organic_Carbon",
    "Electrical_Conductivity",
    "Sunlight_Hours",
    "Field_Area_hectare",
    "Previous_Irrigation_mm",
]

# All 8 categorical features
CATEGORICAL_FEATURES = [
    "Soil_Type",
    "Crop_Type",
    "Crop_Growth_Stage",
    "Season",
    "Irrigation_Type",
    "Water_Source",
    "Mulching_Used",
    "Region",
]

SEEDS = [42, 123, 456]
N_CLASSES = 3


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build feature matrix for S-079:
    Numeric (43 total):
      - degree-3 polynomial features on top-4 (SM, Temp, Rainfall, Wind): 34 features
        (4 degree-1 + 10 degree-2 + 20 degree-3 = 34)
      - 7 raw remaining numerics
      - log1p(Rainfall_mm): 1 feature
      - I_SM_low = (Soil_Moisture < 20).astype(float): 1 feature
    Categorical (8): kept as strings for TargetEncoder
    """
    df = df.copy()

    # Build poly3 features for top-4
    top4_vals = {col: df[col].values for col in TOP4}

    poly_data = {}
    # degree-1
    for col in TOP4:
        poly_data[col] = top4_vals[col]
    # degree-2
    for i, j in combinations_with_replacement(range(4), 2):
        name = f"{TOP4[i]}_x_{TOP4[j]}"
        poly_data[name] = top4_vals[TOP4[i]] * top4_vals[TOP4[j]]
    # degree-3
    for i, j, k in combinations_with_replacement(range(4), 3):
        name = f"{TOP4[i]}_x_{TOP4[j]}_x_{TOP4[k]}"
        poly_data[name] = top4_vals[TOP4[i]] * top4_vals[TOP4[j]] * top4_vals[TOP4[k]]

    poly_df = pd.DataFrame(poly_data, index=df.index)

    # 7 raw remaining numerics
    raw_df = df[REMAINING_NUMERICS].copy()

    # log1p(Rainfall) and I_SM_low
    extra_df = pd.DataFrame(
        {
            "log1p_Rainfall_mm": np.log1p(df["Rainfall_mm"].values),
            "I_SM_low": (df["Soil_Moisture"] < 20).astype(float).values,
        },
        index=df.index,
    )

    # Categorical columns (strings kept for TargetEncoder)
    cat_df = df[CATEGORICAL_FEATURES].copy()

    result = pd.concat([poly_df, raw_df, extra_df, cat_df], axis=1)
    return result


def _get_numeric_cols(df: pd.DataFrame) -> list:
    """Return names of numeric columns (all except CATEGORICAL_FEATURES)."""
    return [c for c in df.columns if c not in CATEGORICAL_FEATURES]


def _build_pipeline(seed: int) -> Pipeline:
    """Build a single pipeline with TargetEncoder + StandardScaler + MLP for given seed."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                "passthrough",  # placeholder, will be resolved per-fold
            ),
            (
                "cat",
                TargetEncoder(cv=5, random_state=seed),
                CATEGORICAL_FEATURES,
            ),
        ],
        n_jobs=-1,
    )

    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="tanh",
        learning_rate_init=0.001,
        max_iter=500,
        random_state=seed,
        early_stopping=True,
        validation_fraction=0.1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("mlp", mlp),
        ]
    )
    return pipeline


def _build_pipeline_with_cols(seed: int, numeric_cols: list) -> Pipeline:
    """Build pipeline with explicit numeric column list."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                StandardScaler(),
                numeric_cols,
            ),
            (
                "cat",
                TargetEncoder(cv=5, random_state=seed),
                CATEGORICAL_FEATURES,
            ),
        ],
        n_jobs=-1,
    )

    mlp = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="tanh",
        learning_rate_init=0.001,
        max_iter=500,
        random_state=seed,
        early_stopping=True,
        validation_fraction=0.1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("mlp", mlp),
        ]
    )
    return pipeline


def build_model(schema: pd.DataFrame):
    """
    Build a single-seed model for artifact generation (full-data training).
    Uses seed=42, TargetEncoder(cv=5), StandardScaler, MLP(64,32) tanh.
    """
    from sklearn.base import BaseEstimator, ClassifierMixin

    numeric_cols = _get_numeric_cols(schema)

    class BalancedTargetEncoderMLP(BaseEstimator, ClassifierMixin):
        def __init__(self):
            self.pipeline = _build_pipeline_with_cols(42, numeric_cols)

        def fit(self, X, y):
            sample_weight = compute_sample_weight("balanced", y)
            self.pipeline.fit(X, y, mlp__sample_weight=sample_weight)
            self.classes_ = self.pipeline.named_steps["mlp"].classes_
            return self

        def predict_proba(self, X):
            return self.pipeline.predict_proba(X)

        def predict(self, X):
            return self.pipeline.predict(X)

    return BalancedTargetEncoderMLP()


def run_manual_cv():
    """
    Manual CV loop: for each fold, fit 3 pipelines (seeds 42, 123, 456),
    average their predict_proba, and evaluate.
    """
    from harness.dataset import (
        load_train_with_folds,
        split_xy,
        FOLD_COLUMN,
        CLASS_LABELS,
    )

    print(f"experiment: {EXPERIMENT_NAME}")
    start_time = time.perf_counter()

    train_df = load_train_with_folds()
    raw_X, y = split_xy(train_df)

    n_samples = len(train_df)
    oof_preds = np.full((n_samples, N_CLASSES), np.nan, dtype=float)
    fold_scores = []

    folds = sorted(train_df[FOLD_COLUMN].unique())

    for fold in folds:
        fold_start = time.perf_counter()
        print(f"\nFold {fold + 1}/{len(folds)}")

        train_mask = (train_df[FOLD_COLUMN] != fold).to_numpy()
        valid_mask = ~train_mask

        # Build features
        X_feat = build_features(raw_X)
        X_train = X_feat[train_mask].copy()
        X_valid = X_feat[valid_mask].copy()
        y_train = y[train_mask]
        y_valid = y[valid_mask]

        numeric_cols = _get_numeric_cols(X_train)
        sample_weight = compute_sample_weight("balanced", y_train)

        # Fit 3 pipelines and average probas
        fold_probas = []
        for seed in SEEDS:
            pipeline = _build_pipeline_with_cols(seed, numeric_cols)
            pipeline.fit(X_train, y_train, mlp__sample_weight=sample_weight)
            proba = pipeline.predict_proba(X_valid)

            # Align class probabilities to canonical order (High=0, Low=1, Medium=2)
            classes = pipeline.named_steps["mlp"].classes_
            aligned = np.zeros((len(X_valid), N_CLASSES), dtype=float)
            for src_idx, cls in enumerate(classes):
                aligned[:, int(cls)] = proba[:, src_idx]
            fold_probas.append(aligned)

            print(f"  seed={seed} done")

        # Average the 3 seed probas
        avg_proba = (fold_probas[0] + fold_probas[1] + fold_probas[2]) / 3.0

        # Store OOF predictions
        oof_preds[valid_mask] = avg_proba

        # Score fold
        pred_classes = np.argmax(avg_proba, axis=1)
        score = balanced_accuracy_score(y_valid, pred_classes)
        fold_scores.append(score)

        fold_elapsed = time.perf_counter() - fold_start
        print(f"  fold {fold + 1} balanced_accuracy: {score:.6f} ({fold_elapsed:.1f}s)")

    mean_score = float(np.mean(fold_scores))
    std_score = float(np.std(fold_scores))
    total_elapsed = time.perf_counter() - start_time

    print(f"\n--- Results ---")
    print(f"fold scores: {[f'{s:.6f}' for s in fold_scores]}")
    print(f"mean balanced_accuracy: {mean_score:.6f}")
    print(f"std balanced_accuracy:  {std_score:.6f}")
    print(f"delta_best (vs 0.970856): {mean_score - 0.970856:+.6f}")
    print(f"total elapsed: {total_elapsed:.1f}s")

    # Save OOF preds
    artifact_dir = REPO_ROOT / "artifacts" / "S-079"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    oof_path = artifact_dir / "oof-preds.npy"
    np.save(oof_path, oof_preds)
    print(f"OOF predictions saved to {oof_path}")

    return mean_score, std_score, fold_scores


if __name__ == "__main__":
    run_manual_cv()
