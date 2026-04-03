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
| S-032 | 0.888151 | 0.000811 | -0.082705 | LR A-004 transformations: SM², log(Rainfall), I_SM_low, StandardScaler+OHE, balanced |
| S-033 | 0.726934 | 0.010742 | -0.243922 | SGDClassifier loss=log_loss A-004 features, StandardScaler+OHE, balanced |
| S-034 | 0.888128 | 0.000894 | -0.000023 | LR A-004 + I_SM_Rain + I_SM_Temp interactions, StandardScaler+OHE, balanced |
| S-035 | 0.892708 | 0.001235 | +0.004557 | LR degree-2 poly on top-4 numeric (14 features) + remaining 7 numeric, StandardScaler+OHE, balanced |
| S-036 | 0.705966 | 0.001609 | -0.186742 | LinearSVC C=1.0 max_iter=5000 balanced, same poly2 feature set as S-035, CalibratedClassifierCV cv=3 |
| S-037 | 0.892753 | 0.001233 | -0.078103 | LR C=10 degree-2 poly on top-4 numeric + remaining 7 numeric, StandardScaler+OHE, balanced |
| S-038 | 0.892644 | 0.001177 | -0.000109 | LR C=0.1 degree-2 poly on top-4 numeric + remaining 7 numeric, StandardScaler+OHE, balanced |
| S-039 | 0.893756 | 0.001323 | -0.077100 | LR C=1.0 degree-2 poly on ALL 11 numerics (77 features), StandardScaler+OHE, balanced |
| S-040 | 0.895614 | 0.001295 | -0.075242 | LR C=1.0 poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric features), StandardScaler+OHE, balanced |
| S-041 | - | - | - | LR L1 saga C=1.0 poly2 all 11 numerics + extras (79 numeric), StandardScaler+OHE, balanced — timed out (0/5 folds, saga too slow on this feature size) |
| S-042 | 0.794584 | 0.001687 | -0.176272 | RidgeClassifier alpha=1.0 balanced + CalibratedClassifierCV cv=3 sigmoid, poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric), StandardScaler+OHE |
| S-043 | 0.916437 | 0.000948 | -0.054419 | LR C=1.0 degree-3 poly on top-4 numerics (34 features) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total), StandardScaler+OHE, balanced |
| S-044 | 0.917093 | 0.000709 | -0.053763 | LR C=10 degree-3 poly on top-4 numerics (34 features) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total), StandardScaler+OHE, balanced |
| S-045 | 0.961844 | 0.001195 | -0.009012 | MLPClassifier (64,32) relu early_stopping poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric), StandardScaler+OHE, sample_weight balanced |
| S-046 | 0.961321 | 0.001368 | -0.009535 | MLPClassifier (128,64,32) relu early_stopping poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric), StandardScaler+OHE, sample_weight balanced |
| S-047 | 0.962405 | 0.001095 | -0.008451 | MLPClassifier (64,32) relu early_stopping degree-3 poly top-4 numerics (34 features) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric), StandardScaler+OHE, sample_weight balanced |
| S-048 | 0.917505 | 0.001109 | +0.000412 | LR C=10 degree-3 poly top-4 (34) + degree-2 poly rem-7 (35) + log1p(Rainfall) + I_SM_low (71 numeric total), StandardScaler+OHE, balanced |
| S-049 | 0.920901 | 0.001293 | +0.003396 | LR C=10 degree-4 poly top-3 (34) + 8 raw numerics + log1p(Rainfall) + I_SM_low (44 numeric total), StandardScaler+OHE, balanced; lbfgs did not converge (2000 iter) |
| S-050 | 0.920898 | 0.001290 | -0.000003 | LR C=10 degree-4 poly top-3 (34) + 8 raw numerics + log1p(Rainfall) + I_SM_low (44 numeric total), StandardScaler+OHE, balanced; max_iter=5000 (converged) |
| S-051 | 0.961914 | 0.001108 | -0.008942 | MLPClassifier (64,32) relu early_stopping degree-4 poly top-3 (34) + 8 raw + log1p(Rainfall) + I_SM_low (44 numeric), StandardScaler+OHE, sample_weight balanced |
| S-052 | 0.928573 | 0.001062 | +0.007675 | LR C=10 degree-4 poly top-4 (69) + 7 raw numerics + log1p(Rainfall) + I_SM_low (78 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-053 | 0.961876 | 0.001435 | -0.000529 | MLPClassifier (64,32) relu early_stopping degree-4 poly top-4 (69) + 7 raw + log1p(Rainfall) + I_SM_low (78 numeric), StandardScaler+OHE, sample_weight balanced |
| S-054 | 0.929671 | 0.001159 | +0.001098 | LR C=100 degree-4 poly top-4 (69) + 7 raw numerics + log1p(Rainfall) + I_SM_low (78 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-055 | 0.922570 | 0.000942 | -0.007101 | LR C=100 degree-5 poly top-3 (55) + 8 raw numerics + log1p(Rainfall) + I_SM_low (65 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-056 | 0.930248 | 0.001574 | +0.000577 | LR C=100 degree-4 poly top-4 (69) + degree-2 poly rem-7 (35) + log1p(Rainfall) + I_SM_low (106 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-057 | - | - | - | LR C=1000 same 106-feature set as S-056, lbfgs max_iter=5000 — timed out (4/5 folds, 1200s) |
| S-058 | 0.917223 | 0.000877 | -0.013025 | LR C=100 degree-3 poly top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
