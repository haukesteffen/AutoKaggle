# Active Hypothesis

**Hypothesis:** Are the rows where LGBM and CatBoost disagree most (absolute OOF diff > p95, i.e. > 0.059) concentrated in a specific identifiable subgroup — e.g. short-tenure month-to-month Fiber optic customers — that a targeted interaction feature could capture?

**Decision if supported:** Direct the scientist to engineer an explicit interaction feature for that subgroup (e.g. a binary flag or binned tenure × contract type × internet service). This may help both models converge on the hard cases and improve ensemble quality even without a new model family.

**Decision if rejected:** The hard disagreement rows are spread diffusely across the feature space. No targeted feature engineering is likely to help; focus instead on model-level diversity (XGBoost or further CatBoost variants).

**Allowed evidence:** crosstabs, counts, churn rates, and median feature values for the high-disagreement rows vs the full dataset. No plots.

**Relevant experiments:** cbef1de (lgbm_baseline), 81151d8 (catboost_baseline)

OOF pred paths:
- LGBM: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/cbef1de9024dbd5dc70988ba46baf1633f280340/oof-preds.npy`
- CatBoost: `/Users/hs/dev/AutoKaggle/artifacts/mar28/experiments/81151d814205733001448397276318fcfe9f5759/oof-preds.npy`
- Train + folds: `/Users/hs/dev/AutoKaggle/data/train.csv`, `/Users/hs/dev/AutoKaggle/data/folds.csv`
