import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "catboost_soil_moisture_squared"


class CatBoostWrapper:
    """
    Wrapper for CatBoost with native categorical feature handling.
    CatBoost handles categorical features natively without ordinal encoding.
    """

    def __init__(self, catboost_model, categorical_cols):
        self.catboost_model = catboost_model
        self.categorical_cols = categorical_cols
        self.classes_ = None

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        self.catboost_model.fit(
            X,
            y,
            cat_features=self.categorical_cols,
            verbose=0,
        )
        self.classes_ = self.catboost_model.classes_
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.catboost_model.predict_proba(X)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Soil_Moisture squared feature (SM²).
    This captures non-linearity in soil moisture effects on irrigation need.
    """
    df = df.copy()

    # Feature: Soil_Moisture squared (captures non-linearity)
    df["Soil_Moisture_squared"] = df["Soil_Moisture"] ** 2

    return df


def build_model(schema: pd.DataFrame) -> CatBoostWrapper:
    """
    CatBoost with SM² feature and native categorical feature handling.
    S-016: Port S-014's tuning to CatBoost
    - iterations=500 (analogous to XGB's n_estimators)
    - learning_rate=0.05
    - depth=5
    - subsample=0.8 (requires bootstrap_type='Bernoulli' or 'MVS')
    - auto_class_weights='Balanced'
    - verbose=0
    Uses native cat_features list for categorical handling.
    """
    numeric_cols = schema.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in schema.columns if col not in numeric_cols]

    # CatBoost with specified parameters
    catboost_model = CatBoostClassifier(
        iterations=500,
        learning_rate=0.05,
        depth=5,
        bootstrap_type='Bernoulli',
        subsample=0.8,
        auto_class_weights='Balanced',
        random_state=RANDOM_STATE,
        verbose=0,
    )

    return CatBoostWrapper(catboost_model, categorical_cols)
