# Scientist Results

| id | score | std | delta_best | desc |
|----|-------|-----|------------|------|
| S-001 | 0.849478 | 0.001081 | +0.000000 | balanced LR lbfgs, StandardScaler+OHE |
| S-002 | 0.955047 | 0.001322 | +0.105569 | RF n=500 balanced, OHE on categoricals |
| S-003 | 0.967124 | 0.000768 | +0.012077 | LGBM n=500 lr=0.05 leaves=63 balanced, OrdinalEncoder |
| S-004 | 0.968439 | 0.001039 | +0.001315 | HistGBM max_iter=500 lr=0.05 max_leaf_nodes=63 balanced, OrdinalEncoder+categorical_features |
| S-005 | 0.969900 | 0.000806 | +0.001461 | XGBoost n=500 lr=0.05 depth=6 sample_weight balanced, OrdinalEncoder |
| S-006 | 0.968353 | 0.001164 | -0.001547 | CatBoost iter=500 lr=0.05 depth=6 auto_class_weights=Balanced, native cat |
| S-007 | 0.969646 | 0.000871 | -0.000254 | XGB+SM²+interactions (4 features), depth=6, sample_weight balanced |
| S-008 | 0.969900 | 0.000806 | +0.000000 | XGB+SM² only, depth=6, sample_weight balanced |
| S-009 | 0.969860 | 0.000768 | -0.000040 | XGB+SM²+I(SM<20 & Rainfall<1000), depth=6, sample_weight balanced |
| S-010 | 0.970484 | 0.000710 | +0.000624 | XGB+SM², depth=5, lr=0.05, sample_weight balanced |
| S-011 | 0.970016 | 0.000736 | -0.000468 | XGB+SM², depth=4, lr=0.05, sample_weight balanced |
| S-012 | 0.969160 | 0.000992 | -0.001324 | XGB+SM², depth=5, lr=0.03, sample_weight balanced |
| S-013 | 0.970719 | 0.000787 | +0.000235 | XGB+SM², depth=5, subsample=0.8, lr=0.05, sample_weight balanced |
| S-014 | 0.970856 | 0.000645 | +0.000137 | XGB+SM², depth=5, subsample=0.8, colsample_bytree=0.8, lr=0.05 |
| S-015 | 0.970648 | 0.000769 | -0.000208 | XGB+SM², depth=5, subsample=0.8, colsample=0.8, min_child_weight=5 |
| S-016 | 0.968737 | 0.001164 | -0.002119 | CatBoost+SM², iterations=500 lr=0.05 depth=5 subsample=0.8 balanced |
| S-017 | 0.969275 | 0.000982 | +0.000538 | LGBM+SM², n=500 lr=0.05 leaves=31 balanced, OrdinalEncoder |
| S-018 | 0.969459 | 0.001013 | +0.000184 | HistGBM+SM², max_iter=500 lr=0.05 max_leaf_nodes=31 balanced |
| S-019 | 0.961740 | 0.000788 | -0.008160 | XGB depth=5 subsample=0.8 colsample=0.8 lr=0.05 n=500 with StandardScaler+Poly2 |
| S-020 | 0.961446 | 0.000677 | -0.009410 | XGB S-014 + East region-aware features (SM², low rainfall) |
| S-021 | 0.961374 | 0.000722 | -0.009482 | XGB S-014 + crop-specific SM thresholds (Maize<18, Rice<20, Sugarcane<22) |
| S-022 | 0.961417 | 0.000863 | -0.009439 | XGBoost S-014 config + SM² + reg_lambda=0.5 |
| S-023 | 0.961265 | 0.000865 | -0.009591 | XGBoost S-014 config with subsample=0.6 |
| S-024 | 0.961004 | 0.000815 | -0.009852 | XGBoost S-014 config with n_estimators=300 |
| S-025 | 0.867516 | 0.001247 | -0.103340 | LogisticRegression linear diversity: StandardScaler+Poly2(SM²,SM²*Temp,SM²*Humidity)+OHE |
| S-026 | 0.911483 | 0.000673 | -0.059373 | ExtraTreesClassifier n=500 depth=15 min_leaf=2 balanced, SM²+OHE |
| S-027 | 0.960892 | 0.000530 | -0.009964 | RandomForest n=500 depth=20 min_leaf=2 balanced, SM²+OHE |
| S-028 | 0.970123 | 0.001049 | -0.000733 | LGBM n=800 lr=0.03 leaves=15 subsample=0.9 balanced, SM²+OrdinalEncoder |
| S-029 | - | - | - | CatBoost iter=800 lr=0.03 depth=5 subsample=0.9 Bernoulli balanced SM² timed out |
| S-030 | - | - | - | CatBoost iter=600 lr=0.04 depth=5 subsample=0.9 Bernoulli balanced SM² timed out |
