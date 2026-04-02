import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import OrdinalEncoder

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "xgboost_s014_n_estimators_300"


class SimpleXGBoostWrapper:
    """
    Wrapper for XGBoost with OrdinalEncoder for categorical features.
    Features are engineered in build_features(); no scaling applied here.
    """

    def __init__(self, xgb_model, encoder, categorical_cols):
        self.xgb_model = xgb_model
        self.encoder = encoder
        self.categorical_cols = categorical_cols
        self.classes_ = None
        self.encoder_fitted = False

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        X_processed = self._process_features_for_fit(X)
        self.xgb_model.fit(X_processed, y)
        self.classes_ = self.xgb_model.classes_
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_processed = self._process_features(X)
        return self.xgb_model.predict_proba(X_processed)

    def _process_features_for_fit(self, X: pd.DataFrame) -> pd.DataFrame:
        X_proc = X.copy()

        # Encode categorical columns
        if self.categorical_cols:
            if not self.encoder_fitted:
                self.encoder.fit(X_proc[self.categorical_cols])
                self.encoder_fitted = True
            encoded = self.encoder.transform(X_proc[self.categorical_cols])
            for i, col in enumerate(self.categorical_cols):
                X_proc[col] = encoded[:, i]

        return X_proc

    def _process_features(self, X: pd.DataFrame) -> pd.DataFrame:
        X_proc = X.copy()

        # Encode categorical columns
        if self.categorical_cols:
            encoded = self.encoder.transform(X_proc[self.categorical_cols])
            for i, col in enumerate(self.categorical_cols):
                X_proc[col] = encoded[:, i]

        return X_proc


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build features including:
    - Soil_Moisture squared (SM²) from S-014
    """
    X = df.copy()

    # Add Soil_Moisture squared (SM²) - same as S-014
    # This captures the non-linear threshold behavior in soil moisture
    X['Soil_Moisture_squared'] = X['Soil_Moisture'] ** 2

    return X


def build_model(schema: pd.DataFrame) -> SimpleXGBoostWrapper:
    """
    XGBoost with S-014 tuning configuration but fewer trees (n_estimators=300):
    - max_depth=5
    - subsample=0.8 (from S-014)
    - colsample_bytree=0.8
    - learning_rate=0.05
    - n_estimators=300 (shallower ensemble vs S-014's 500)
    - reg_lambda=1.0 (XGBoost default)

    Features:
    - Soil_Moisture² (SM²) from S-014
    - OrdinalEncoder on categorical features
    """
    numeric_cols = schema.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in schema.columns if col not in numeric_cols]

    # Create ordinal encoder for categorical features
    ordinal_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)

    # Create XGBoost model with S-014 tuning config but n_estimators=300
    xgb_model = XGBClassifier(
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        learning_rate=0.05,
        n_estimators=300,
        random_state=RANDOM_STATE,
        tree_method="hist",
        device="cpu",
        verbosity=0,
    )

    return SimpleXGBoostWrapper(
        xgb_model=xgb_model,
        encoder=ordinal_encoder,
        categorical_cols=categorical_cols,
    )
