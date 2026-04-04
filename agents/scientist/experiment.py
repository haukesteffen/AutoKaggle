import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score

EXPERIMENT_NAME = "blend_s088_xgb_lgbm_fine_sweep"

ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
XGB_TASK_ID = "S-014"
LGBM_TASK_ID = "S-082"
XGB_ALPHAS = np.array([0.64, 0.66, 0.68, 0.69, 0.70, 0.71, 0.72, 0.74, 0.76], dtype=float)
CLASSES = np.array([0, 1, 2], dtype=int)


def _load_preds(task_id: str, filename: str) -> np.ndarray:
    return np.load(ARTIFACTS_ROOT / task_id / filename)


XGB_OOF = _load_preds(XGB_TASK_ID, "oof-preds.npy")
LGBM_OOF = _load_preds(LGBM_TASK_ID, "oof-preds.npy")
XGB_TEST = _load_preds(XGB_TASK_ID, "test-preds.npy")
LGBM_TEST = _load_preds(LGBM_TASK_ID, "test-preds.npy")


def build_features(raw_X: pd.DataFrame) -> pd.DataFrame:
    return raw_X.copy()


class FineSweepBlendModel:
    def __init__(self) -> None:
        self.alpha_ = float(XGB_ALPHAS[0])
        self._predict_test = False

    def _blend(self, alpha: float, xgb_preds: np.ndarray, lgbm_preds: np.ndarray) -> np.ndarray:
        return alpha * xgb_preds + (1.0 - alpha) * lgbm_preds

    def fit(self, X: pd.DataFrame, y, **kwargs):
        row_idx = X.index.to_numpy()
        y_array = np.asarray(y)

        best_alpha = None
        best_score = -np.inf
        for alpha in XGB_ALPHAS:
            blend = self._blend(alpha, XGB_OOF[row_idx], LGBM_OOF[row_idx])
            score = balanced_accuracy_score(y_array, blend.argmax(axis=1))
            if score > best_score:
                best_score = score
                best_alpha = float(alpha)

        self.alpha_ = best_alpha if best_alpha is not None else float(XGB_ALPHAS[0])
        self._predict_test = len(X) == len(XGB_OOF)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        row_idx = X.index.to_numpy()
        if self._predict_test:
            if len(X) != len(XGB_TEST):
                raise ValueError("unexpected test row count for S-088 blend predictions")
            return self._blend(self.alpha_, XGB_TEST, LGBM_TEST)

        return self._blend(self.alpha_, XGB_OOF[row_idx], LGBM_OOF[row_idx])

    @property
    def classes_(self) -> np.ndarray:
        return CLASSES


def build_model(X_sample: pd.DataFrame) -> FineSweepBlendModel:
    return FineSweepBlendModel()
