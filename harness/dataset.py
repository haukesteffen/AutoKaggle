import csv
import time
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold


DATA_DIR = Path("data")
TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
FOLDS_PATH = DATA_DIR / "folds.csv"
COMPETITION = "playground-series-s6e3"
ID_COLUMN = "id"
TARGET_COLUMN = "Churn"
POSITIVE_LABEL = "Yes"
NEGATIVE_LABEL = "No"
FOLD_ROW_INDEX_COLUMN = "row_idx"
FOLD_COLUMN = "fold"
N_SPLITS = 5
RANDOM_STATE = 42
TIME_BUDGET_SECONDS = 20 * 60


FeatureBuilder = Callable[[pd.DataFrame], pd.DataFrame]
ModelBuilder = Callable[[pd.DataFrame], Any]
ProgressCallback = Callable[[int], None]


@dataclass(frozen=True)
class EvaluationResult:
    fold_scores: list[float]
    mean_score: float | None
    std_score: float | None
    completed_folds: int
    training_seconds: float
    timed_out: bool


def main():
    DATA_DIR.mkdir(exist_ok=True)

    if not TRAIN_PATH.exists() or not TEST_PATH.exists():
        zip_path = DATA_DIR / f"{COMPETITION}.zip"
        subprocess.run(
            [
                "uv",
                "run",
                "kaggle",
                "competitions",
                "download",
                "-c",
                COMPETITION,
                "-p",
                str(DATA_DIR),
                "--force",
            ],
            check=True,
        )
        with ZipFile(zip_path) as zf:
            zf.extractall(DATA_DIR)
        zip_path.unlink()

    with TRAIN_PATH.open(newline="") as f:
        train_rows = list(csv.DictReader(f))
    folds = [-1] * len(train_rows)

    splitter = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    for fold, (_, valid_idx) in enumerate(splitter.split(train_rows)):
        for i in valid_idx:
            folds[i] = fold

    with FOLDS_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([FOLD_ROW_INDEX_COLUMN, FOLD_COLUMN])
        for i, fold in enumerate(folds):
            writer.writerow([i, fold])


def load_train_with_folds() -> pd.DataFrame:
    train_df = pd.read_csv(TRAIN_PATH)
    folds_df = pd.read_csv(FOLDS_PATH).sort_values(FOLD_ROW_INDEX_COLUMN).reset_index(drop=True)

    expected_indices = pd.Series(np.arange(len(train_df)), name=FOLD_ROW_INDEX_COLUMN)
    if len(folds_df) != len(train_df) or not folds_df[FOLD_ROW_INDEX_COLUMN].equals(expected_indices):
        raise ValueError("fold assignments do not align with the training rows")

    train_df[FOLD_COLUMN] = folds_df[FOLD_COLUMN].to_numpy()
    return train_df


def split_xy(train_df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    y = train_df[TARGET_COLUMN].map({NEGATIVE_LABEL: 0, POSITIVE_LABEL: 1})
    if y.isna().any():
        raise ValueError("training labels contain unexpected values")
    X = train_df.drop(columns=[ID_COLUMN, TARGET_COLUMN, FOLD_COLUMN])
    return X, y.to_numpy()


def score_fold(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(roc_auc_score(y_true, y_pred))


def evaluate_model(
    model_builder: ModelBuilder,
    feature_builder: FeatureBuilder,
    deadline: float,
    on_fold_complete: ProgressCallback | None = None,
) -> EvaluationResult:
    train_df = load_train_with_folds()
    raw_X, y = split_xy(train_df)

    fold_scores: list[float] = []
    training_start = time.perf_counter()

    for fold in sorted(train_df[FOLD_COLUMN].unique()):
        if time.monotonic() >= deadline:
            return _timeout_result(fold_scores, training_start)

        train_mask = train_df[FOLD_COLUMN] != fold
        valid_mask = ~train_mask

        X_train = _build_feature_frame(feature_builder, raw_X.loc[train_mask].copy(), "train")
        X_valid = _build_feature_frame(feature_builder, raw_X.loc[valid_mask].copy(), "valid")
        _validate_feature_columns(X_train, X_valid)

        model = model_builder(X_train.head(0).copy())
        model.fit(X_train, y[train_mask.to_numpy()])
        if time.monotonic() >= deadline:
            return _timeout_result(fold_scores, training_start)

        valid_pred = _predict_positive_scores(model, X_valid)
        if time.monotonic() >= deadline:
            return _timeout_result(fold_scores, training_start)

        fold_scores.append(score_fold(y[valid_mask.to_numpy()], valid_pred))
        if on_fold_complete is not None:
            on_fold_complete(len(fold_scores))

    training_seconds = time.perf_counter() - training_start
    return EvaluationResult(
        fold_scores=fold_scores,
        mean_score=float(np.mean(fold_scores)),
        std_score=float(np.std(fold_scores)),
        completed_folds=len(fold_scores),
        training_seconds=training_seconds,
        timed_out=False,
    )


def _build_feature_frame(feature_builder: FeatureBuilder, df: pd.DataFrame, split_name: str) -> pd.DataFrame:
    feature_df = feature_builder(df)
    if not isinstance(feature_df, pd.DataFrame):
        raise TypeError(f"build_features must return a pandas DataFrame for the {split_name} split")
    if len(feature_df) != len(df):
        raise ValueError(f"build_features changed the row count for the {split_name} split")
    return feature_df


def _validate_feature_columns(X_train: pd.DataFrame, X_valid: pd.DataFrame) -> None:
    if X_train.columns.tolist() != X_valid.columns.tolist():
        raise ValueError("build_features must return the same columns for train and valid splits")


def _predict_positive_scores(model: Any, X_valid: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        pred = np.asarray(model.predict_proba(X_valid))
        if pred.ndim != 2 or pred.shape[1] < 2:
            raise ValueError("predict_proba must return a 2D array with at least two columns")
        return pred[:, 1]

    if hasattr(model, "decision_function"):
        pred = np.asarray(model.decision_function(X_valid))
        if pred.ndim == 1:
            return pred
        if pred.ndim == 2 and pred.shape[1] >= 2:
            return pred[:, 1]
        raise ValueError("decision_function must return a 1D array or a 2D array with at least two columns")

    raise TypeError("build_model must return an estimator with predict_proba or decision_function")


def _timeout_result(fold_scores: list[float], training_start: float) -> EvaluationResult:
    return EvaluationResult(
        fold_scores=fold_scores,
        mean_score=None,
        std_score=None,
        completed_folds=len(fold_scores),
        training_seconds=time.perf_counter() - training_start,
        timed_out=True,
    )


if __name__ == "__main__":
    main()
