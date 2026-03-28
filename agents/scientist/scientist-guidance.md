# Scientist Guidance

## Current Lane

LGBM hyperparameter tuning has plateaued — deeper trees, more estimators, and count features all showed no gain over `cbef1de` (CV 0.915855). The analyst has now provided strong evidence for target encoding: 13/15 categorical columns show >10pp churn rate variation. This is the highest-priority next experiment. After that, run a CatBoost baseline for ensemble diversity.

## Success Criterion

Target encoding: CV improvement >0.001 over `cbef1de` (0.915855) counts as progress. CatBoost: CV within ~0.003 of LGBM best is good enough for ensemble diversity — it doesn't need to beat LGBM.

## Harness Path Fix — Important

Always pass `--experiment-path` as an **absolute path**:

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## Priority Ideas

1. **Target encoding for high-variation categoricals** — In `build_features`, add target-encoded versions of these 13 columns (analyst-confirmed >10pp variation): `Contract`, `PaymentMethod`, `InternetService`, `OnlineSecurity`, `TechSupport`, `OnlineBackup`, `DeviceProtection`, `StreamingMovies`, `StreamingTV`, `PaperlessBilling`, `Dependents`, `Partner`, `MultipleLines`. Use sklearn's `TargetEncoder` (sklearn ≥1.3) with cross-fitting to avoid leakage, or implement a simple fold-based target encoding in `build_features`. Keep the original OHE columns too — add the encoded versions as extra numeric columns alongside the existing pipeline. `EXPERIMENT_NAME = "lgbm_target_enc"`.

   **Analyst caveat:** The six internet add-on columns (OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport, StreamingTV, StreamingMovies) all share an identical "No internet service" sub-group (140,727 rows, 1.43% churn). Their target-encoded values will be highly correlated with InternetService. LightGBM will handle the redundancy, but don't be surprised if feature importance concentrates on Contract, PaymentMethod, and InternetService.

2. **CatBoost baseline** — After the target encoding result (whether it helps or not), run `CatBoostClassifier` with default settings. Pass the categorical column names via `cat_features` so CatBoost handles them natively — do **not** OHE for CatBoost. `EXPERIMENT_NAME = "catboost_baseline"`. This is for ensemble diversity.

## Avoid For Now

- Further LGBM hyperparameter search (tuning and deeper variants already exhausted)
- Stacking or meta-learners
- Any experiment that takes >20 minutes per run

## Why

Analyst data confirms massive target-rate variation in categorical features. Standard OHE treats all categories as equidistant; target encoding gives LightGBM a direct continuous signal aligned with the target. The three most powerful columns (Contract, PaymentMethod, InternetService) have 40+ pp variation — target encoding these alone may be enough to see a meaningful CV lift. After that, CatBoost is the most realistic path to ensemble diversity given the 3-day deadline.
