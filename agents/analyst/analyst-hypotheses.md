# Active Hypothesis

**Hypothesis:** Do the categorical features in the training dataset have enough target-rate variation across their values to make target encoding a likely improvement over one-hot encoding for LightGBM — specifically, are there categorical columns where the churn rate varies by more than 10 percentage points across levels?

**Decision if supported:** Direct the scientist to add target-encoded versions of those high-variation categorical features to `build_features` in the next LightGBM experiment.

**Decision if rejected:** Skip feature engineering entirely and go straight to CatBoost baseline for ensemble diversity.

**Allowed evidence:** tables, counts, metrics, and concise text only. No plots.

**Relevant experiments:** cbef1de (lgbm_baseline, CV 0.915855)
