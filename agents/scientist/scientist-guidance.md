# Scientist Guidance

## Current Lane

Current best: weighted LGBM+CatBoost ensemble (CV 0.916530). **Do not try further weighting variants of LGBM and CatBoost** — the analyst confirmed these two models have OOF Pearson r = 0.9953. They are near-redundant. Weighted averaging of near-redundant models produces noise-level gains (+0.000054 from 0.3/0.7 weighting). This is not a productive direction.

The only path to meaningful improvement is an **orthogonal third model**. Priority: ExtraTrees.

If ExtraTrees doesn't improve the ensemble, move to tuned CatBoost divergence, then consult the supervisor for next direction — do not stop experimenting.

## Success Criterion

Any new component that, when averaged with the existing LGBM+CatBoost ensemble (or replacing CatBoost), yields CV > 0.916776 (+0.0003 over current best). Solo CV doesn't need to beat LGBM — diversity is the goal.

## Harness Path Fix — Important

Always pass `--experiment-path` as an **absolute path**:

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## Priority Ideas

1. **Lighter tuned CatBoost** — the depth=9/iter=1500/rsm=0.7 variant was OOM-killed. Retry with reduced settings: `iterations=1000, learning_rate=0.03, depth=7, rsm=0.8`. This is still meaningfully different from the default CatBoost (which used ~default depth=6, ~1000 iterations) while being lighter on memory. `EXPERIMENT_NAME = "catboost_tuned_d7"`. Report solo CV and OOF correlation with LGBM baseline.

2. **Ensemble with tuned CatBoost** — if `catboost_tuned_d7` scores well (CV ≥ 0.916), try simple average of LGBM (cbef1de) + tuned CatBoost. LGBM OOF: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`. `EXPERIMENT_NAME = "ensemble_lgbm_catboost_tuned_avg"`.

3. **XGBoost baseline** — if CatBoost tuning still doesn't yield a useful diverse component, try `XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8, random_state=42)`. `EXPERIMENT_NAME = "xgb_baseline"`.

## Avoid For Now

- Further LGBM tuning (exhausted day 1)
- Target encoding on LGBM (no gain day 1)
- XGBoost (too similar to LGBM, low-priority)
- Stacking or meta-learners
- Neural networks

## Why

ExtraTrees uses bagging + random feature splits rather than gradient boosting. Its errors are correlated with LGBM/CatBoost on easy examples but differ on hard ones — exactly the diversity needed. The day-2 question is whether this structural difference translates to measurable ensemble gain on this dataset. CatBoost tuned for divergence is the backup if ExtraTrees is too weak as a solo model to contribute meaningfully.
