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

1. **Tuned CatBoost for divergence** — ExtraTrees (solo CV 0.911) was too weak to help the ensemble. Next: try CatBoost with `iterations=1500, learning_rate=0.03, depth=9, rsm=0.7`. The goal is to make CatBoost explore different feature interactions than the default-settings version (which is near-redundant with LGBM at r=0.9953). `EXPERIMENT_NAME = "catboost_tuned_diverge"`. Report solo CV and OOF correlation with LGBM.

2. **Ensemble with tuned CatBoost** — if tuned CatBoost scores well solo (CV ≥ 0.916), try replacing the default CatBoost component in the ensemble: simple average of LGBM (cbef1de) + tuned CatBoost. OOF artifact path for LGBM: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`. `EXPERIMENT_NAME = "ensemble_lgbm_catboost_tuned_avg"`.

3. **XGBoost baseline** — if tuned CatBoost doesn't diverge meaningfully from LGBM, try `XGBClassifier(n_estimators=500, learning_rate=0.05, max_depth=6, random_state=42)`. Low expectations for diversity but worth confirming. `EXPERIMENT_NAME = "xgb_baseline"`.

## Avoid For Now

- Further LGBM tuning (exhausted day 1)
- Target encoding on LGBM (no gain day 1)
- XGBoost (too similar to LGBM, low-priority)
- Stacking or meta-learners
- Neural networks

## Why

ExtraTrees uses bagging + random feature splits rather than gradient boosting. Its errors are correlated with LGBM/CatBoost on easy examples but differ on hard ones — exactly the diversity needed. The day-2 question is whether this structural difference translates to measurable ensemble gain on this dataset. CatBoost tuned for divergence is the backup if ExtraTrees is too weak as a solo model to contribute meaningfully.
