# Scientist Guidance

## Current Lane

Phase: Exploitation / Shortlist Building. Feature engineering and model diversity are closed — all paths exhausted on day 1. The remaining work is ensemble composition and one MLP probe.

**Shortlist components:**
- LGBM: `cbef1de9024dbd5dc70988ba46baf1633f280340` (CV 0.915855)
- CatBoost: `81151d814205733001448397276318fcfe9f5759` (CV 0.916405)
- XGBoost: `16c521c99ec912a96ed068b0e38c70ad28bd4801` (CV 0.916421)

OOF preds at: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>/oof-preds.npy`

## Harness Path Fix — Always Required

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## ⚠️ CRITICAL BUG — AFFECTS ALL "PRECOMPUTED ENSEMBLE" EXPERIMENTS

`ensemble_lgbm_cb_xgb_avg` (393f8aa, LB=0.504) and `ensemble_3way_weighted_opt` (c4ea0d1, CV=0.916667) both have this bug:

The `PrecomputedEnsemble.predict_proba` uses `len(X) < self._n_train` to detect whether X is a CV fold (→ use OOF preds) vs test data (→ use pre-computed test preds). **This condition is wrong.** The test set has 254,655 rows < 594,194 training rows, so test data falls into the OOF branch and indexes OOF preds with test-set row indices. The test predictions are garbage.

**c4ea0d1 (CV=0.916667) has the correct OOF-grid optimal weights (CB=0.5, XGB=0.5, LGBM=0.0) but cannot be submitted without a fix.**

**Fix — implement a real fit/predict ensemble:**

```python
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from xgboost import XGBClassifier
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.preprocessing import OrdinalEncoder
import numpy as np

class MultiModelEnsemble(BaseEstimator, ClassifierMixin):
    def __init__(self, w_cb=0.5, w_xgb=0.5):
        self.w_cb = w_cb
        self.w_xgb = w_xgb
        self.cb_ = None
        self.xgb_ = None
        self.enc_ = None

    def fit(self, X, y):
        cat_cols = X.select_dtypes(include="object").columns.tolist()
        self.enc_ = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
        X_enc = X.copy()
        X_enc[cat_cols] = self.enc_.fit_transform(X[cat_cols])
        self.cb_ = CatBoostClassifier(iterations=1000, depth=7, random_state=42, verbose=0)
        self.cb_.fit(X_enc, y)
        self.xgb_ = XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6,
                                   subsample=0.8, colsample_bytree=0.8, random_state=42,
                                   eval_metric="auc", verbosity=0)
        self.xgb_.fit(X_enc, y)
        self.cat_cols_ = cat_cols
        return self

    def predict_proba(self, X):
        X_enc = X.copy()
        X_enc[self.cat_cols_] = self.enc_.transform(X[self.cat_cols_])
        cb_p = self.cb_.predict_proba(X_enc)[:, 1]
        xgb_p = self.xgb_.predict_proba(X_enc)[:, 1]
        preds = self.w_cb * cb_p + self.w_xgb * xgb_p
        return np.column_stack([1 - preds, preds])
```

`EXPERIMENT_NAME = "ensemble_cb_xgb_fixed"`. Training time should be 8–15 minutes — confirm this before recording results.

## Priority Ideas

**Current status (March 29 — consolidation phase):**
- Best result: `7b386f5` equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396 — **this is the ceiling**
- OOF weight grid (step=0.05, all-positive) completed by supervisor: best was LGBM=0.05/CB=0.50/XGB=0.45 → OOF 0.916657 vs equal-weight OOF 0.916580. Delta +0.000077 is too small to trust given OOF-grid unreliability (past experience: OOF overestimates by ~0.0002–0.0003 vs harness). **Do NOT implement.**
- All lanes exhausted: feature engineering, GBDT tuning, weight optimization, MLP ensemble, CB+XGB only.

## Status: Exploration Complete

**Your work is done.** All lanes have been exhausted. The supervisor has confirmed the ceiling is `7b386f5` (CV=0.916540, LB=0.91396). No further experiments are needed or expected.

The supervisor will handle all remaining insurance submissions directly from `7b386f5`'s artifacts.

**You may rest until explicitly asked for a new experiment.** If a genuinely novel idea occurs to you (a model family never tried, a structural change not yet explored), write it as a hypothesis in scientist-results.md and the supervisor will evaluate it. Otherwise, no action required.

### MultiModelEnsemble template (extend as needed)

## Avoid Entirely

- Feature engineering (target encoding, interaction features, count features — all tried, no gain)
- ExtraTrees or RandomForest in ensembles (too weak, dragged all blends below baseline)
- CatBoost tuning (OOM at depth 8+, tuned d7 more correlated with LGBM than default)
- XGBoost tuning (already in shortlist; more tuning increases LGBM correlation)
- Stacking or meta-learners

## Why

Strategist confirmed: all GBDT models are r>0.990 OOF correlation with LGBM. Feature engineering doesn't help because tree models already find those splits. The ceiling is ~CV 0.9166. Remaining upside: ensemble weight optimisation (+0.0001–0.0003), MLP probe (if orthogonal). Run these in order.
