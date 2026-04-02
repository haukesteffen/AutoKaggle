import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import OrdinalEncoder

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "histgradientboosting_s031_aggressive_tuning_with_sm2"


class HistGBMWrapper:
    """
    Wrapper for HistGradientBoosting with OrdinalEncoder on categoricals.
    Passes categorical feature indices to the model for native handling.
    """

    def __init__(self, model, encoder, categorical_indices):
        self.model = model
        self.encoder = encoder
        self.categorical_indices = categorical_indices
        self.classes_ = None
        self.encoder_fitted = False

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        X_processed = self._process_features_for_fit(X)
        self.model.fit(X_processed, y)
        self.classes_ = self.model.classes_
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_processed = self._process_features(X)
        return self.model.predict_proba(X_processed)

    def _process_features_for_fit(self, X: pd.DataFrame) -> pd.DataFrame:
        X_proc = X.copy()

        # Fit and apply OrdinalEncoder to categorical columns
        if self.categorical_indices:
            categorical_cols = [X.columns[i] for i in self.categorical_indices if i < len(X.columns)]
            if categorical_cols:
                if not self.encoder_fitted:
                    encoded = self.encoder.fit_transform(X_proc[categorical_cols])
                    self.encoder_fitted = True
                else:
                    encoded = self.encoder.transform(X_proc[categorical_cols])
                for i, col in enumerate(categorical_cols):
                    X_proc[col] = encoded[:, i]

        return X_proc

    def _process_features(self, X: pd.DataFrame) -> pd.DataFrame:
        X_proc = X.copy()

        # Apply OrdinalEncoder to categorical columns
        if self.categorical_indices:
            categorical_cols = [X.columns[i] for i in self.categorical_indices if i < len(X.columns)]
            if categorical_cols:
                encoded = self.encoder.transform(X_proc[categorical_cols])
                for i, col in enumerate(categorical_cols):
                    X_proc[col] = encoded[:, i]

        return X_proc


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Soil_Moisture squared feature (SM²).
    This captures non-linearity in soil moisture effects on irrigation need.
    """
    df = df.copy()

    # Feature: Soil_Moisture squared (captures non-linearity)
    df["Soil_Moisture_squared"] = df["Soil_Moisture"] ** 2

    return df


def build_model(schema: pd.DataFrame) -> HistGBMWrapper:
    """
    HistGradientBoosting with aggressive tuning and SM² feature.
    S-031: More iterations, slower learning, more regularization.
    - max_iter=800 (more boosting)
    - learning_rate=0.03 (slower, refined)
    - max_leaf_nodes=31 (regularized)
    - class_weight='balanced'
    - categorical_features passed to model
    Uses OrdinalEncoder for categorical feature handling.
    """
    numeric_cols = schema.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in schema.columns if col not in numeric_cols]

    # Get indices of categorical columns for the model
    categorical_indices = [schema.columns.get_loc(col) for col in categorical_cols]

    # Create OrdinalEncoder for categorical features
    ordinal_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)

    # HistGradientBoosting with aggressive tuning
    hist_gbm = HistGradientBoostingClassifier(
        max_iter=800,
        learning_rate=0.03,
        max_leaf_nodes=31,
        class_weight='balanced',
        random_state=RANDOM_STATE,
        categorical_features=categorical_indices if categorical_indices else None,
    )

    return HistGBMWrapper(hist_gbm, ordinal_encoder, categorical_indices)
