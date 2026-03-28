# Scientist Guidance

## Current Lane

Tree models are clearly dominant: LightGBM baseline scored CV 0.915855 vs LR 0.907919 (+0.008 gap). LB confirms this (0.91326 vs 0.90504). Focus entirely on LightGBM refinement now, then one CatBoost diversity run. Do not revisit LR.

## Success Criterion

CV improvement of >0.001 over `cbef1de` (0.915855) counts as progress. Target: push CV above 0.917 via modest tuning, then build a CatBoost component for ensembling.

## Harness Path Fix — Important

Always pass `--experiment-path` as an **absolute path** from the worktree:

```bash
uv run python -m harness.experiment_runner \
  --experiment-path /Users/hs/dev/AutoKaggle-mar28-scientist/agents/scientist/experiment.py \
  --artifact-dir /Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/<hash>
```

## Priority Ideas

1. **LightGBM modest tuning** — set `num_leaves=63`, `min_child_samples=20`, keep other defaults. EXPERIMENT_NAME = `lgbm_num_leaves_63`. If this beats cbef1de by >0.001, keep it as the new best.
2. **LightGBM with more estimators** — if num_leaves tuning is marginal, try `n_estimators=1000, learning_rate=0.03, num_leaves=63`. EXPERIMENT_NAME = `lgbm_deeper`.
3. **CatBoost baseline** — after the best LightGBM variant is found, run a `CatBoostClassifier` with default settings (pass categorical column names via `cat_features`). EXPERIMENT_NAME = `catboost_baseline`. This is for ensemble diversity, not necessarily a score improvement.

## Avoid For Now

- Feature engineering (analyst is assessing whether target encoding would help)
- Stacking or OOF-based meta-learners
- XGBoost (redundant with LightGBM for now given the deadline)
- Hyperparameter sweeps beyond the two LightGBM variants above

## Why

With 3 days remaining and CV tracking LB well (gap ~0.003), the highest-value work is: (a) squeeze the best single LightGBM variant, (b) get one CatBoost component for a simple-average ensemble. The submission budget is tight — only run these experiments and report results clearly.
