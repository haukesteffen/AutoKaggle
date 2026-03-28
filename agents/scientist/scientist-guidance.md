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

## Status: NEW LANES OPENED — Resume Exploration

Research on recent Kaggle Playground Series winners (S3–S6) has identified 4 untried techniques. Current best: `7b386f5` CV=0.916540, LB=0.91396. These are ordered by confidence — run them in sequence, stopping if time runs out.

### ~~Priority 1: Seed Diversity Bagging~~ — DONE, FAILED

`ensemble_seed_bag_15` (3eaeb6c): CV=0.916382 — below 0.916540. 15-model seed average is worse than equal single-seed 3-way. Discard. Pattern holds: any deviation from equal LGBM+CB+XGB hurts harness CV.

### ~~Priority 1 (now active): Original Telco Dataset Blend~~ — DONE, FAILED

`ensemble_lgbm_cb_xgb_orig` (b465548): CV=0.916341 — below 0.916540. Adding the IBM Telco original 7k rows hurt. Likely reason: synthetic training data (600k rows) has a different distribution than the 7k original; blending in the original introduces noise rather than signal. Discard.

### Priority 2 (now active): Soft Pseudo-Labeling

Train each of LGBM, CatBoost, XGBoost with **5 different random seeds** (same hyperparameters as the shortlist models). Average all 15 sets of OOF predictions and 15 sets of test predictions. Run through harness as `ensemble_seed_bag_15`.

```python
SEEDS = [42, 123, 456, 789, 1234]

# For each seed, train LGBM/CatBoost/XGBoost with that seed
# Collect 15 OOF arrays and 15 test prediction arrays
# Final OOF = mean of all 15; Final test = mean of all 15
```

Use the same preprocessor (OrdinalEncoder) and same hyperparameters as the shortlist models:
- LGBM: n_estimators=500, lr=0.05, num_leaves=31
- CatBoost: default settings (no cat_features — use OrdinalEncoder)
- XGBoost: n_estimators=500, lr=0.05, depth=6, subsample=0.8, colsample=0.8

This creates a proper `MultiSeedEnsemble` class with `fit` (trains 15 models) and `predict_proba` (averages 15 predictions). Verify training time >15 minutes. Do NOT use pre-computed OOF arrays — all models must train from scratch.

**If CV > 0.916540: keep and the supervisor will submit.**

### Priority 2: Blend Original Telecom Dataset *(~2h)*

S6E3 is based on a real public telecom churn dataset. The original is likely the **IBM Telco Customer Churn** dataset (`blastchar/telco-customer-churn` on Kaggle datasets, ~7k rows). Adding original rows to training gives a consistent boost in Playground Series competitions because synthetic generation introduces distribution artifacts.

Steps:
1. Download the original dataset: check if it exists at `/Users/hs/dev/AutoKaggle/data/` or search Kaggle datasets for `blastchar/telco-customer-churn`
2. Align column names/types to match the competition schema (same feature names and dtypes as `data/train.csv`)
3. Add `target` column encoded as 0/1
4. Concatenate with training data: `train_aug = pd.concat([train, original_data])`
5. Run `ensemble_lgbm_cb_xgb_orig` through harness using the equal-weight 3-way ensemble architecture from `7b386f5` but trained on `train_aug`
6. Compare CV to 0.916540. If better, keep.

**Important:** Use the same 5-fold structure. Original rows should be included in every training fold but excluded from validation folds (assign them `fold=-1` or include in all training splits).

### Priority 3: Soft Pseudo-Labeling *(~3h, highest ceiling, CV uninformative)*

Use the test predictions from `7b386f5` as soft labels for the test set. Retrain the 3-way ensemble on the combined dataset.

Steps:
1. Load test predictions: `test_pseudo = np.load('artifacts/mar28/experiments/7b386f5.../test-preds.npy')`
2. Load test features: `X_test` from `harness.dataset`
3. Concatenate: `X_aug = pd.concat([X_train, X_test])`, `y_aug = np.concatenate([y_train, test_pseudo])`
4. For 5-fold CV: assign all pseudo-labeled rows to `fold=-1` (training only, never validation)
5. Run as `ensemble_lgbm_cb_xgb_pseudo` using the same equal-weight architecture
6. **CV will be similar to baseline** (pseudo rows not in val) — the only true test is LB. Report CV anyway.

### Priority 4 (speculative): Two-Stage Residual Model *(~2h, low confidence)*

**Hypothesis:** The synthetic training data was generated from the IBM Telco original (~7k rows). If the synthesis process is roughly additive, we can decompose the signal into an "original signal" component and a "synthetic residual" component:

1. Train Model A on the original 7k IBM Telco rows
2. Apply Model A to the 600k synthetic training rows → compute residuals `y_train - Model_A.predict_proba(X_train)[:, 1]`
3. Train Model B on 600k synthetic rows to predict those residuals
4. Test prediction = `clip(Model_A.predict_proba(X_test)[:, 1] + Model_B.predict_proba(X_test)[:, 1], 0, 1)`

**Why this is probably wrong (supervisor notes):** We already established that adding original 7k rows *hurt* CV (0.916341 < 0.916540), implying distribution mismatch between original and synthetic data. Model A trained on 7k rows will generalize poorly to 600k out-of-distribution synthetic rows, making the "residual" mostly noise rather than learnable signal. The synthesis process is likely not additive in probability space.

**Run it anyway** to confirm. `EXPERIMENT_NAME = "ensemble_two_stage_residual"`. If CV is below 0.916540, discard immediately.

### Priority 5: Two-Feature-Set Blend *(~3h)*

Even if individual features didn't help CV, a second feature branch may *decorrelate* predictions enough to boost the blend. Train the 3-way GBDT ensemble on two feature views and average:
- Branch A: original features (same as 7b386f5)
- Branch B: add frequency encoding (`.value_counts()` per categorical column), log(tenure+1), and ratio of MonthlyCharges/TotalCharges

Compute OOF correlation between Branch A and Branch B predictions. If r < 0.97, run both through harness and average their test predictions as `ensemble_two_branch`.

**Run Branch B OOF offline first** — only proceed to harness if OOF correlation with Branch A is < 0.97.

### MultiModelEnsemble template (extend as needed)

## Avoid Entirely

- Feature engineering (target encoding, interaction features, count features — all tried, no gain)
- ExtraTrees or RandomForest in ensembles (too weak, dragged all blends below baseline)
- CatBoost tuning (OOM at depth 8+, tuned d7 more correlated with LGBM than default)
- XGBoost tuning (already in shortlist; more tuning increases LGBM correlation)
- Stacking or meta-learners

## Why

Strategist confirmed: all GBDT models are r>0.990 OOF correlation with LGBM. Feature engineering doesn't help because tree models already find those splits. The ceiling is ~CV 0.9166. Remaining upside: ensemble weight optimisation (+0.0001–0.0003), MLP probe (if orthogonal). Run these in order.
