import csv
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedKFold


DATA_DIR = Path("data")
TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
SAMPLE_SUBMISSION_PATH = DATA_DIR / "sample_submission.csv"
FOLDS_PATH = DATA_DIR / "folds.csv"
COMPETITION = "playground-series-s6e4"
TASK_TYPE = "multiclass_classification"
METRIC_NAME = "balanced_accuracy"
ID_COLUMN = "id"
TARGET_COLUMN = "Irrigation_Need"
FEATURE_COLUMNS = (
    "Soil_Type",
    "Soil_pH",
    "Soil_Moisture",
    "Organic_Carbon",
    "Electrical_Conductivity",
    "Temperature_C",
    "Humidity",
    "Rainfall_mm",
    "Sunlight_Hours",
    "Wind_Speed_kmh",
    "Crop_Type",
    "Crop_Growth_Stage",
    "Season",
    "Irrigation_Type",
    "Water_Source",
    "Field_Area_hectare",
    "Mulching_Used",
    "Previous_Irrigation_mm",
    "Region",
)
CLASS_LABELS = ("High", "Low", "Medium")
CLASS_TO_INDEX = {label: index for index, label in enumerate(CLASS_LABELS)}
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


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    _ensure_competition_files()

    train_columns = pd.read_csv(TRAIN_PATH, nrows=0).columns.tolist()
    test_columns = pd.read_csv(TEST_PATH, nrows=0).columns.tolist()
    sample_submission_df = pd.read_csv(SAMPLE_SUBMISSION_PATH, nrows=10)
    _validate_dataset_schema(train_columns, test_columns, sample_submission_df)

    train_targets = pd.read_csv(TRAIN_PATH, usecols=[TARGET_COLUMN])[TARGET_COLUMN]
    y = encode_target_labels(train_targets)
    folds = np.full(len(y), -1, dtype=int)

    splitter = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    for fold, (_, valid_idx) in enumerate(splitter.split(np.zeros((len(y), 1)), y)):
        folds[valid_idx] = fold

    with FOLDS_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([FOLD_ROW_INDEX_COLUMN, FOLD_COLUMN])
        for i, fold in enumerate(folds):
            writer.writerow([i, int(fold)])


def load_train_with_folds() -> pd.DataFrame:
    train_df = pd.read_csv(TRAIN_PATH)
    _validate_train_dataframe(train_df)
    folds_df = pd.read_csv(FOLDS_PATH).sort_values(FOLD_ROW_INDEX_COLUMN).reset_index(drop=True)

    expected_indices = pd.Series(np.arange(len(train_df)), name=FOLD_ROW_INDEX_COLUMN)
    if len(folds_df) != len(train_df) or not folds_df[FOLD_ROW_INDEX_COLUMN].equals(expected_indices):
        raise ValueError("fold assignments do not align with the training rows")

    train_df[FOLD_COLUMN] = folds_df[FOLD_COLUMN].to_numpy()
    return train_df


