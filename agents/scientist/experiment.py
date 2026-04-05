from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression

from harness.dataset import FOLD_COLUMN, TARGET_COLUMN, encode_target_labels, load_train_with_folds


TASK_ID = "S-104"
SOURCE_IDS = ("S-014", "S-082", "S-073")
MEDIUM_ONLY_SOURCE_ID = "S-052"
CLASSES = ["High", "Low", "Medium"]
EPS = 1e-6
SHRINKAGE_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
EXPERIMENT_NAME = TASK_ID


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _artifacts_root() -> Path:
    return _repo_root() / "artifacts"


def _candidate_files(task_id: str, split: str) -> Iterable[Path]:
    patterns = (
        f"{task_id}/**/*{split}*.npy",
        f"{task_id}/**/*{split}*.parquet",
        f"{task_id}/**/*{split}*.csv",
        f"{task_id}/**/{split}.npy",
        f"{task_id}/**/{split}.parquet",
        f"{task_id}/**/{split}.csv",
    )
    root = _artifacts_root()
    seen: set[Path] = set()
    for pattern in patterns:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
                yield path


def _read_frame(path: Path) -> pd.DataFrame:
    if path.suffix == ".npy":
        arr = np.load(path)
        if arr.ndim != 2 or arr.shape[1] != len(CLASSES):
            raise ValueError(f"Unexpected array shape in {path}: {arr.shape}")
        return pd.DataFrame(arr, columns=CLASSES)
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _score_frame(df: pd.DataFrame) -> int:
    cols = {col.lower() for col in df.columns}
    score = 0
    if "id" in cols:
        score += 2
    if {"high", "low", "medium"}.issubset(cols):
        score += 5
    if "target" in cols or "label" in cols:
        score += 2
    return score


def _load_best_frame(task_id: str, split: str) -> pd.DataFrame:
    candidates = list(_candidate_files(task_id, split))
    if not candidates:
        raise FileNotFoundError(f"No {split} file found for {task_id}")
    ranked = sorted(candidates, key=lambda path: (_score_frame(_read_frame(path)), str(path)), reverse=True)
    return _read_frame(ranked[0])


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {}
    for col in df.columns:
        lower = col.lower()
        if lower in {"high", "low", "medium", "id", "target", "label"}:
            renamed[col] = lower.capitalize() if lower in {"high", "low", "medium"} else lower
    out = df.rename(columns=renamed).copy()
    prob_aliases = {
        "prob_high": "High",
        "prob_low": "Low",
        "prob_medium": "Medium",
        "high_prob": "High",
        "low_prob": "Low",
        "medium_prob": "Medium",
    }
    for src, dst in prob_aliases.items():
        if src in out.columns and dst not in out.columns:
            out = out.rename(columns={src: dst})
    return out


def _extract_probs(df: pd.DataFrame, source_id: str) -> pd.DataFrame:
    df = _normalize_columns(df)
    missing = [col for col in CLASSES if col not in df.columns]
    if missing:
        raise ValueError(f"Missing probability columns for {source_id}: {missing}")
    keep = [col for col in ("id", "target", "label") if col in df.columns]
    probs = df[keep + CLASSES].copy()
    rename = {cls: f"{source_id}_{cls}" for cls in CLASSES}
    return probs.rename(columns=rename)


def _ovr_logit_features(df: pd.DataFrame, source_id: str) -> pd.DataFrame:
    features = {}
    for cls in CLASSES:
        prob = df[f"{source_id}_{cls}"].clip(EPS, 1.0 - EPS)
        features[f"{source_id}_{cls}_ovr_logit"] = np.log(prob / (1.0 - prob))
    return pd.DataFrame(features, index=df.index)


def _prepare_split(split: str) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for source_id in SOURCE_IDS:
        df = _extract_probs(_load_best_frame(source_id, split), source_id)
        if merged is None:
            merged = df
        else:
            if "id" in merged.columns and "id" in df.columns:
                merged = merged.merge(df, on="id", how="inner")
            else:
                merged = pd.concat([merged.reset_index(drop=True), df.reset_index(drop=True)], axis=1)
    if merged is None:
        raise RuntimeError(f"Failed to prepare {split} split")
    feature_blocks = [_ovr_logit_features(merged, source_id) for source_id in SOURCE_IDS]
    medium_only = _extract_probs(_load_best_frame(MEDIUM_ONLY_SOURCE_ID, split), MEDIUM_ONLY_SOURCE_ID)
    if "id" in merged.columns and "id" in medium_only.columns:
        merged = merged.merge(medium_only, on="id", how="inner")
    else:
        merged = pd.concat([merged.reset_index(drop=True), medium_only.reset_index(drop=True)], axis=1)
    medium_prob = merged[f"{MEDIUM_ONLY_SOURCE_ID}_Medium"].clip(EPS, 1.0)
    high_prob = merged[f"{MEDIUM_ONLY_SOURCE_ID}_High"].clip(EPS, 1.0)
    low_prob = merged[f"{MEDIUM_ONLY_SOURCE_ID}_Low"].clip(EPS, 1.0)
    feature_blocks.append(_medium_feature_block(medium_prob, high_prob, low_prob, shrinkage=1.0, index=merged.index))
    features = pd.concat(feature_blocks, axis=1)
    if "id" in merged.columns:
        features.index = merged["id"].to_numpy()
    return features


