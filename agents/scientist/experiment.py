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


EXPERIMENT_NAME = "lr_s049_poly4_top3_raw8_extras"

# Top-3 numeric features for degree-4 polynomial expansion
TOP3_NUMERIC_FEATURES = [
    "Soil_Moisture",
    "Temperature_C",
    "Rainfall_mm",
]

# Remaining 8 raw numeric features (no polynomial expansion)
REMAINING_NUMERIC_FEATURES = [
    "Wind_Speed_kmh",
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


class LRPoly4Top3Wrapper:
    """
    LogisticRegression with degree-4 polynomial expansion on top-3 numerics.

    Pipeline:
    1. PolynomialFeatures(degree=4, include_bias=False) on top-3 numerics
       (Soil_Moisture, Temperature_C, Rainfall_mm)
       -> 34 poly features  [C(3+4,4) - 1 = 35 - 1 = 34]
    2. Remaining 8 raw numeric features (no poly expansion)
    3. Extra features:
       - log1p(Rainfall_mm)
       - I_SM_low = (Soil_Moisture < 20).astype(float)
       Total numeric: 34 + 8 + 2 = 44 features
    4. StandardScaler on all 44 numeric features
    5. OneHotEncoder on all 8 categorical features
    6. LogisticRegression(C=10, class_weight='balanced', solver='lbfgs',
                          max_iter=2000, random_state=42)
    """

    def __init__(self):
        self.poly_top3 = PolynomialFeatures(degree=4, include_bias=False)
        self.scaler = StandardScaler()
        self.ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.model = LogisticRegression(
            C=10,
            class_weight="balanced",
            solver="lbfgs",
            max_iter=2000,
            random_state=RANDOM_STATE,
        )
        self.classes_ = None

    def _build_extra(self, X: pd.DataFrame) -> np.ndarray:
        log_rainfall = np.log1p(X["Rainfall_mm"].values).reshape(-1, 1)
        i_sm_low = (X["Soil_Moisture"].values < 20).astype(float).reshape(-1, 1)
        return np.hstack([log_rainfall, i_sm_low])

    def _transform(self, X: pd.DataFrame, fit: bool) -> np.ndarray:
        # 1. Degree-4 polynomial expansion on top-3 numerics (-> 34 features)
        X_top3_input = X[TOP3_NUMERIC_FEATURES].values
        if fit:
            X_poly_top3 = self.poly_top3.fit_transform(X_top3_input)
        else:
            X_poly_top3 = self.poly_top3.transform(X_top3_input)

        # 2. Remaining 8 raw numeric features
        X_raw_rem = X[REMAINING_NUMERIC_FEATURES].values

        # 3. Extra features: log1p(Rainfall_mm) and I_SM_low
        X_extra = self._build_extra(X)

        # 4. Concatenate all numeric features: 34 + 8 + 2 = 44
        X_all_numeric = np.hstack([X_poly_top3, X_raw_rem, X_extra])

        # 5. Scale all 44 numeric features
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


def build_model(schema: pd.DataFrame) -> LRPoly4Top3Wrapper:
    """
    Build LogisticRegression with degree-4 polynomial expansion on top-3 numerics.

    Configuration:
    - PolynomialFeatures(degree=4, include_bias=False) on top-3 numerics (-> 34 features)
    - 8 raw remaining numeric features
    - log1p(Rainfall_mm) + I_SM_low (2 more) -> 44 total numeric features
    - StandardScaler on all 44 numeric features
    - OneHotEncoder on 8 categorical features
    - LogisticRegression(C=10, class_weight='balanced', solver='lbfgs', max_iter=2000)
    """
    return LRPoly4Top3Wrapper()
