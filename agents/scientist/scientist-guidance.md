# Scientist Guidance

## Current Lane

CatBoost baseline is done (CV 0.916405, +0.00055 over LGBM). Both model components are now available. Two tasks remain: (1) build the simple average ensemble of LGBM + CatBoost, and (2) still try target encoding on LGBM — it was skipped and remains the highest-potential feature engineering move.

## Success Criterion

- Ensemble: CV clearly above 0.916405 (current CatBoost best). Even +0.001 over the better single model is a good result.
- Target encoding: CV improvement >0.001 over `cbef1de` (0.915855).

## Harness Path Fix — Important

Always pass `--experiment-path` as an **absolute path**:

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## Priority Ideas

1. **Simple average ensemble (LGBM + CatBoost)** — Load the OOF preds from both kept experiments and average them to get a combined OOF score. If it beats 0.916405, build `experiment.py` to produce this ensemble (train both models, average `predict_proba` outputs). Artifact hashes:
   - LGBM: `cbef1de9024dbd5dc70988ba46baf1633f280340` (CV 0.915855)
   - CatBoost: `81151d814205733001448397276318fcfe9f5759` (CV 0.916405)
   - OOF preds live at: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>/oof-preds.npy`
   - `EXPERIMENT_NAME = "ensemble_lgbm_catboost_avg"`

2. **Target encoding on LGBM** — Still not tried. In `build_features`, add target-encoded versions of the 13 high-variation columns (analyst-confirmed): `Contract`, `PaymentMethod`, `InternetService`, `OnlineSecurity`, `TechSupport`, `OnlineBackup`, `DeviceProtection`, `StreamingMovies`, `StreamingTV`, `PaperlessBilling`, `Dependents`, `Partner`, `MultipleLines`. Use sklearn's `TargetEncoder` with cross-fitting. `EXPERIMENT_NAME = "lgbm_target_enc"`. If this yields a better LGBM component, re-run the ensemble with the improved LGBM.

3. **Ensemble with target-encoded LGBM** — If target encoding improves LGBM, replace the LGBM component in the ensemble and re-score. `EXPERIMENT_NAME = "ensemble_lgbm_tenc_catboost_avg"`.

## Avoid For Now

- Further CatBoost tuning
- Stacking or meta-learners
- Any experiment that takes >20 minutes

## Why

With 3 days left, the highest-value moves are: lock in the best ensemble now (the two model families are available), then see if target encoding can upgrade the LGBM component. Both tasks can be done today. The supervisor will decide whether to submit based on results.