def _medium_feature_block(
    medium_prob: pd.Series,
    high_prob: pd.Series,
    low_prob: pd.Series,
    shrinkage: float,
    index: pd.Index,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            f"{MEDIUM_ONLY_SOURCE_ID}_Medium_vs_High_logit": shrinkage * np.log(medium_prob / high_prob),
            f"{MEDIUM_ONLY_SOURCE_ID}_Medium_vs_Low_logit": shrinkage * np.log(medium_prob / low_prob),
        },
        index=index,
    )


OOF_FEATURES = _prepare_split("oof")
TEST_FEATURES = _prepare_split("test")
TRAIN_WITH_FOLDS = load_train_with_folds()
TRAIN_FOLDS = TRAIN_WITH_FOLDS[FOLD_COLUMN].to_numpy()
TRAIN_Y = encode_target_labels(TRAIN_WITH_FOLDS[TARGET_COLUMN])
BASE_FEATURE_COLUMNS = [col for col in OOF_FEATURES.columns if not col.startswith(f"{MEDIUM_ONLY_SOURCE_ID}_")]
MEDIUM_FEATURE_COLUMNS = [col for col in OOF_FEATURES.columns if col.startswith(f"{MEDIUM_ONLY_SOURCE_ID}_")]


def _row_keys(x: pd.DataFrame | np.ndarray) -> np.ndarray:
    if isinstance(x, pd.DataFrame):
        if "id" in x.columns:
            return x["id"].to_numpy()
        return x.index.to_numpy()
    raise TypeError("Expected pandas DataFrame input from experiment runner")


class ExternalStacker(BaseEstimator, ClassifierMixin):
    def __init__(self) -> None:
        self.model: LogisticRegression | None = None
        self.best_shrinkage_: float = 1.0
        self.classes_ = np.arange(len(CLASSES))

    def fit(self, x: pd.DataFrame, y: np.ndarray) -> "ExternalStacker":
        train_keys = _row_keys(x)
        train_x = (
            OOF_FEATURES.iloc[train_keys]
            if np.issubdtype(np.asarray(train_keys).dtype, np.integer)
            else OOF_FEATURES.loc[train_keys]
        )
        self.best_shrinkage_ = BEST_SHRINKAGE
        self.model = self._build_lr()
        self.model.fit(self._apply_shrinkage(train_x, self.best_shrinkage_), y)
        return self

    def predict_proba(self, x: pd.DataFrame) -> np.ndarray:
        keys = _row_keys(x)
        use_test = len(keys) == len(TEST_FEATURES)
        feature_bank = TEST_FEATURES if use_test else OOF_FEATURES
        if np.issubdtype(np.asarray(keys).dtype, np.integer):
            pred_x = feature_bank.iloc[keys] if not use_test else feature_bank
        else:
            pred_x = feature_bank.loc[keys]
        if self.model is None:
            raise ValueError("model must be fit before predict_proba")
        pred_x = self._apply_shrinkage(pred_x, self.best_shrinkage_)
        return self.model.predict_proba(pred_x)

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        return self.predict_proba(x).argmax(axis=1)

    def _build_lr(self) -> LogisticRegression:
        return LogisticRegression(
            C=4.0,
            class_weight="balanced",
            max_iter=2000,
            solver="lbfgs",
        )

    def _apply_shrinkage(self, features: pd.DataFrame, shrinkage: float) -> pd.DataFrame:
        out = features.copy()
        out.loc[:, BASE_FEATURE_COLUMNS] = features.loc[:, BASE_FEATURE_COLUMNS].to_numpy()
        out.loc[:, MEDIUM_FEATURE_COLUMNS] = shrinkage * features.loc[:, MEDIUM_FEATURE_COLUMNS].to_numpy()
        return out


def _balanced_accuracy_from_labels(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    per_class = []
    for cls in range(len(CLASSES)):
        mask = y_true == cls
        if mask.any():
            per_class.append(float((y_pred[mask] == cls).mean()))
    return float(np.mean(per_class))


def _select_offline_shrinkage() -> float:
    best_shrinkage = 1.0
    best_score = -np.inf
    unique_folds = np.unique(TRAIN_FOLDS)
    helper = ExternalStacker()
    for shrinkage in SHRINKAGE_GRID:
        scaled_x = helper._apply_shrinkage(OOF_FEATURES, shrinkage)
        fold_scores: list[float] = []
        for fold in unique_folds:
            train_mask = TRAIN_FOLDS != fold
            valid_mask = ~train_mask
            model = helper._build_lr()
            model.fit(scaled_x.iloc[train_mask], TRAIN_Y[train_mask])
            fold_pred = model.predict(scaled_x.iloc[valid_mask])
            fold_scores.append(_balanced_accuracy_from_labels(TRAIN_Y[valid_mask], fold_pred))
        mean_score = float(np.mean(fold_scores))
        if mean_score > best_score + 1e-12 or (
            abs(mean_score - best_score) <= 1e-12 and abs(shrinkage - 1.0) < abs(best_shrinkage - 1.0)
        ):
            best_score = mean_score
            best_shrinkage = shrinkage
    return best_shrinkage


BEST_SHRINKAGE = _select_offline_shrinkage()
EXPERIMENT_NAME = f"{TASK_ID}-shrink-{BEST_SHRINKAGE:.2f}"


def build_model(_: pd.DataFrame | None = None) -> ExternalStacker:
    return ExternalStacker()


def build_features(x: pd.DataFrame) -> pd.DataFrame:
    return x
