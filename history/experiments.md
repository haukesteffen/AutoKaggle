# Experiment Ledger

Append one compact terminal row per completed scientist batch.
Use this ledger only as a parseable summary. Put detailed per-variant logs, raw outputs, plots, and bulky evidence in `artifacts/<task_id>/`.

| task_id | finished_at | lane | metric | delta_best | status | artifact_dir | summary |
|---------|-------------|------|--------|------------|--------|-------------|---------|
| S-001 | - | - | 0.849478 | +0.000000 | scored | artifacts/S-001 | balanced LR lbfgs, StandardScaler+OHE |
| S-002 | - | - | 0.955047 | +0.105569 | scored | artifacts/S-002 | RF n=500 balanced, OHE on categoricals |
| S-003 | - | - | 0.967124 | +0.012077 | scored | artifacts/S-003 | LGBM n=500 lr=0.05 leaves=63 balanced, OrdinalEncoder |
| S-004 | - | - | 0.968439 | +0.001315 | scored | artifacts/S-004 | HistGBM max_iter=500 lr=0.05 max_leaf_nodes=63 balanced, OrdinalEncoder+categorical_features |
| S-005 | - | - | 0.969900 | +0.001461 | scored | artifacts/S-005 | XGBoost n=500 lr=0.05 depth=6 sample_weight balanced, OrdinalEncoder |
| S-006 | - | - | 0.968353 | -0.001547 | scored | artifacts/S-006 | CatBoost iter=500 lr=0.05 depth=6 auto_class_weights=Balanced, native cat |
| S-007 | - | - | 0.969646 | -0.000254 | scored | artifacts/S-007 | XGB+SM^2+interactions (4 features), depth=6, sample_weight balanced |
| S-008 | - | - | 0.969900 | +0.000000 | scored | artifacts/S-008 | XGB+SM^2 only, depth=6, sample_weight balanced |
| S-009 | - | - | 0.969860 | -0.000040 | scored | artifacts/S-009 | XGB+SM^2+I(SM<20 & Rainfall<1000), depth=6, sample_weight balanced |
| S-010 | - | - | 0.970484 | +0.000624 | scored | artifacts/S-010 | XGB+SM^2, depth=5, lr=0.05, sample_weight balanced |
| S-011 | - | - | 0.970016 | -0.000468 | scored | artifacts/S-011 | XGB+SM^2, depth=4, lr=0.05, sample_weight balanced |
| S-012 | - | - | 0.969160 | -0.001324 | scored | artifacts/S-012 | XGB+SM^2, depth=5, lr=0.03, sample_weight balanced |
| S-013 | - | - | 0.970719 | +0.000235 | scored | artifacts/S-013 | XGB+SM^2, depth=5, subsample=0.8, lr=0.05, sample_weight balanced |
| S-014 | - | - | 0.970856 | +0.000137 | scored | artifacts/S-014 | XGB+SM^2, depth=5, subsample=0.8, colsample_bytree=0.8, lr=0.05 |
| S-015 | - | - | 0.970648 | -0.000208 | scored | artifacts/S-015 | XGB+SM^2, depth=5, subsample=0.8, colsample=0.8, min_child_weight=5 |
| S-016 | - | - | 0.968737 | -0.002119 | scored | artifacts/S-016 | CatBoost+SM^2, iterations=500 lr=0.05 depth=5 subsample=0.8 balanced |
| S-017 | - | - | 0.969275 | +0.000538 | scored | artifacts/S-017 | LGBM+SM^2, n=500 lr=0.05 leaves=31 balanced, OrdinalEncoder |
| S-018 | - | - | 0.969459 | +0.000184 | scored | artifacts/S-018 | HistGBM+SM^2, max_iter=500 lr=0.05 max_leaf_nodes=31 balanced |
| S-019 | - | - | 0.961740 | -0.008160 | scored | artifacts/S-019 | XGB depth=5 subsample=0.8 colsample=0.8 lr=0.05 n=500 with StandardScaler+Poly2 |
| S-020 | - | - | 0.961446 | -0.009410 | scored | artifacts/S-020 | XGB S-014 + East region-aware features (SM^2, low rainfall) |
| S-021 | - | - | 0.961374 | -0.009482 | scored | artifacts/S-021 | XGB S-014 + crop-specific SM thresholds (Maize<18, Rice<20, Sugarcane<22) |
| S-022 | - | - | 0.961417 | -0.009439 | scored | artifacts/S-022 | XGBoost S-014 config + SM^2 + reg_lambda=0.5 |
| S-023 | - | - | 0.961265 | -0.009591 | scored | artifacts/S-023 | XGBoost S-014 config with subsample=0.6 |
| S-024 | - | - | 0.961004 | -0.009852 | scored | artifacts/S-024 | XGBoost S-014 config with n_estimators=300 |
| S-025 | - | - | 0.867516 | -0.103340 | scored | artifacts/S-025 | LogisticRegression linear diversity: StandardScaler+Poly2(SM^2,SM^2*Temp,SM^2*Humidity)+OHE |
| S-026 | - | - | 0.911483 | -0.059373 | scored | artifacts/S-026 | ExtraTreesClassifier n=500 depth=15 min_leaf=2 balanced, SM^2+OHE |
| S-027 | - | - | 0.960892 | -0.009964 | scored | artifacts/S-027 | RandomForest n=500 depth=20 min_leaf=2 balanced, SM^2+OHE |
| S-028 | - | - | 0.970123 | -0.000733 | scored | artifacts/S-028 | LGBM n=800 lr=0.03 leaves=15 subsample=0.9 balanced, SM^2+OrdinalEncoder |
| S-029 | - | - | - | - | timeout | artifacts/S-029 | CatBoost iter=800 lr=0.03 depth=5 subsample=0.9 Bernoulli balanced SM^2 timed out |
| S-030 | - | - | - | - | timeout | artifacts/S-030 | CatBoost iter=600 lr=0.04 depth=5 subsample=0.9 Bernoulli balanced SM^2 timed out |
| S-032 | - | - | 0.888151 | -0.082705 | scored | artifacts/S-032 | LR A-004 transformations: SM^2, log(Rainfall), I_SM_low, StandardScaler+OHE, balanced |
| S-033 | - | - | 0.726934 | -0.243922 | scored | artifacts/S-033 | SGDClassifier loss=log_loss A-004 features, StandardScaler+OHE, balanced |
| S-034 | - | - | 0.888128 | -0.000023 | scored | artifacts/S-034 | LR A-004 + I_SM_Rain + I_SM_Temp interactions, StandardScaler+OHE, balanced |
| S-035 | - | - | 0.892708 | +0.004557 | scored | artifacts/S-035 | LR degree-2 poly on top-4 numeric (14 features) + remaining 7 numeric, StandardScaler+OHE, balanced |
| S-036 | - | - | 0.705966 | -0.186742 | scored | artifacts/S-036 | LinearSVC C=1.0 max_iter=5000 balanced, same poly2 feature set as S-035, CalibratedClassifierCV cv=3 |
| S-037 | - | - | 0.892753 | -0.078103 | scored | artifacts/S-037 | LR C=10 degree-2 poly on top-4 numeric + remaining 7 numeric, StandardScaler+OHE, balanced |
| S-038 | - | - | 0.892644 | -0.000109 | scored | artifacts/S-038 | LR C=0.1 degree-2 poly on top-4 numeric + remaining 7 numeric, StandardScaler+OHE, balanced |
| S-039 | - | - | 0.893756 | -0.077100 | scored | artifacts/S-039 | LR C=1.0 degree-2 poly on ALL 11 numerics (77 features), StandardScaler+OHE, balanced |
| S-040 | - | - | 0.895614 | -0.075242 | scored | artifacts/S-040 | LR C=1.0 poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric features), StandardScaler+OHE, balanced |
| S-041 | - | - | - | - | timeout | artifacts/S-041 | LR L1 saga C=1.0 poly2 all 11 numerics + extras (79 numeric), StandardScaler+OHE, balanced - timed out (0/5 folds, saga too slow on this feature size) |
| S-042 | - | - | 0.794584 | -0.176272 | scored | artifacts/S-042 | RidgeClassifier alpha=1.0 balanced + CalibratedClassifierCV cv=3 sigmoid, poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric), StandardScaler+OHE |
| S-043 | - | - | 0.916437 | -0.054419 | scored | artifacts/S-043 | LR C=1.0 degree-3 poly on top-4 numerics (34 features) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total), StandardScaler+OHE, balanced |
| S-044 | - | - | 0.917093 | -0.053763 | scored | artifacts/S-044 | LR C=10 degree-3 poly on top-4 numerics (34 features) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total), StandardScaler+OHE, balanced |
| S-045 | - | - | 0.961844 | -0.009012 | scored | artifacts/S-045 | MLPClassifier (64,32) relu early_stopping poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric), StandardScaler+OHE, sample_weight balanced |
| S-046 | - | - | 0.961321 | -0.009535 | scored | artifacts/S-046 | MLPClassifier (128,64,32) relu early_stopping poly2 all 11 numerics + log1p(Rainfall) + I_SM_low (79 numeric), StandardScaler+OHE, sample_weight balanced |
| S-047 | - | - | 0.962405 | -0.008451 | scored | artifacts/S-047 | MLPClassifier (64,32) relu early_stopping degree-3 poly top-4 numerics (34 features) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric), StandardScaler+OHE, sample_weight balanced |
| S-048 | - | - | 0.917505 | +0.000412 | scored | artifacts/S-048 | LR C=10 degree-3 poly top-4 (34) + degree-2 poly rem-7 (35) + log1p(Rainfall) + I_SM_low (71 numeric total), StandardScaler+OHE, balanced |
| S-049 | - | - | 0.920901 | +0.003396 | scored | artifacts/S-049 | LR C=10 degree-4 poly top-3 (34) + 8 raw numerics + log1p(Rainfall) + I_SM_low (44 numeric total), StandardScaler+OHE, balanced; lbfgs did not converge (2000 iter) |
| S-050 | - | - | 0.920898 | -0.000003 | scored | artifacts/S-050 | LR C=10 degree-4 poly top-3 (34) + 8 raw numerics + log1p(Rainfall) + I_SM_low (44 numeric total), StandardScaler+OHE, balanced; max_iter=5000 (converged) |
| S-051 | - | - | 0.961914 | -0.008942 | scored | artifacts/S-051 | MLPClassifier (64,32) relu early_stopping degree-4 poly top-3 (34) + 8 raw + log1p(Rainfall) + I_SM_low (44 numeric), StandardScaler+OHE, sample_weight balanced |
| S-052 | - | - | 0.928573 | +0.007675 | scored | artifacts/S-052 | LR C=10 degree-4 poly top-4 (69) + 7 raw numerics + log1p(Rainfall) + I_SM_low (78 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-053 | - | - | 0.961876 | -0.000529 | scored | artifacts/S-053 | MLPClassifier (64,32) relu early_stopping degree-4 poly top-4 (69) + 7 raw + log1p(Rainfall) + I_SM_low (78 numeric), StandardScaler+OHE, sample_weight balanced |
| S-054 | - | - | 0.929671 | +0.001098 | scored | artifacts/S-054 | LR C=100 degree-4 poly top-4 (69) + 7 raw numerics + log1p(Rainfall) + I_SM_low (78 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-055 | - | - | 0.922570 | -0.007101 | scored | artifacts/S-055 | LR C=100 degree-5 poly top-3 (55) + 8 raw numerics + log1p(Rainfall) + I_SM_low (65 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-056 | - | - | 0.930248 | +0.000577 | scored | artifacts/S-056 | LR C=100 degree-4 poly top-4 (69) + degree-2 poly rem-7 (35) + log1p(Rainfall) + I_SM_low (106 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-057 | - | - | - | - | timeout | artifacts/S-057 | LR C=1000 same 106-feature set as S-056, lbfgs max_iter=5000 - timed out (4/5 folds, 1200s) |
| S-058 | - | - | 0.917223 | -0.013025 | scored | artifacts/S-058 | LR C=100 degree-3 poly top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total), StandardScaler+OHE, balanced; lbfgs max_iter=5000 |
| S-060 | - | - | 0.961110 | -0.009746 | scored | artifacts/S-060 | MLPClassifier (64,32) relu early_stopping QuantileTransformer(normal) on 11 raw numerics + OHE 8 cats, sample_weight balanced |
| S-061 | - | - | 0.961316 | -0.009540 | scored | artifacts/S-061 | MLPClassifier (64,32) relu early_stopping QuantileTransformer(normal) on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-062 | - | - | 0.962077 | -0.008779 | scored | artifacts/S-062 | MLPClassifier (64,32) relu early_stopping PowerTransformer(yeo-johnson) on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-063 | - | - | 0.961319 | -0.001086 | scored | artifacts/S-063 | MLPClassifier (256,128) relu early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-064 | - | - | 0.961562 | -0.009294 | scored | artifacts/S-064 | MLPClassifier (128,64,32,16) relu early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-065 | - | - | 0.963162 | -0.007694 | scored | artifacts/S-065 | MLPClassifier (64,32) tanh early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-066 | - | - | 0.957414 | -0.013442 | scored | artifacts/S-066 | MLPClassifier (64,32) tanh no early_stopping max_iter=2000 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-067 | - | - | 0.961183 | -0.001979 | scored | artifacts/S-067 | MLPClassifier (64,32) tanh early_stopping lr_init=0.01 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-068 | - | - | 0.962913 | -0.007943 | scored | artifacts/S-068 | MLPClassifier (64,32) tanh early_stopping lr_init=0.0001 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-069 | - | - | 0.951735 | -0.019121 | scored | artifacts/S-069 | MLPClassifier (64,32) tanh early_stopping lr_init=0.001 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, aggressive sample_weight High=30x Low=10x Medium=1x normalized |
| S-070 | - | - | 0.961741 | -0.009115 | scored | artifacts/S-070 | MLPClassifier (64,32) tanh SGD solver momentum=0.9 adaptive lr lr_init=0.001 early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-071 | - | - | 0.963759 | -0.007097 | scored | artifacts/S-071 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping TargetEncoder(cv=5) on 8 cats + StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric, 51 total after TE), sample_weight balanced |
| S-072 | - | - | 0.962762 | -0.008094 | scored | artifacts/S-072 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping OrdinalEncoder on 8 cats + StandardScaler on all 51 features (43 numeric + 8 ordinal), poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low, sample_weight balanced |
| S-073 | - | - | 0.964422 | -0.006434 | scored | artifacts/S-073 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping multi-seed ensemble (seeds 42, 123, 456 averaged per fold), StandardScaler+OHE, poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric + 8 cats), sample_weight balanced |
| S-074 | - | - | 0.960228 | -0.010628 | scored | artifacts/S-074 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping StandardScaler->PCA(0.95 var, whiten=True) on 43 numeric + OHE on 8 cats, poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low, sample_weight balanced |
| S-075 | - | - | 0.961186 | -0.009670 | scored | artifacts/S-075 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping QuantileTransformer(output_distribution='uniform') on 43 numeric + OHE on 8 cats, poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low, sample_weight balanced |
| S-076 | - | - | 0.962403 | -0.008453 | scored | artifacts/S-076 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping StandardScaler on 25 numeric (11 raw + log1p(Rainfall) + I_SM_low + SM^2 + Rainfall^2 + 10 pairwise products of top-5) + OHE on 8 cats, sample_weight balanced |
| S-077 | - | - | 0.962391 | -0.008465 | scored | artifacts/S-077 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping QuantileTransformer(normal) on 43 numeric (poly3 top-4 34 + 7 raw + log1p(Rainfall) + I_SM_low) + OrdinalEncoder on 8 cats + StandardScaler on all 51 features, sample_weight balanced |
| S-078 | - | - | 0.963187 | -0.007669 | scored | artifacts/S-078 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping validation_fraction=0.05 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-079 | - | - | 0.964960 | -0.005896 | scored | artifacts/S-079 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping multi-seed ensemble (seeds 42, 123, 456 averaged per fold) + TargetEncoder(cv=5) on 8 cats + StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric, 51 total after TE), sample_weight balanced |
| S-080 | - | - | 0.970772 | -0.000084 | scored | artifacts/S-080 | Weighted blend XGB+LR: alpha=0.95xXGB(S-014) + 0.05xLR(S-052) OOF; sweep over [0.95,0.90,0.85,0.80,0.75,0.70] - best at 0.95, all alphas below XGB-only baseline |
| S-081 | - | - | 0.970604 | -0.000252 | scored | artifacts/S-081 | LGBM n=800 lr=0.03 leaves=15 subsample=0.9 colsample_bytree=0.8 balanced, SM^2+OrdinalEncoder - colsample_bytree=0.8 did not help LGBM (vs S-028: 0.970123, delta +0.000481 over S-028 but still below S-014 best) |
| S-082 | - | - | 0.970657 | -0.000199 | scored | artifacts/S-082 | LGBM n=1500 lr=0.02 leaves=15 subsample=0.9 colsample_bytree=0.8 balanced, SM^2+OrdinalEncoder - slower learning with more trees improves slightly over S-081 (0.970604) but still below S-014 XGB best (0.970856) |
| S-083 | - | - | 0.971177 | +0.000321 | scored | artifacts/S-083 | Weighted blend XGB+LGBM: alpha=0.7xXGB(S-014) + 0.3xLGBM(S-082) OOF; sweep over [0.9,0.8,0.7,0.6,0.5,0.4,0.3] - best at alpha=0.7, positive lift over S-014 XGB-only baseline (0.970856) |
| S-084 | - | - | 0.954218 | -0.016959 | scored | artifacts/S-084 | LGBM n=2000 lr=0.02 num_leaves=7 min_child_samples=100 subsample=0.9 colsample_bytree=0.8 balanced, SM^2+OrdinalEncoder - too aggressively regularized (num_leaves=7 underfits vs 15 in S-082: 0.970657, large regression -0.016638 vs S-014) |
| S-085 | - | - | 0.970782 | -0.000395 | scored | artifacts/S-085 | XGB n=1000 lr=0.025 depth=5 subsample=0.8 colsample_bytree=0.8 balanced, SM^2+StandardScaler+OHE - slower learning with 2x trees does not improve over S-014 (0.970856); slightly below standalone XGB best |
| S-086 | - | - | 0.969934 | -0.001243 | scored | artifacts/S-086 | HistGBM max_iter=1500 lr=0.02 max_leaf_nodes=15 min_samples_leaf=50 l2_reg=0.1 class_weight=balanced, SM^2+OrdinalEncoder - tuned toward LGBM params; 0.969934 close to S-018 (0.969459) but below XGB/LGBM best; note subsample not available in sklearn HistGBM, removed; marginal improvement over S-018 (+0.000475) insufficient for 3-way blend at current best 0.971177 |
| S-087 | - | - | 0.971124 | -0.000053 | scored | artifacts/S-087 | Weighted blend XGB+LGBM+HistGBM: sweep [(0.6,0.3,0.1),(0.6,0.25,0.15),(0.5,0.35,0.15),(0.55,0.3,0.15),(0.65,0.25,0.10)] on S-014/S-082/S-086 OOF; best at (0.55,0.30,0.15), slightly below S-083 (0.971177) |
| S-088 | - | - | 0.971161 | -0.000016 | scored | artifacts/S-088 | Fine XGB+LGBM blend sweep on S-014/S-082 OOF over alpha=[0.64,0.66,0.68,0.69,0.70,0.71,0.72,0.74,0.76]; near-anchor search stayed just below S-083 |
| S-089 | - | - | 0.971927 | +0.000750 | scored | artifacts/S-089 | Multinomial LR stacker on S-014+S-082 OOF/test probs |
| S-090 | - | - | 0.971946 | +0.000019 | scored | artifacts/S-090 | Multinomial LR stacker C=4.0 on S-014+S-082 probs |
| S-091 | - | - | 0.972013 | +0.000067 | scored | artifacts/S-091 | Multinomial LR stacker C=4.0 on logit S-014+S-082 probs |
| S-092 | - | - | 0.963836 | -0.008177 | scored | artifacts/S-092 | Logit S-014+S-082 LR stacker with class_weight=None |
| S-093 | - | - | 0.972282 | +0.000269 | scored | artifacts/S-093 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073 probs |
| S-094 | - | - | 0.972299 | +0.000017 | scored | artifacts/S-094 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs |
| S-095 | - | - | 0.972253 | -0.000046 | scored | artifacts/S-095 | Multinomial LR stacker C=8.0 on logit S-014+S-082+S-073+S-052 probs |
| S-096 | - | - | 0.972243 | -0.000056 | scored | artifacts/S-096 | Multinomial LR stacker C=2.0 on logit S-014+S-082+S-073+S-052 probs |
| S-097 | - | - | 0.971843 | -0.000456 | scored | artifacts/S-097 | Multinomial LR stacker C=4.0 on raw S-014+S-082+S-073+S-052 probs |
| S-098 | - | - | 0.972097 | -0.000202 | scored | artifacts/S-098 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-052 probs |
| S-099 | - | - | 0.963954 | -0.008345 | scored | artifacts/S-099 | Multinomial LR stacker C=4.0 class_weight=None on logit S-014+S-082+S-073 probs |
| S-100 | - | - | 0.972208 | -0.000091 | scored | artifacts/S-100 | Multinomial LR stacker C=4.0 balanced on HM/LM log-odds S-014+S-082+S-073 |
| S-101 | - | - | 0.972282 | -0.000017 | scored | artifacts/S-101 | Multinomial LR C=4.0 balanced on full OVR logits S-014+S-082+S-073 |
| S-102 | - | - | 0.972297 | -0.000002 | scored | artifacts/S-102 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium OVR |
| S-103 | - | - | 0.972279 | -0.000020 | scored | artifacts/S-103 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium pairwise |
| S-104 | - | - | 0.972271 | -0.000028 | scored | artifacts/S-104 | Multinomial LR C=4.0 balanced on S-101 OVR logits + shrunk S-052 Medium pairwise |
| S-105 | - | - | 0.972308 | +0.000009 | scored | artifacts/S-105 | Multinomial LR C=4.0 balanced on S-094 OVR logits + shrunk S-052 High/Low |
