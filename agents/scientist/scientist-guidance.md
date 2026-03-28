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

**Current status (end of March 28):**
- Best result: `7b386f5` equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396
- `ensemble_cb_xgb_fixed` (3963ca3, CB=0.5/XGB=0.5): CV=0.916381 — worse (OOF-grid weights don't transfer)
- `ensemble_cb_xgb_mlp_fixed` (2c580af, CB=0.5/XGB=0.4/MLP=0.1): CV=0.916228 — worse (MLP hurts despite orthogonality; solo CV 0.911 is too low)
- **MLP ensemble lane is CLOSED.** Adding MLP to any blend reduces CV.
- March 28 slots exhausted. March 29: 5 fresh slots.

### Step 1: OOF weight grid search (LGBM + CB + XGB, finer grain, all-positive)

MLP lane is closed — do NOT include MLP in any further ensemble search.

Run a standalone Python script (not through the harness). Load OOF preds from:
- LGBM (cbef1de): `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
- CatBoost (81151d8): `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/81151d814205733001448397276318fcfe9f5759/oof-preds.npy`
- XGBoost (16c521c): `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/16c521c99ec912a96ed068b0e38c70ad28bd4801/oof-preds.npy`
- Labels: use `harness.dataset.load_train()` to get `y`

Grid-search all (w_lgbm, w_cb, w_xgb) with steps of **0.05** that sum to 1.0, **all > 0** (no zero-weight components). Compute ROC-AUC for each blend. Report the best weight combo and OOF AUC. **Do not run through harness yet.**

Note: prior coarse grid (step=0.1) found LGBM=0 as optimal but real training showed equal weights beat that. This finer search looks for any all-positive combo that beats the equal-weight OOF estimate (~0.916592).

### Step 2: Based on grid result

**If best all-positive OOF AUC > 0.916592:**
Implement `ensemble_lgbm_cb_xgb_opt` with those weights using the `MultiModelEnsemble` template (add LGBM arm alongside CB and XGB). Run through harness.

**If no all-positive combo beats 0.916592:**
Report to supervisor. `7b386f5` (equal weights, CV=0.916540, LB=0.91396) is the ceiling. The team will shift to insurance submissions only.

### MultiModelEnsemble template (extend as needed)

## Avoid Entirely

- Feature engineering (target encoding, interaction features, count features — all tried, no gain)
- ExtraTrees or RandomForest in ensembles (too weak, dragged all blends below baseline)
- CatBoost tuning (OOM at depth 8+, tuned d7 more correlated with LGBM than default)
- XGBoost tuning (already in shortlist; more tuning increases LGBM correlation)
- Stacking or meta-learners

## Why

Strategist confirmed: all GBDT models are r>0.990 OOF correlation with LGBM. Feature engineering doesn't help because tree models already find those splits. The ceiling is ~CV 0.9166. Remaining upside: ensemble weight optimisation (+0.0001–0.0003), MLP probe (if orthogonal). Run these in order.
