# Scientist Results

| id | score | std | delta_best | desc |
|----|-------|-----|------------|------|
| S-001 | 0.849478 | 0.001081 | +0.000000 | balanced LR lbfgs, StandardScaler+OHE |
| S-002 | 0.955047 | 0.001322 | +0.105569 | RF n=500 balanced, OHE on categoricals |
| S-003 | 0.967124 | 0.000768 | +0.012077 | LGBM n=500 lr=0.05 leaves=63 balanced, OrdinalEncoder |
| S-004 | 0.968439 | 0.001039 | +0.001315 | HistGBM max_iter=500 lr=0.05 max_leaf_nodes=63 balanced, OrdinalEncoder+categorical_features |
| S-005 | 0.969900 | 0.000806 | +0.001461 | XGBoost n=500 lr=0.05 depth=6 sample_weight balanced, OrdinalEncoder |
| S-006 | 0.968353 | 0.001164 | -0.001547 | CatBoost iter=500 lr=0.05 depth=6 auto_class_weights=Balanced, native cat |
| S-016 | 0.968737 | 0.001164 | -0.002119 | CatBoost+SM², iterations=500 lr=0.05 depth=5 subsample=0.8 balanced |
| S-017 | 0.969275 | 0.000982 | +0.000538 | LGBM+SM², n=500 lr=0.05 leaves=31 balanced, OrdinalEncoder |
| S-018 | 0.969459 | 0.001013 | +0.000184 | HistGBM+SM², max_iter=500 lr=0.05 max_leaf_nodes=31 balanced |
| S-019 | 0.961740 | 0.000788 | -0.008160 | XGB depth=5 subsample=0.8 colsample=0.8 lr=0.05 n=500 with StandardScaler+Poly2 |
