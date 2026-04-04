import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

EXPERIMENT_NAME = "stack_s089_lr_meta_s014_s082"

ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
XGB_TASK_ID = "S-014"
LGBM_TASK_ID = "S-082"
CLASSES = np.array([0, 1, 2], dtype=int)


def _load_preds(task_id: str, filename: str) -> np.ndarray:
    return np.load(ARTIFACTS_ROOT / task_id / filename)


XGB_OOF = _load_preds(XGB_TASK_ID, "oof-preds.npy")
LGBM_OOF = _load_preds(LGBM_TASK_ID, "oof-preds.npy")
XGB_TEST = _load_preds(XGB_TASK_ID, "test-preds.npy")
LGBM_TEST = _load_preds(LGBM_TASK_ID, "test-preds.npy")


def _stack_features(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    return np.concatenate([first, second], axis=1)


OOF_FEATURES = _stack_features(XGB_OOF, LGBM_OOF)
TEST_FEATURES = _stack_features(XGB_TEST, LGBM_TEST)


def build_features(raw_X: pd.DataFrame) -> pd.DataFrame:
    return raw_X.copy()


class LogisticMetaStacker:
    def __init__(self) -> None:
        self.model_ = LogisticRegression(
            solver="lbfgs",
            C=1.0,
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )
        self._predict_test = False

    def fit(self, X: pd.DataFrame, y, **kwargs):
        row_idx = X.index.to_numpy()
        self.model_.fit(OOF_FEATURES[row_idx], np.asarray(y))
        self._predict_test = len(X) == len(OOF_FEATURES)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if self._predict_test:
            if len(X) != len(TEST_FEATURES):
                raise ValueError("unexpected test row count for S-089 stacker predictions")
            return self.model_.predict_proba(TEST_FEATURES)

        row_idx = X.index.to_numpy()
        return self.model_.predict_proba(OOF_FEATURES[row_idx])

    @property
    def classes_(self) -> np.ndarray:
        return CLASSES


def build_model(X_sample: pd.DataFrame) -> LogisticMetaStacker:
    return LogisticMetaStacker()
