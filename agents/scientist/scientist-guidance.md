# Scientist Guidance

## Current Lane

Current best: weighted LGBM+CatBoost ensemble (CV 0.916530). **Do not try further weighting variants of LGBM and CatBoost** — the analyst confirmed these two models have OOF Pearson r = 0.9953. They are near-redundant. Weighted averaging of near-redundant models produces noise-level gains (+0.000054 from 0.3/0.7 weighting). This is not a productive direction.

The only path to meaningful improvement is an **orthogonal third model**. Priority: ExtraTrees.

**Hard gate:** If ExtraTrees (or tuned CatBoost) doesn't add >=0.0003 CV to the best available ensemble above 0.916530, lock the current best as the final submission candidate.

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

1. **ExtraTrees baseline** — `build_model` returns an `ExtraTreesClassifier(n_estimators=500, max_features="sqrt", min_samples_leaf=5, random_state=42)` in a Pipeline with the same preprocessor as the LGBM baseline. `EXPERIMENT_NAME = "extratrees_baseline"`. Report solo CV and whether it would improve the 3-way ensemble (LGBM + CatBoost + ExtraTrees simple average).

2. **3-component ensemble (LGBM + CatBoost + ExtraTrees)** — if ExtraTrees solo CV is anywhere near 0.910+, try a simple average of all three OOF preds and report the combined CV. OOF artifact paths:
   - LGBM: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
   - CatBoost: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/81151d814205733001448397276318fcfe9f5759/oof-preds.npy`
   - `EXPERIMENT_NAME = "ensemble_lgbm_catboost_extratrees_avg"`

3. **Tuned CatBoost for divergence** — if ExtraTrees doesn't help, try CatBoost with `iterations=1500, learning_rate=0.03, depth=9, rsm=0.7`. This forces CatBoost to explore different feature interactions than LGBM. `EXPERIMENT_NAME = "catboost_tuned_diverge"`. Only pursue if ExtraTrees path is exhausted or clearly fails.

## Avoid For Now

- Further LGBM tuning (exhausted day 1)
- Target encoding on LGBM (no gain day 1)
- XGBoost (too similar to LGBM, low-priority)
- Stacking or meta-learners
- Neural networks

## Why

ExtraTrees uses bagging + random feature splits rather than gradient boosting. Its errors are correlated with LGBM/CatBoost on easy examples but differ on hard ones — exactly the diversity needed. The day-2 question is whether this structural difference translates to measurable ensemble gain on this dataset. CatBoost tuned for divergence is the backup if ExtraTrees is too weak as a solo model to contribute meaningfully.
