# Backlog

Ranked by expected impact. Supervisor updates after each wake.

| rank | idea | type | impact | status | notes |
|------|------|------|--------|--------|-------|
| 1 | GroupBy aggregations: mean/std/count of each numeric grouped by each categorical | feature_eng | high | pending | 8 cats x 11 nums x 3 stats = ~264 features; let model select |
| 2 | All pairwise categorical interactions (8C2 = 28 new columns, label-encoded) | feature_eng | high | pending | Concatenate string pairs, then ordinal-encode |
| 3 | Target encoding per categorical (smoothed, within CV folds only) | feature_eng | high | pending | Mean of encoded target per category level; use sklearn TargetEncoder |
| 4 | Frequency encoding per categorical (count and proportion of each level) | feature_eng | medium | pending | Simple value_counts mapping |
| 5 | CatBoost with iter<=300 lr=0.05 depth=5, native categoricals, SM^2 | new_model | high | pending | S-029/S-030 timed out at iter=500+; retry budget-safe |
| 6 | Retrain XGBoost (S-014 config) on expanded feature set | new_model | high | pending | Depends on feature eng results; retrain best config on best features |
| 7 | Ridge classifier on StandardScaler + OHE features | new_model | medium | pending | Linear diversity for stacking; fast to train |
| 8 | KNN (k=15-30) on StandardScaler top-10 numeric features | new_model | medium | pending | Non-parametric diversity; may need subsampling for speed |
| 9 | ExtraTrees n=500 depth=None min_leaf=2 balanced, SM^2+OHE | new_model | medium | pending | S-026 used depth=15 (0.911); unlimited depth should improve |
| 10 | Random Forest n=500 depth=None balanced, SM^2+OHE | new_model | medium | pending | S-027 used depth=20 (0.961); unlimited depth may help |
| 11 | Original dataset: find and blend real source data for S6E4 | refinement | high | pending | Standard PS technique; check competition page for source link |
| 12 | Multi-seed XGBoost: 5 seeds of S-014 config, average OOF | refinement | medium | pending | Variance reduction on best single model |
| 13 | Pseudo-labeling: use S-094 confident test preds as extra training data | refinement | medium | pending | Add high-confidence test rows to train; retrain base models |
| 14 | Diversity analysis across current portfolio | analysis | high | pending | OOF correlation matrix for S-014, S-082, S-073, S-052 |
| 15 | Error analysis on S-094 stack: where does it fail? | analysis | high | pending | Characterize worst-predicted rows by feature values |
