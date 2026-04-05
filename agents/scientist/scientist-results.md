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
| S-060 | 0.961110 | 0.000736 | -0.009746 | MLPClassifier (64,32) relu early_stopping QuantileTransformer(normal) on 11 raw numerics + OHE 8 cats, sample_weight balanced |
| S-061 | 0.961316 | 0.001450 | -0.009540 | MLPClassifier (64,32) relu early_stopping QuantileTransformer(normal) on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-062 | 0.962077 | 0.001472 | -0.008779 | MLPClassifier (64,32) relu early_stopping PowerTransformer(yeo-johnson) on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-063 | 0.961319 | 0.000877 | -0.001086 | MLPClassifier (256,128) relu early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-064 | 0.961562 | 0.001480 | -0.009294 | MLPClassifier (128,64,32,16) relu early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-065 | 0.963162 | 0.000786 | -0.007694 | MLPClassifier (64,32) tanh early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-066 | 0.957414 | 0.000764 | -0.013442 | MLPClassifier (64,32) tanh no early_stopping max_iter=2000 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-067 | 0.961183 | 0.000675 | -0.001979 | MLPClassifier (64,32) tanh early_stopping lr_init=0.01 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-068 | 0.962913 | 0.000718 | -0.007943 | MLPClassifier (64,32) tanh early_stopping lr_init=0.0001 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-069 | 0.951735 | 0.003614 | -0.019121 | MLPClassifier (64,32) tanh early_stopping lr_init=0.001 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, aggressive sample_weight High=30x Low=10x Medium=1x normalized |
| S-070 | 0.961741 | 0.000833 | -0.009115 | MLPClassifier (64,32) tanh SGD solver momentum=0.9 adaptive lr lr_init=0.001 early_stopping StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-071 | 0.963759 | 0.000997 | -0.007097 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping TargetEncoder(cv=5) on 8 cats + StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric, 51 total after TE), sample_weight balanced |
| S-072 | 0.962762 | 0.001271 | -0.008094 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping OrdinalEncoder on 8 cats + StandardScaler on all 51 features (43 numeric + 8 ordinal), poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low, sample_weight balanced |
| S-073 | 0.964422 | 0.000919 | -0.006434 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping multi-seed ensemble (seeds 42, 123, 456 averaged per fold), StandardScaler+OHE, poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric + 8 cats), sample_weight balanced |
| S-074 | 0.960228 | 0.000992 | -0.010628 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping StandardScaler→PCA(0.95 var, whiten=True) on 43 numeric + OHE on 8 cats, poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low, sample_weight balanced |
| S-075 | 0.961186 | 0.001258 | -0.009670 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping QuantileTransformer(output_distribution='uniform') on 43 numeric + OHE on 8 cats, poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low, sample_weight balanced |
| S-076 | 0.962403 | 0.000746 | -0.008453 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping StandardScaler on 25 numeric (11 raw + log1p(Rainfall) + I_SM_low + SM² + Rainfall² + 10 pairwise products of top-5) + OHE on 8 cats, sample_weight balanced |
| S-077 | 0.962391 | 0.001110 | -0.008465 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping QuantileTransformer(normal) on 43 numeric (poly3 top-4 34 + 7 raw + log1p(Rainfall) + I_SM_low) + OrdinalEncoder on 8 cats + StandardScaler on all 51 features, sample_weight balanced |
| S-078 | 0.963187 | 0.000745 | -0.007669 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping validation_fraction=0.05 StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric total) + OHE 8 cats, sample_weight balanced |
| S-079 | 0.964960 | 0.000864 | -0.005896 | MLPClassifier (64,32) tanh adam lr_init=0.001 early_stopping multi-seed ensemble (seeds 42, 123, 456 averaged per fold) + TargetEncoder(cv=5) on 8 cats + StandardScaler on poly3 top-4 (34) + 7 raw + log1p(Rainfall) + I_SM_low (43 numeric, 51 total after TE), sample_weight balanced |
| S-080 | 0.970772 | 0.000718 | -0.000084 | Weighted blend XGB+LR: alpha=0.95×XGB(S-014) + 0.05×LR(S-052) OOF; sweep over [0.95,0.90,0.85,0.80,0.75,0.70] — best at 0.95, all alphas below XGB-only baseline |
| S-081 | 0.970604 | 0.001021 | -0.000252 | LGBM n=800 lr=0.03 leaves=15 subsample=0.9 colsample_bytree=0.8 balanced, SM²+OrdinalEncoder — colsample_bytree=0.8 did not help LGBM (vs S-028: 0.970123, delta +0.000481 over S-028 but still below S-014 best) |
| S-082 | 0.970657 | 0.001010 | -0.000199 | LGBM n=1500 lr=0.02 leaves=15 subsample=0.9 colsample_bytree=0.8 balanced, SM²+OrdinalEncoder — slower learning with more trees improves slightly over S-081 (0.970604) but still below S-014 XGB best (0.970856) |
| S-083 | 0.971177 | 0.000764 | +0.000321 | Weighted blend XGB+LGBM: alpha=0.7×XGB(S-014) + 0.3×LGBM(S-082) OOF; sweep over [0.9,0.8,0.7,0.6,0.5,0.4,0.3] — best at alpha=0.7, positive lift over S-014 XGB-only baseline (0.970856) |
| S-084 | 0.954218 | 0.000676 | -0.016959 | LGBM n=2000 lr=0.02 num_leaves=7 min_child_samples=100 subsample=0.9 colsample_bytree=0.8 balanced, SM²+OrdinalEncoder — too aggressively regularized (num_leaves=7 underfits vs 15 in S-082: 0.970657, large regression -0.016638 vs S-014) |
| S-085 | 0.970782 | 0.000840 | -0.000395 | XGB n=1000 lr=0.025 depth=5 subsample=0.8 colsample_bytree=0.8 balanced, SM²+StandardScaler+OHE — slower learning with 2× trees does not improve over S-014 (0.970856); slightly below standalone XGB best |
| S-086 | 0.969934 | 0.000824 | -0.001243 | HistGBM max_iter=1500 lr=0.02 max_leaf_nodes=15 min_samples_leaf=50 l2_reg=0.1 class_weight=balanced, SM²+OrdinalEncoder — tuned toward LGBM params; 0.969934 close to S-018 (0.969459) but below XGB/LGBM best; note subsample not available in sklearn HistGBM, removed; marginal improvement over S-018 (+0.000475) insufficient for 3-way blend at current best 0.971177 |
| S-087 | 0.971124 | 0.000808 | -0.000053 | Weighted blend XGB+LGBM+HistGBM: sweep [(0.6,0.3,0.1),(0.6,0.25,0.15),(0.5,0.35,0.15),(0.55,0.3,0.15),(0.65,0.25,0.10)] on S-014/S-082/S-086 OOF; best at (0.55,0.30,0.15), slightly below S-083 (0.971177) |
| S-088 | 0.971161 | 0.000785 | -0.000016 | Fine XGB+LGBM blend sweep on S-014/S-082 OOF over alpha=[0.64,0.66,0.68,0.69,0.70,0.71,0.72,0.74,0.76]; near-anchor search stayed just below S-083 |
| S-089 | 0.971927 | 0.000684 | +0.000750 | Multinomial LR stacker on S-014+S-082 OOF/test probs |
| S-090 | 0.971946 | 0.000662 | +0.000019 | Multinomial LR stacker C=4.0 on S-014+S-082 probs |
| S-091 | 0.972013 | 0.000756 | +0.000067 | Multinomial LR stacker C=4.0 on logit S-014+S-082 probs |
| S-092 | 0.963836 | 0.000548 | -0.008177 | Logit S-014+S-082 LR stacker with class_weight=None |
| S-093 | 0.972282 | 0.000704 | +0.000269 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073 probs |
| S-094 | 0.972299 | 0.000659 | +0.000017 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs |
| S-095 | 0.972253 | 0.000654 | -0.000046 | Multinomial LR stacker C=8.0 on logit S-014+S-082+S-073+S-052 probs |
| S-096 | 0.972243 | 0.000670 | -0.000056 | Multinomial LR stacker C=2.0 on logit S-014+S-082+S-073+S-052 probs |
| S-097 | 0.971843 | 0.000590 | -0.000456 | Multinomial LR stacker C=4.0 on raw S-014+S-082+S-073+S-052 probs |
| S-098 | 0.972097 | 0.000610 | -0.000202 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-052 probs |
| S-099 | 0.963954 | 0.000740 | -0.008345 | Multinomial LR stacker C=4.0 class_weight=None on logit S-014+S-082+S-073 probs |
| S-100 | 0.972208 | 0.000625 | -0.000091 | Multinomial LR stacker C=4.0 balanced on HM/LM log-odds S-014+S-082+S-073 |
| S-101 | 0.972282 | 0.000704 | -0.000017 | Multinomial LR C=4.0 balanced on full OVR logits S-014+S-082+S-073 |
| S-102 | 0.972297 | 0.000690 | -0.000002 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium OVR |
| S-103 | 0.972279 | 0.000532 | -0.000020 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium pairwise |
| S-104 | 0.972271 | 0.000598 | -0.000028 | Multinomial LR C=4.0 balanced on S-101 OVR logits + shrunk S-052 Medium pairwise |
| S-105 | 0.972308 | 0.000597 | +0.000009 | Multinomial LR C=4.0 balanced on S-094 OVR logits + shrunk S-052 High/Low |
