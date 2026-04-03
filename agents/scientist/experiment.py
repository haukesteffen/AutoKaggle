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


EXPERIMENT_NAME = "lr_c100_poly5_top4_s059"

# Top-4 numeric features for degree-5 polynomial expansion
# With 4 features and degree=5: C(4+5, 5) - 1 = 126 - 1 = 125 poly features (no bias)
TOP4_NUMERIC_FEATURES = [
    "Soil_Moisture",
    "Temperature_C",
    "Rainfall_mm",
    "Wind_Speed_kmh",
]

# Remaining 7 numeric features (used as raw)
REM7_NUMERIC_FEATURES = [
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


class LRPoly5Top4C100Wrapper:
    """
    LogisticRegression with degree-5 polynomial expansion on top-4 numerics,
    remaining 7 raw numerics, plus log1p(Rainfall_mm) and I_SM_low.

    Pipeline:
    1. PolynomialFeatures(degree=5, include_bias=False) on top-4 numerics
       (Soil_Moisture, Temperature_C, Rainfall_mm, Wind_Speed_kmh)
       -> 125 poly features (C(4+5,5) - 1 = 126 - 1 = 125)
    2. Remaining 7 raw numerics (no poly expansion)
    3. Extra features:
       - log1p(Rainfall_mm)
       - I_SM_low = (Soil_Moisture < 20).astype(float)
       Total numeric: 125 + 7 + 2 = 134 features
    4. StandardScaler on all 134 numeric features
    5. OneHotEncoder on all 8 categorical features
    6. LogisticRegression(C=100, class_weight='balanced', solver='lbfgs',
                          max_iter=5000, random_state=42)
    """

    def __init__(self):
        self.poly_top4 = PolynomialFeatures(degree=5, include_bias=False)
        self.scaler = StandardScaler()
        self.ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.model = LogisticRegression(
            C=100,
            class_weight="balanced",
            solver="lbfgs",
            max_iter=5000,
            random_state=RANDOM_STATE,
        )
        self.classes_ = None

    def _build_extra(self, X: pd.DataFrame) -> np.ndarray:
        log_rainfall = np.log1p(X["Rainfall_mm"].values).reshape(-1, 1)
        i_sm_low = (X["Soil_Moisture"].values < 20).astype(float).reshape(-1, 1)
        return np.hstack([log_rainfall, i_sm_low])

    def _transform(self, X: pd.DataFrame, fit: bool) -> np.ndarray:
        # 1. Degree-5 polynomial expansion on top-4 numerics (-> 125 features)
        X_top4_input = X[TOP4_NUMERIC_FEATURES].values
        if fit:
            X_poly_top4 = self.poly_top4.fit_transform(X_top4_input)
        else:
            X_poly_top4 = self.poly_top4.transform(X_top4_input)

        # 2. Remaining 7 raw numerics
        X_rem7 = X[REM7_NUMERIC_FEATURES].values

        # 3. Extra features: log1p(Rainfall_mm) and I_SM_low
        X_extra = self._build_extra(X)

        # 4. Concatenate all numeric features: 125 + 7 + 2 = 134
        X_all_numeric = np.hstack([X_poly_top4, X_rem7, X_extra])

        # 5. Scale all 134 numeric features
        if fit:
            X_numeric = self.scaler.fit_transform(X_all_numeric)
        else:
            X_numeric = self.scaler.transform(X_all_numeric)

        # 6. Categorical OHE
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


def build_model(schema: pd.DataFrame) -> LRPoly5Top4C100Wrapper:
    """
    Build LogisticRegression with degree-5 poly on top-4 numerics,
    7 raw remaining numerics, log1p(Rainfall_mm), and I_SM_low.

    Configuration:
    - PolynomialFeatures(degree=5, include_bias=False) on top-4 numerics (-> 125 features)
    - 7 raw remaining numerics (-> 7 features)
    - log1p(Rainfall_mm) + I_SM_low (2 more) -> 134 total numeric features
    - StandardScaler on all 134 numeric features
    - OneHotEncoder on 8 categorical features
    - LogisticRegression(C=100, class_weight='balanced', solver='lbfgs',
                         max_iter=5000, random_state=42)
    """
    return LRPoly5Top4C100Wrapper()
