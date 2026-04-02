import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from sklearn.preprocessing import OrdinalEncoder, StandardScaler, PolynomialFeatures

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "xgboost_scaled_polynomial_features"


class XGBoostWithPreprocessing:
    """
    Wrapper for XGBoost with StandardScaler on numeric features and PolynomialFeatures
    on key signal features, plus OrdinalEncoder for categorical features.
    """

    def __init__(self, xgb_model, scaler, poly_features, encoder, categorical_cols, numeric_cols, key_numeric_cols):
        self.xgb_model = xgb_model
        self.scaler = scaler
        self.poly_features = poly_features
        self.encoder = encoder
        self.categorical_cols = categorical_cols
        self.numeric_cols = numeric_cols
        self.key_numeric_cols = key_numeric_cols
        self.classes_ = None
        self.scaler_fitted = False
        self.poly_fitted = False
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

        # Fit and apply StandardScaler to numeric features
        if self.numeric_cols:
            if not self.scaler_fitted:
                scaled = self.scaler.fit_transform(X_proc[self.numeric_cols])
                self.scaler_fitted = True
            else:
                scaled = self.scaler.transform(X_proc[self.numeric_cols])
            for i, col in enumerate(self.numeric_cols):
                X_proc[col] = scaled[:, i]

        # Fit and apply PolynomialFeatures to key numeric columns
        if self.key_numeric_cols:
            if not self.poly_fitted:
                poly_features = self.poly_features.fit_transform(X_proc[self.key_numeric_cols])
                self.poly_fitted = True
            else:
                poly_features = self.poly_features.transform(X_proc[self.key_numeric_cols])

            # Get feature names from PolynomialFeatures
            feature_names = self.poly_features.get_feature_names_out(self.key_numeric_cols)
            # Create DataFrame with polynomial features
            poly_df = pd.DataFrame(poly_features, columns=feature_names, index=X_proc.index)
            # Drop original key numeric columns and add polynomial features
            X_proc = X_proc.drop(columns=self.key_numeric_cols)
            X_proc = pd.concat([X_proc, poly_df], axis=1)

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

        # Apply StandardScaler to numeric features
        if self.numeric_cols:
            scaled = self.scaler.transform(X_proc[self.numeric_cols])
            for i, col in enumerate(self.numeric_cols):
                X_proc[col] = scaled[:, i]

        # Apply PolynomialFeatures to key numeric columns
        if self.key_numeric_cols:
            poly_features = self.poly_features.transform(X_proc[self.key_numeric_cols])
            feature_names = self.poly_features.get_feature_names_out(self.key_numeric_cols)
            poly_df = pd.DataFrame(poly_features, columns=feature_names, index=X_proc.index)
            X_proc = X_proc.drop(columns=self.key_numeric_cols)
            X_proc = pd.concat([X_proc, poly_df], axis=1)

        # Encode categorical columns
        if self.categorical_cols:
            encoded = self.encoder.transform(X_proc[self.categorical_cols])
            for i, col in enumerate(self.categorical_cols):
                X_proc[col] = encoded[:, i]

        return X_proc


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    No feature engineering here; preprocessing is handled in the model wrapper.
    Return features as-is for the model to process.
    """
    return df.copy()


def build_model(schema: pd.DataFrame) -> XGBoostWithPreprocessing:
    """
    XGBoost with S-014 tuning configuration:
    - max_depth=5
    - subsample=0.8
    - colsample_bytree=0.8
    - learning_rate=0.05
    - n_estimators=500

    Preprocessing:
    - StandardScaler on all numeric features
    - PolynomialFeatures(degree=2, include_bias=False) on key signal features
      (Soil_Moisture, Temperature_C, Humidity)
    - OrdinalEncoder on categorical features
    """
    numeric_cols = schema.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in schema.columns if col not in numeric_cols]

    # Key signal features for polynomial expansion
    key_numeric_cols = ["Soil_Moisture", "Temperature_C", "Humidity"]

    # Filter to only those key columns that exist in the schema
    key_numeric_cols = [col for col in key_numeric_cols if col in numeric_cols]

    # Create preprocessors
    scaler = StandardScaler()
    poly_features = PolynomialFeatures(degree=2, include_bias=False)
    ordinal_encoder = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)

    # Create XGBoost model with S-014 tuning config
    xgb_model = XGBClassifier(
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        learning_rate=0.05,
        n_estimators=500,
        random_state=RANDOM_STATE,
        tree_method="hist",
        device="cpu",
        verbosity=0,
    )

    return XGBoostWithPreprocessing(
        xgb_model=xgb_model,
        scaler=scaler,
        poly_features=poly_features,
        encoder=ordinal_encoder,
        categorical_cols=categorical_cols,
        numeric_cols=numeric_cols,
        key_numeric_cols=key_numeric_cols,
    )
