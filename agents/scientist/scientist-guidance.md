# Scientist Guidance

## Current Lane

Current best: weighted LGBM+CatBoost ensemble (CV 0.916530).

**STATUS:** Analyst has confirmed all CatBoost variants (default r=0.9953, tuned d7 r=0.9972) and likely XGBoost are all near-redundant with LGBM. Model diversity from same-family tuning is exhausted. **The next experiment must be `lgbm_mtm_fiber_bins` — the interaction feature.** This has been priority #1 for several wakes and has not yet been run.

Do not run any more model variants or ensembles until the interaction feature result is in.

## Success Criterion

CV improvement >0.001 over `cbef1de` (0.915855) for a new LGBM with interaction features, or any ensemble CV > 0.916530 when a new component is added.

## Harness Path Fix — Important

Always pass `--experiment-path` as an **absolute path**:

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## ⚠️ NEXT EXPERIMENT: lgbm_mtm_fiber_bins — DO NOT RUN ANYTHING ELSE FIRST

All model diversity paths have been exhausted (ExtraTrees cv=0.911, RandomForest cv=0.910, XGBoost cv=0.916 but near-redundant with LGBM per analyst, tuned CatBoost r=0.9972 with LGBM). The ONLY remaining lever is feature engineering. Run `lgbm_mtm_fiber_bins` next.

## Priority Ideas

1. **Three mtm_fiber tenure flags** — Analyst confirmed a clear churn threshold pattern within Month-to-month × Fiber optic. Add these three binary features to `build_features` for LGBM:
   - `mtm_fiber_early`: 1 if `Contract == "Month-to-month"` AND `InternetService == "Fiber optic"` AND `tenure <= 12` (70.8% churn)
   - `mtm_fiber_mid`: 1 if same AND `13 <= tenure <= 24` (42.3% churn)
   - `mtm_fiber_late`: 1 if same AND `tenure > 24` (~35% churn)
   The 12-month split has a 28.6pp churn gap — the single most informative cut in this subgroup. Keep all original features unchanged. `EXPERIMENT_NAME = "lgbm_mtm_fiber_bins"`.

2. **Tuned CatBoost — strict budget** — If interaction feature doesn't help, try CatBoost with exactly `iterations=1000, learning_rate=0.03, depth=7, rsm=0.8`. **Do not use iterations=1500** — depth=8/iter=1500 already timed out. `EXPERIMENT_NAME = "catboost_tuned_d7_i1000"`. If this also times out, skip CatBoost tuning.

3. **XGBoost baseline** — If CatBoost tuning fails, try `XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8, random_state=42)`. `EXPERIMENT_NAME = "xgb_baseline"`.

## Avoid For Now

- Further LGBM hyperparameter tuning (exhausted)
- Target encoding on LGBM (tried, no gain)
- Weighted blending of LGBM + CatBoost only (near-redundant)
- Stacking or meta-learners
- Neural networks

## Why

Analyst confirmed the hardest 5% of rows are heavily concentrated in Month-to-month × Fiber optic, with short-tenure customers (7–12 months) at 1.71x lift. Both LGBM and CatBoost predict ~44% churn here vs 22.5% overall — genuine ambiguity both models struggle with. A cheap binary flag + tenure bins may give the model a cleaner split on this subgroup without expensive tuning.
