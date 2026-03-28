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

**Current status:** MLP experiment (442ff2a) is running now. Wait for it to finish.

1. **After MLP finishes — report CV score and OOF correlation check.** The supervisor will post an analyst hypothesis for MLP OOF correlation vs LGBM. Do NOT implement a new experiment until the analyst clears it.

2. **Implement `ensemble_cb_xgb_fixed`** — Use the `MultiModelEnsemble` class above (CB=0.5, XGB=0.5). This is the corrected version of c4ea0d1 (CV=0.916667, best OOF grid result). Verify training time >8 minutes. This is the most important submission candidate.

3. **If MLP passes orthogonality (analyst confirms r < 0.990 with LGBM)** — add MLP as a 3rd component: `ensemble_cb_xgb_mlp`. Weights TBD from OOF grid over CB/XGB/MLP preds. Implement as a proper `MultiModelEnsemble` extension.

4. **LR as small-weight ensemble component** — The LR OOF preds already exist from experiment `4bc520f`. Try averaging CB + XGB + LR with LR weight 0.05–0.10. Compute OOF CV offline first; only run through harness if it improves above 0.916667.

## Avoid Entirely

- Feature engineering (target encoding, interaction features, count features — all tried, no gain)
- ExtraTrees or RandomForest in ensembles (too weak, dragged all blends below baseline)
- CatBoost tuning (OOM at depth 8+, tuned d7 more correlated with LGBM than default)
- XGBoost tuning (already in shortlist; more tuning increases LGBM correlation)
- Stacking or meta-learners

## Why

Strategist confirmed: all GBDT models are r>0.990 OOF correlation with LGBM. Feature engineering doesn't help because tree models already find those splits. The ceiling is ~CV 0.9166. Remaining upside: ensemble weight optimisation (+0.0001–0.0003), MLP probe (if orthogonal). Run these in order.
