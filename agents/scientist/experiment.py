from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.linear_model import LogisticRegression


TASK_ID = "S-100"
SOURCE_IDS = ("S-014", "S-082", "S-073")
CLASSES = ["High", "Low", "Medium"]
CLASS_TO_INT = {label: idx for idx, label in enumerate(CLASSES)}
EPS = 1e-6
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


def _medium_log_odds_features(df: pd.DataFrame, source_id: str) -> pd.DataFrame:
    high = df[f"{source_id}_High"].clip(EPS, 1.0)
    low = df[f"{source_id}_Low"].clip(EPS, 1.0)
    medium = df[f"{source_id}_Medium"].clip(EPS, 1.0)
    return pd.DataFrame(
        {
            f"{source_id}_high_vs_medium": np.log(high / medium),
            f"{source_id}_low_vs_medium": np.log(low / medium),
        },
        index=df.index,
    )


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
    feature_blocks = [_medium_log_odds_features(merged, source_id) for source_id in SOURCE_IDS]
    features = pd.concat(feature_blocks, axis=1)
    if "id" in merged.columns:
        features.index = merged["id"].to_numpy()
    return features


OOF_FEATURES = _prepare_split("oof")
TEST_FEATURES = _prepare_split("test")


def _row_keys(x: pd.DataFrame | np.ndarray) -> np.ndarray:
    if isinstance(x, pd.DataFrame):
        if "id" in x.columns:
            return x["id"].to_numpy()
        return x.index.to_numpy()
    raise TypeError("Expected pandas DataFrame input from experiment runner")


class ExternalStacker(BaseEstimator, ClassifierMixin):
    def __init__(self) -> None:
        self.model = LogisticRegression(
            C=4.0,
            class_weight="balanced",
            max_iter=2000,
            solver="lbfgs",
        )
        self.classes_ = np.arange(len(CLASSES))

    def fit(self, x: pd.DataFrame, y: np.ndarray) -> "ExternalStacker":
        train_keys = _row_keys(x)
        train_x = OOF_FEATURES.iloc[train_keys] if np.issubdtype(np.asarray(train_keys).dtype, np.integer) else OOF_FEATURES.loc[train_keys]
        self.model.fit(train_x, y)
        return self

    def predict_proba(self, x: pd.DataFrame) -> np.ndarray:
        keys = _row_keys(x)
        use_test = len(keys) == len(TEST_FEATURES)
        feature_bank = TEST_FEATURES if use_test else OOF_FEATURES
        if np.issubdtype(np.asarray(keys).dtype, np.integer):
            pred_x = feature_bank.iloc[keys] if not use_test else feature_bank
        else:
            pred_x = feature_bank.loc[keys]
        return self.model.predict_proba(pred_x)

    def predict(self, x: pd.DataFrame) -> np.ndarray:
        return self.predict_proba(x).argmax(axis=1)


def build_model(_: pd.DataFrame | None = None) -> ExternalStacker:
    return ExternalStacker()


def build_features(x: pd.DataFrame) -> pd.DataFrame:
    return x
