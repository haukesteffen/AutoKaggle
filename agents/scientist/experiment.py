import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "logreg_c10_s037_poly2_top4_features"

# Top-4 numeric features identified by A-004 linear importance analysis
POLY_FEATURES = ["Soil_Moisture", "Temperature_C", "Wind_Speed_kmh", "Rainfall_mm"]

# Remaining 7 numeric features (raw, unpolynomialised)
REMAINING_NUMERIC = [
    "Soil_pH",
    "Organic_Carbon",
    "Electrical_Conductivity",
    "Humidity",
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


class LogRegPoly2Wrapper:
    """
    LogisticRegression with degree-2 polynomial expansion on top-4 numeric features.

    Pipeline:
    1. PolynomialFeatures(degree=2, include_bias=False) on POLY_FEATURES (4 -> 14 features)
    2. Combine poly features + remaining 7 numeric features -> StandardScaler
    3. OHE for 8 categorical features
    4. LogisticRegression(C=10, class_weight='balanced', solver='lbfgs', max_iter=2000)
    """

    def __init__(self):
        self.poly = PolynomialFeatures(degree=2, include_bias=False)
        self.scaler = StandardScaler()
        self.ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.model = LogisticRegression(
            C=10,
            class_weight="balanced",
            solver="lbfgs",
            max_iter=2000,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        self.classes_ = None

    def _transform(self, X: pd.DataFrame, fit: bool) -> np.ndarray:
        # 1. Polynomial expansion on top-4 features
        X_poly_input = X[POLY_FEATURES].values
        if fit:
            X_poly = self.poly.fit_transform(X_poly_input)
        else:
            X_poly = self.poly.transform(X_poly_input)

        # 2. Remaining 7 numeric features (raw)
        X_remaining = X[REMAINING_NUMERIC].values

        # 3. Combine poly + remaining -> scale together
        X_numeric = np.hstack([X_poly, X_remaining])
        if fit:
            X_numeric = self.scaler.fit_transform(X_numeric)
        else:
            X_numeric = self.scaler.transform(X_numeric)

        # 4. Categorical OHE
        X_cat = X[CATEGORICAL_FEATURES].values
        if fit:
            X_cat = self.ohe.fit_transform(X_cat)
        else:
            X_cat = self.ohe.transform(X_cat)

        return np.hstack([X_numeric, X_cat])

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        X_processed = self._transform(X, fit=True)
        self.model.fit(X_processed, y)
        self.classes_ = self.model.classes_
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_processed = self._transform(X, fit=False)
        return self.model.predict_proba(X_processed)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Pass through -- all feature engineering happens in the wrapper."""
    return df.copy()


def build_model(schema: pd.DataFrame) -> LogRegPoly2Wrapper:
    """
    Build LogisticRegression model with degree-2 polynomial expansion on top-4 numeric features.

    Configuration:
    - PolynomialFeatures(degree=2, include_bias=False) on POLY_FEATURES (4 -> 14 features)
    - StandardScaler on poly features + remaining 7 numeric features
    - OneHotEncoder on 8 categorical features
    - LogisticRegression(C=10, class_weight='balanced', solver='lbfgs', max_iter=2000)
    """
    return LogRegPoly2Wrapper()
