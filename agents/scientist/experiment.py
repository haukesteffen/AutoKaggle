import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "sgd_classifier_s033_with_a004_transformations"


class SGDClassifierWrapper:
    """
    Wrapper for SGDClassifier with preprocessing pipeline.
    Handles StandardScaler on numerics and OneHotEncoder on categoricals.
    """

    def __init__(self, model, preprocessor):
        self.model = model
        self.preprocessor = preprocessor
        self.classes_ = None

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        X_processed = self.preprocessor.fit_transform(X)
        self.model.fit(X_processed, y)
        self.classes_ = self.model.classes_
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        X_processed = self.preprocessor.transform(X)
        return self.model._predict_proba_lr(X_processed)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add A-004 recommended feature transformations:
    - SM² (Soil_Moisture squared): captures non-linear threshold at SM≈20
    - log(Rainfall_mm + 1): handles skew in wide-range rainfall data
    - I_SM_low = (Soil_Moisture < 20): binary indicator for high-need region
    """
    df = df.copy()

    # Feature 1: Soil_Moisture squared (captures non-linearity)
    df["Soil_Moisture_squared"] = df["Soil_Moisture"] ** 2

    # Feature 2: Log-scale Rainfall (handles skew)
    df["Rainfall_mm_log"] = np.log(df["Rainfall_mm"] + 1)

    # Feature 3: Binary indicator for low soil moisture (captures threshold)
    df["I_SM_low"] = (df["Soil_Moisture"] < 20).astype(int)

    return df


def build_model(schema: pd.DataFrame) -> SGDClassifierWrapper:
    """
    SGDClassifier with A-004 optimal preprocessing.

    Configuration:
    - StandardScaler on numeric features (required for SGD convergence)
    - OneHotEncoder on categorical features
    - SGDClassifier: loss='log_loss' (multiclass logistic), class_weight='balanced',
      max_iter=1000, random_state=RANDOM_STATE
    """
    numeric_cols = schema.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in schema.columns if col not in numeric_cols]

    # Create preprocessor with StandardScaler for numerics and OneHotEncoder for categoricals
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric_cols),
            ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
        ],
        remainder="passthrough",
    )

    # SGDClassifier with log_loss for multiclass logistic regression
    sgd = SGDClassifier(
        loss='log_loss',
        class_weight='balanced',
        max_iter=1000,
        random_state=RANDOM_STATE,
        n_jobs=-1,  # Use all CPU cores
    )

    return SGDClassifierWrapper(sgd, preprocessor)