def split_xy(train_df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    y = encode_target_labels(train_df[TARGET_COLUMN])
    X = train_df.drop(columns=[ID_COLUMN, TARGET_COLUMN, FOLD_COLUMN])
    return X, y


def score_fold(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(balanced_accuracy_score(y_true, class_probabilities_to_indices(y_pred)))


def evaluate_model(
    model_builder: ModelBuilder,
    feature_builder: FeatureBuilder,
    deadline: float,
    on_fold_complete: ProgressCallback | None = None,
) -> tuple[EvaluationResult, np.ndarray]:
    train_df = load_train_with_folds()
    raw_X, y = split_xy(train_df)

    fold_scores: list[float] = []
    oof_preds = np.full((len(train_df), len(CLASS_LABELS)), np.nan, dtype=float)
    training_start = time.perf_counter()

    for fold in sorted(train_df[FOLD_COLUMN].unique()):
        if time.monotonic() >= deadline:
            return _timeout_result(fold_scores, training_start, oof_preds)

        train_mask = train_df[FOLD_COLUMN] != fold
        valid_mask = ~train_mask

        X_train = _build_feature_frame(feature_builder, raw_X.loc[train_mask].copy(), "train")
        X_valid = _build_feature_frame(feature_builder, raw_X.loc[valid_mask].copy(), "valid")
        _validate_feature_columns(X_train, X_valid)

        model = model_builder(X_train.head(0).copy())
        model.fit(X_train, y[train_mask.to_numpy()])
        if time.monotonic() >= deadline:
            return _timeout_result(fold_scores, training_start, oof_preds)

        valid_pred = predict_class_probabilities(model, X_valid)
        oof_preds[valid_mask.to_numpy(), :] = valid_pred
        if time.monotonic() >= deadline:
            return _timeout_result(fold_scores, training_start, oof_preds)

        fold_scores.append(score_fold(y[valid_mask.to_numpy()], valid_pred))
        if on_fold_complete is not None:
            on_fold_complete(len(fold_scores))

    training_seconds = time.perf_counter() - training_start
    if np.isnan(oof_preds).any():
        raise ValueError("missing out-of-fold predictions after successful evaluation")
    return (
        EvaluationResult(
            fold_scores=fold_scores,
            mean_score=float(np.mean(fold_scores)),
            std_score=float(np.std(fold_scores)),
            completed_folds=len(fold_scores),
            training_seconds=training_seconds,
            timed_out=False,
        ),
        oof_preds,
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


def encode_target_labels(labels: pd.Series | list[str] | np.ndarray) -> np.ndarray:
    label_series = pd.Series(labels)
    encoded = label_series.map(CLASS_TO_INDEX)
    if encoded.isna().any():
        unexpected = sorted(label_series[encoded.isna()].astype(str).unique().tolist())
        raise ValueError(f"training labels contain unexpected values: {unexpected}")
    return encoded.to_numpy(dtype=int)


def decode_target_labels(indices: np.ndarray | list[int]) -> np.ndarray:
    decoded_indices = np.asarray(indices)
    if decoded_indices.ndim != 1:
        raise ValueError("predicted class indices must be a 1D array")
    if np.any((decoded_indices < 0) | (decoded_indices >= len(CLASS_LABELS))):
        raise ValueError("predicted class indices are out of range")
    return np.asarray(CLASS_LABELS, dtype=object)[decoded_indices]


def class_probabilities_to_indices(pred: np.ndarray) -> np.ndarray:
    pred_array = np.asarray(pred, dtype=float)
    _validate_probability_matrix(pred_array, "prediction")
    return np.argmax(pred_array, axis=1).astype(int)


def predict_class_probabilities(model: Any, X_valid: pd.DataFrame) -> np.ndarray:
    if not hasattr(model, "predict_proba"):
        raise TypeError("build_model must return an estimator with predict_proba")

    pred = np.asarray(model.predict_proba(X_valid), dtype=float)
    if pred.ndim != 2:
        raise ValueError("predict_proba must return a 2D array")
    if pred.shape[0] != len(X_valid):
        raise ValueError("predict_proba returned an unexpected row count")

    model_classes = getattr(model, "classes_", None)
    if model_classes is None:
        raise ValueError("predict_proba estimators must expose classes_ after fit")
    return _align_class_probabilities(pred, model_classes)


def _timeout_result(
    fold_scores: list[float], training_start: float, oof_preds: np.ndarray
) -> tuple[EvaluationResult, np.ndarray]:
    return (
        EvaluationResult(
            fold_scores=fold_scores,
            mean_score=None,
            std_score=None,
            completed_folds=len(fold_scores),
            training_seconds=time.perf_counter() - training_start,
            timed_out=True,
        ),
        oof_preds,
    )


def _ensure_competition_files() -> None:
    if TRAIN_PATH.exists() and TEST_PATH.exists() and SAMPLE_SUBMISSION_PATH.exists():
        return

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
    zip_path.unlink(missing_ok=True)


def _validate_dataset_schema(
    train_columns: list[str], test_columns: list[str], sample_submission_df: pd.DataFrame
) -> None:
    expected_train_columns = [ID_COLUMN, *FEATURE_COLUMNS, TARGET_COLUMN]
    expected_test_columns = [ID_COLUMN, *FEATURE_COLUMNS]
    expected_submission_columns = [ID_COLUMN, TARGET_COLUMN]

    if train_columns != expected_train_columns:
        raise ValueError("train.csv does not match the expected S6E4 irrigation schema")
    if test_columns != expected_test_columns:
        raise ValueError("test.csv does not match the expected S6E4 irrigation schema")
    if sample_submission_df.columns.tolist() != expected_submission_columns:
        raise ValueError("sample_submission.csv does not match the expected S6E4 irrigation schema")
    if not sample_submission_df.empty and not set(sample_submission_df[TARGET_COLUMN]).issubset(CLASS_TO_INDEX):
        raise ValueError("sample_submission.csv contains unexpected irrigation labels")


def _validate_train_dataframe(train_df: pd.DataFrame) -> None:
    expected_train_columns = [ID_COLUMN, *FEATURE_COLUMNS, TARGET_COLUMN]
    if train_df.columns.tolist() != expected_train_columns:
        raise ValueError("train.csv does not match the expected S6E4 irrigation schema")


def _align_class_probabilities(pred: np.ndarray, model_classes: Any) -> np.ndarray:
    model_classes_array = np.asarray(model_classes)
    if pred.shape[1] != len(model_classes_array):
        raise ValueError("predict_proba column count does not match model classes_")

    aligned = np.zeros((pred.shape[0], len(CLASS_LABELS)), dtype=float)
    seen_targets: set[int] = set()

    for source_index, class_value in enumerate(model_classes_array.tolist()):
        try:
            target_index = int(class_value)
        except (TypeError, ValueError) as exc:
            raise ValueError("model classes_ must contain encoded integer class labels") from exc
        if target_index < 0 or target_index >= len(CLASS_LABELS):
            raise ValueError("model classes_ contain out-of-range class labels")
        if target_index in seen_targets:
            raise ValueError("model classes_ contain duplicate class labels")
        aligned[:, target_index] = pred[:, source_index]
        seen_targets.add(target_index)

    if len(seen_targets) != len(CLASS_LABELS):
        raise ValueError("predict_proba must return one column for each irrigation class")
    _validate_probability_matrix(aligned, "predict_proba")
    return aligned


def _validate_probability_matrix(pred: np.ndarray, source_name: str) -> None:
    if pred.ndim != 2:
        raise ValueError(f"{source_name} must be a 2D probability matrix")
    if pred.shape[1] != len(CLASS_LABELS):
        raise ValueError(f"{source_name} must return exactly {len(CLASS_LABELS)} class columns")


if __name__ == "__main__":
    main()
