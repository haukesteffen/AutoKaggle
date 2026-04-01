import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "catboost_native_categorical_balanced"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


class CatBoostWrapper:
    """
    Wraps CatBoostClassifier with native categorical feature support.
    Stores categorical column indices from the schema and passes them
    as cat_features to fit(). No encoding or imputation needed.
    """

    def __init__(self, cat_feature_indices: list[int], **cb_kwargs):
        self.cat_feature_indices = cat_feature_indices
        self.model_ = CatBoostClassifier(**cb_kwargs)

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        self.model_.fit(X, y, cat_features=self.cat_feature_indices)
        self.classes_ = self.model_.classes_
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model_.predict_proba(X)


def build_model(schema: pd.DataFrame) -> CatBoostWrapper:
    numeric_cols = schema.select_dtypes(include=["number"]).columns.tolist()
    all_cols = schema.columns.tolist()
    cat_feature_indices = [
        all_cols.index(col)
        for col in all_cols
        if col not in numeric_cols
    ]

    return CatBoostWrapper(
        cat_feature_indices=cat_feature_indices,
        iterations=500,
        learning_rate=0.05,
        depth=6,
        random_seed=RANDOM_STATE,
        auto_class_weights="Balanced",
        verbose=0,
    )
