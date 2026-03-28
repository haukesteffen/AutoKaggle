# Scientist Guidance

## Current Lane

We are in the bootstrap/anchor-finding phase with 3 days remaining (deadline: March 31, 2026). The first priority is establishing a solid CV baseline so all subsequent work can be ranked reliably. The current `experiment.py` is a logistic regression pipeline — run it as-is first to get the floor score, then immediately pivot to a LightGBM experiment with minimal tuning to determine whether tree models are clearly better than linear models on this churn task.

## Success Criterion

Two anchor CV scores from two different model families (logistic regression + LightGBM), recorded and comparable. After that, the best single model or a simple average of both is the target. A CV improvement of 0.002+ over the logistic regression baseline counts as meaningful progress.

## Priority Ideas

1. **Run the existing baseline as-is.** Do not change `experiment.py` yet. Get the logistic regression CV score and OOF predictions. This is the floor against which everything is measured.
2. **LightGBM baseline.** After the logistic regression run completes, swap `build_model` to a `LGBMClassifier` with default or near-default settings (e.g. `n_estimators=500, learning_rate=0.05, num_leaves=31`). Keep `build_features` returning `df.copy()` unchanged — no feature engineering yet. Change `EXPERIMENT_NAME` to something like `lgbm_baseline`.
3. **If LightGBM clearly beats LR (>0.002 CV gap):** try a second LightGBM run with modest tuning (`num_leaves=63`, `min_child_samples=20`) to see if easy gains remain.

## Avoid For Now

- Feature engineering of any kind until both model-family anchors exist
- Hyperparameter sweeps or Optuna/grid search
- Stacking or any ensemble that requires careful OOF alignment
- Neural networks or any model that takes >10 minutes per fold

## Why

The harness uses 5-fold CV (fixed seed 42) scored on ROC-AUC. The logistic regression pipeline in `experiment.py` handles all preprocessing automatically via sklearn Pipeline. LightGBM should be a drop-in replacement in `build_model` — just return an `LGBMClassifier` wrapped in a Pipeline with the same preprocessor. The goal on day one is two anchor scores, not a polished model.
