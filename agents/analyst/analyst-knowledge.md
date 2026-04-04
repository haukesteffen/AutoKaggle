# Analyst Knowledge

## AK-001 — Dataset Dimensions (S6E4, Irrigation Need)
source: A-001
at: 2026-04-01

- Train: 630,000 rows. Test: 270,000 rows.
- Target: `Irrigation_Need` (multiclass: High / Low / Medium). Metric: balanced accuracy.
- Total features: 19 (11 numeric, 8 categorical). No `id` in test target.
- Numeric features: Soil_pH, Soil_Moisture, Organic_Carbon, Electrical_Conductivity, Temperature_C, Humidity, Rainfall_mm, Sunlight_Hours, Wind_Speed_kmh, Field_Area_hectare, Previous_Irrigation_mm.
- Categorical features: Soil_Type (4), Crop_Type (6), Crop_Growth_Stage (4), Season (3), Irrigation_Type (4), Water_Source (4), Mulching_Used (2), Region (5).
- No boolean-like numerics. All categorical cardinalities are low (≤6). No train-only or test-only category values.

## AK-002 — Class Imbalance: High Class is Rare
source: A-001
at: 2026-04-01

- Class distribution: Low=58.7%, Medium=37.9%, High=3.3%.
- Imbalance ratio (max/min): 17.6×.
- This is severe. Because the metric is balanced accuracy, the High class must be predicted reasonably well. Rebalancing (class weights, oversampling, or threshold tuning) will likely be required.

## AK-003 — No Missingness
source: A-001
at: 2026-04-01

- Zero missing values in both train and test. No imputation required.

## AK-004 — No Train/Test Distributional Shift
source: A-001
at: 2026-04-01

- KS test on all 11 numeric features: all p-values > 0.12. No feature shows significant shift (p<0.01).
- Train and test appear to be drawn from the same distribution. No covariate shift correction needed.

## AK-005 — No Obvious Leakage
source: A-001
at: 2026-04-01

- Maximum |Pearson correlation| between any single numeric feature and the label-encoded target: 0.25 (Soil_Moisture).
- No feature approaches perfect correlation. No single-feature leakage detected.

## AK-006 — No Extreme Outliers
source: A-001
at: 2026-04-01

- No numeric feature has any rows with |z-score| > 5. Feature ranges are well-bounded.
- Rainfall_mm has the widest range (0.38–2499.69) but no outliers by z-score threshold.

## AK-007 — Soil_Moisture is Strongest Numeric Signal
source: A-001
at: 2026-04-01

- Soil_Moisture has the highest single-feature Pearson correlation with the label-encoded target (−0.250).
- Next strongest: Wind_Speed_kmh (0.129), Temperature_C (0.099).
- All other numeric features are weak (|corr| < 0.03).

## AK-008 — Soil_Moisture Exhibits Non-Linear Relationship with High Class
source: A-002
at: 2026-04-01

Soil_Moisture shows clear threshold behavior, not linear relationship:
- Low SM range (8–20): 10.88% High-class prevalence
- Mid SM range (20–30): 6.38% prevalence
- High SM range (>30): 0.14–0.16% prevalence (60–70× drop-off)

This requires polynomial or binning-based feature engineering. Linear terms alone
will not capture the decision boundary.

## AK-009 — Soil_Moisture × Rainfall is Strongest Interaction for High Class
source: A-002
at: 2026-04-01

(Low Soil_Moisture, Low Rainfall) → 23.38% High-class rate (7.0× baseline).
This is the dominant decision boundary for High-class predictions.

Feature to engineer: I(Soil_Moisture < 20 AND Rainfall < 1000 mm)

## AK-010 — Soil_Moisture × Temperature is Second-Strongest Interaction
source: A-002
at: 2026-04-01

(Low Soil_Moisture, High Temperature) → 21.16% High-class rate (6.4× baseline).
S-005 XGBoost mispredictions show +4.96°C temperature bias, indicating model
overfits temperature at the expense of Soil_Moisture interaction signal.

Feature to engineer: I(Soil_Moisture < 20 AND Temperature > 33°C)

## AK-011 — Crop Type Modulates Soil_Moisture Signal (Maize, Sugarcane > Others)
source: A-002
at: 2026-04-01

Within Low Soil_Moisture stratum:
- Maize: 12.61% High-class rate
- Sugarcane: 12.28%
- Rice: 7.24%

Suggests crop-specific moisture thresholds. Consider separate Soil_Moisture bins
or interaction terms for Maize/Sugarcane vs. other crops.

Feature to engineer: I(Crop_Type in ['Maize', 'Sugarcane'] AND Soil_Moisture < 20)

## AK-012 — Soil_Moisture × Humidity and Season are Weak Signals
source: A-002
at: 2026-04-01

Humidity shows mild non-linearity within Low SM (9–13% prevalence) but is weak
overall. Season shows negligible variation across Zaid/Kharif/Rabi.

Not recommended for feature engineering.

## AK-013 — S-014 Fold Stability is Excellent
source: A-003
at: 2026-04-02

S-014 (XGBoost depth=5, subsample=0.8, colsample=0.8 with StandardScaler + PolynomialFeatures):
- CV mean: 0.9709, std: 0.0006 (extremely low variance)
- All 5 folds range 0.9699–0.9717 (max delta < 0.002)
- Hardest fold: Fold 0 (0.9699), easiest fold: Fold 2 (0.9717)
- No evidence of overfitting or fold instability

This tight fold-level consistency suggests the engineering (scaling + polynomial)
has made the model robust across train/valid splits. No fold-specific tuning needed.

## AK-014 — S-014 High-Class Recall is 95.0% Across All Folds
source: A-003
at: 2026-04-02

S-014 achieves exceptional High-class recall:
- Overall High recall: 0.9500 (19,959 TP out of 21,009 samples)
- Per-fold High recall: 0.9462–0.9541 (very consistent)
- TP=19,959, FP=2,515, FN=1,050
- Precision on High: 0.8881 (good; not overfitting to false positives)

This is 95% vs. 5.5% (S-005 baseline). Polynomial + scaling enabled the jump.

## AK-015 — Regional Weakness in East; Seasonal Weakness in Rabi
source: A-003
at: 2026-04-02

S-014 shows minor but consistent subgroup weaknesses:
- East region: High recall 0.9423 (worst, -0.8% vs. best)
- All other regions (Central, North, South, West): 0.950–0.953

- Rabi season: High recall 0.9479 (worst, -0.4% vs. Kharif)
- Kharif: 0.9521, Zaid: 0.9497

- Crop-level: Sugarcane (0.9482) and Potato (0.9484) slightly below Maize (0.9509)

These gaps are small (<1%) and may reflect data distribution rather than model
weakness. Not a priority for tuning unless region/season-specific thresholds show
promise in future experiments.

## AK-016 — S-014 Feature Importance Unavailable Due to Pickle Dependency
source: A-003
at: 2026-04-02

The S-014 model pickle could not be unpickled (ModuleNotFoundError: autokaggle_experiment_artifacts).
Feature importance analysis was not possible.

However, infer from domain knowledge that SM² + StandardScaler + PolynomialFeatures
(esp. Temperature² and Humidity² interactions) likely drive the performance gains.
Next analysis should extract importance via alternative methods (e.g., SHAP, permutation
on test set) if needed to guide future feature engineering.

## AK-017 — Linear Separability is Moderate (LDA at 0.7227 vs Tree at 0.9709)
source: A-004
at: 2026-04-02

LDA classification on numeric features achieves 0.7227 CV, indicating moderate linear separability.
The 97.5% of variance is captured by the first LDA component, but the 2.5% second component
(Medium vs High discrimination) is essential. This ~0.24 gap from LDA baseline to tree performance
suggests non-linear decision boundaries are critical but not insurmountable.

## AK-018 — Top 5 Linear Features (by Logistic Regression Coefficient)
source: A-004
at: 2026-04-02

Ranked by absolute coefficient magnitude on numeric-only LR:
1. Soil_Moisture: 1.042
2. Temperature_C: 0.688
3. Wind_Speed_kmh: 0.561
4. Rainfall_mm: 0.339
5. Soil_pH: 0.047

Soil_Moisture dominates (1.5× Temperature). Wind_Speed and Rainfall are moderate signals.
Remaining 6 numeric features (Humidity, Sunlight, Org Carbon, EC, Field Area, Prev Irrig)
have coefficients < 0.05 and contribute minimally to linear discrimination.

## AK-019 — Preprocessing Choice is Neutral (StandardScaler ≈ RobustScaler ≈ MinMaxScaler)
source: A-004
at: 2026-04-02

Logistic Regression CV on numeric + categorical OHE shows near-identical performance:
- StandardScaler: 0.6977
- RobustScaler: 0.6977
- MinMaxScaler: 0.6976

Scaling choice does not drive performance variance. StandardScaler is recommended
for consistency (standard in literature), not due to superior performance.

## AK-020 — Simple Interactions Yield +0.008 Lift; Transformations Yield +0.037 Lift
source: A-004
at: 2026-04-02

Logistic Regression CV (numeric only):
- Baseline (numeric): 0.6919
- + simple interactions (SM×Temp, SM×Rainfall, etc.): 0.6999 (+0.008)
- + transformations (Rainfall_log, SM², SM<20 bin): 0.7290 (+0.037)

Transformations (especially log-scaling Rainfall and binning SM) are far more impactful
than simple linear products. This aligns with earlier findings (AK-008) that SM exhibits
threshold behavior at ~20, not linear behavior.

## AK-021 — SM × Rainfall is Strongest Linear Interaction (coef=0.753)
source: A-004
at: 2026-04-02

Among 4 tested linear interactions, SM × Rainfall has the highest coefficient (0.753),
followed by Temp × Rainfall (0.616) and SM × Temperature (0.426). SM × Humidity is weak
(0.054). This supports domain insight from A-002: low SM + low rainfall is the dominant
high-irrigation-need pattern (7.0× baseline prevalence).

## AK-022 — Dropping Weak Features Hurts Linear Model (-0.0003 CV)
source: A-004
at: 2026-04-02

Hypothesis: drop Humidity, Previous_Irrigation_mm, Sunlight_Hours (bottom 3 by coefficient).
Result: CV drops from 0.6919 to 0.6916 (−0.0003). Weak features do not add noise;
they add small signal. Keep all 11 numeric features for linear models.

## AK-023 — S-032 LR: Subgroup (SM<20 AND Rainfall<1000) is Already Well-Recalled
source: A-005
at: 2026-04-02

S-032 LR with SM², log(Rainfall), I_SM_low, StandardScaler+OHE (CV=0.8882):
- High recall IN subgroup (SM<20 AND Rainfall<1000, 5.6% of data): 0.9515
- High recall OUTSIDE subgroup (94.4% of data): 0.9059
- Delta: +0.0457 better inside than outside subgroup

The (SM<20 AND Rainfall<1000) subgroup is the model's stronger zone.
Adding the joint indicator I(SM<20 AND Rainfall<1000) is unlikely to improve recall here.
The primary LR weakness is outside the subgroup (1329 of 1663 total High-class FNs = 80%).
All subgroup FNs (334) are predicted as Medium, not Low — a calibration/boundary issue,
not a missing indicator issue. Out-of-subgroup improvements should be the focus.

## AK-024 — S-032 LR Out-of-Subgroup FNs Cluster in Two Extreme Zones
source: A-006
at: 2026-04-02

Out-of-subgroup High-class FNs (1329 total, 79.9% of all LR FNs) cluster in two distinct
high-FN-rate regions — NOT spread uniformly across SM or Rainfall:

Zone analysis:
- Zone B (SM>=20 AND Rain<1000): 40.6% of out-subgroup FNs, recall 87.3%
- Zone A (SM<20 AND Rain>=1000): 29.2% of out-subgroup FNs, recall 94.2%
- Zone C (SM>=20 AND Rain>=1000): 30.2% of out-subgroup FNs, recall 87.6%

Two high-FN-rate pockets identified:
1. SM>=35 region: 49.7% FN rate (235 FNs, 238 TPs). High prevalence drops to 0.53% here
   but FN/(FN+TP) is extreme — model badly mislabels most High-class samples in this zone.
2. Temperature<25 region: 59.1% FN rate (338 FNs, 234 TPs). Also very high FN rate.

SM 20-25 zone (Zone B core): large absolute FN count (659 FNs, 49.6% of all out-subgroup
FNs) but only 9.7% FN rate — model already captures most High here. Adding I(SM 20-25)
would include too many TPs for minimal gain.

SM x Temperature cross-tab:
- SM<25 & Temp<33: 54.3% of FNs but only 17.0% FN rate (mixed zone)
- SM>=25 & Temp<33: 57.4% FN rate (151 FNs, 112 TPs) — most concentrated cluster
- SM>=25 & Temp>=33: 33.6% FN rate (131 FNs, 259 TPs)

All out-of-subgroup FNs are predicted as Medium (99.0%), not Low.
LR model consistently confused High → Medium in these out-of-subgroup zones.

Best candidate threshold indicators ranked by FN-rate purity:
- I(Temperature<25): 59.1% FN rate, captures 25.4% of FNs
- I(SM>=35): 49.7% FN rate, captures 19.6% of FNs (but very small High prevalence)
- I(SM>=25 AND Temp<33): 57.4% FN rate, captures 11.4% of FNs

NOTE (A-007): High FN rate does NOT equal High-class enrichment. See AK-025 for selectivity analysis.

## AK-026 — Target Encoding Does Not Beat OHE for Categoricals in LR with Degree-2 Poly
source: A-008
at: 2026-04-02

Fold-safe target encoding (3 columns per categorical, 24 TE columns total) was compared
to OHE on the same feature set (S-039: degree-2 poly on all 11 numerics, LR C=1.0 balanced).

Result: TE CV = 0.893384 vs OHE CV = 0.893806 → delta = −0.000422 (TE is WORSE).
All 5 folds showed TE ≤ OHE (range: −0.000719 to −0.000064).
Neither approach exceeds the +0.001 materiality threshold above OHE.

OHE CV (0.893806) closely matches S-039 reference (0.893756), confirming faithful replication.
OHE remains the preferred categorical encoding for logistic regression on this dataset.

## AK-025 — Candidate Threshold Indicators from A-006 Are DEPLETED Zones (Not Enriched)
source: A-007
at: 2026-04-02

The three A-006 candidate indicators are in heavily depleted High-class zones, not enriched ones:
- I(Temp<25): 0.218% High prevalence (0.07× baseline of 3.3%)
- I(SM>=35): 0.149% High prevalence (0.04× baseline)
- I(SM>=25 AND Temp<33): 0.082% High prevalence (0.02× baseline)
- I(Temp<25 AND SM>=35): 0.016% High prevalence (0.00× baseline — almost no High-class)

Their complement zones have High prevalence of 3.2%–5.5% (above baseline).

Interpretation: These indicators do NOT have sufficient selectivity (High-class enrichment) to justify
adding them as positive-signal indicators for LR. The high FN rate in these zones reflects that
the model struggles in low-prevalence zones — not that the zones are enriched for High-class.

Adding these indicators as binary features to LR would encode negative signal (depletion, not enrichment).
Whether that negative signal is already captured by SM² and Temperature terms needs investigation
(see A-007 follow_up hypotheses).

## AK-027 — MLP(64,32) is Strongly Diverse from LR on S-040 Feature Set
source: A-009
at: 2026-04-03

MLPClassifier(hidden=(64,32), relu, max_iter=500, early_stopping=True) on the S-040 feature set:
- MLP CV: 0.9539 ± 0.0028 (vs LR CV: 0.8954 ± 0.0012; delta: +0.0585)
- MLP substantially outperforms LR on balanced accuracy — it is not a weak diversity source.
- OOF High-class proba Pearson r (LR vs MLP): 0.730 (well below 0.97 threshold)
- OOF Low-class proba Pearson r: 0.906
- OOF Medium-class proba Pearson r: 0.842
- OOF prediction agreement: 89.45% (10.55% disagreement = 66,434 rows differ)
- High-class recall: LR=0.928, MLP=0.901 (LR edges MLP here; MLP has higher overall CV due to Low/Medium)
- MLP calibrates probabilities differently: mean High proba LR=0.078 vs MLP=0.033

Diversity verdict: YES. MLP adds meaningful diversity for ensembling. Low cross-model correlation
(0.73) makes it a strong candidate for a 3-way blend with LR and XGBoost.

## AK-028 — S-045 MLP is Too Correlated with S-014 XGBoost to Ensemble Beneficially
source: A-010
at: 2026-04-03

S-045 MLP (CV=0.9618) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
- OOF prediction agreement: 98.80% (only 7,546 of 630,000 rows differ)
- High-class proba Pearson r: 0.961 (below 0.97 diversity threshold, but barely)
- High-class Pearson r among true High samples only: 0.919
- High-class recall: S-014=0.9500, S-045=0.9382 (S-014 is superior)
- Complementary TPs: S-045 has 104 unique TPs, S-014 has 353 unique TPs (S-014 covers more)
- Simple average ensemble BA: 0.9679 — which is WORSE than S-014 standalone (0.9709)
- Ensemble lift vs best: −0.0030 (negative lift)

Both models predict wrong High samples as Medium (100% of wrong predictions in that direction).
The models are too similar in prediction space despite different architectures — S-045 does not
recover the cases S-014 misses in a way that compensates for S-045's lower overall accuracy.

Conclusion: Simple average of S-045 + S-014 is not recommended. Weighted blending favoring S-014,
or finding a model with corr < 0.90 vs S-014, are better paths.

## AK-029 — S-052 LR is More Diverse from S-014 XGBoost Than S-045 MLP Was
source: A-011
at: 2026-04-03

S-052 LR (CV=0.9286) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
- OOF prediction agreement: 93.23% (vs 98.80% for S-045 MLP — meaningfully more diverse)
- High-class proba Pearson r: 0.883 (vs 0.961 for S-045 MLP — well below 0.97 threshold)
- High-class Pearson r among true High samples only: 0.816
- High-class recall: S-014=0.9500, S-052=0.9474 (S-014 marginally superior)
- Complementary TPs: S-052 has 284 unique TPs (vs 104 for S-045 MLP), S-014 has 340 unique TPs
- Simple average ensemble BA: 0.9647 — WORSE than S-014 standalone (0.9709), lift = −0.0062
- Both models' errors are almost entirely High→Medium confusions (S-052: 99.4% FNs to Medium)

S-052 LR is more diverse than S-045 MLP in prediction space (higher disagreement, lower proba corr,
more complementary High TPs). However, simple averaging still yields negative lift (−0.0062) because
the LR's lower overall accuracy drags the ensemble down. Weighted blending (e.g., 0.8×XGB + 0.2×LR)
or threshold-tuning may recover positive lift. Do not use 50-50 simple average.

## AK-030 — S-073 Adds Diversity vs S-014/S-082 but Hurts Simple 3-Way Averaging
source: A-012
at: 2026-04-04

OOF artifact comparison across S-014 XGBoost, S-082 LightGBM, S-073 MLP ensemble, and S-083 weighted blend:
- S-014 vs S-082 are extremely correlated: High=0.9942, Low=0.9984, Medium=0.9975; argmax agreement=99.62%
- S-073 is less correlated with both tree models on every class:
  S-073 vs S-014: High=0.9755, Low=0.9962, Medium=0.9919; agreement=99.18%
  S-073 vs S-082: High=0.9735, Low=0.9965, Medium=0.9920; agreement=99.20%
- Despite that diversity, simple averaging degrades performance:
  S-014+S-082 avg BA = 0.971153
  S-014+S-082+S-073 avg BA = 0.969687
  S-083 weighted blend BA = 0.971177
  3-way avg vs S-083 delta = -0.001490

Durable conclusion: lower OOF probability correlation alone was not sufficient here. S-073 provides
real diversity relative to the XGB/LGBM pair, but naive 3-way averaging is worse than both the 2-way
tree average and the current S-083 weighted blend.

## AK-031 — S-052 Remains Diverse Against S-093, but Naive Averaging Regresses Sharply
source: A-013
at: 2026-04-04

OOF artifact comparison across S-093 stacker, S-052 logistic regression, and the
S-014/S-082 tree baseline:
- S-014 vs S-082 remain extremely correlated: High=0.9942, Low=0.9984, Medium=0.9975; argmax agreement=99.62%
- S-093 vs S-052 are materially less correlated: High=0.8781, Low=0.9353, Medium=0.9049; argmax agreement=93.17%
- Correlation gap vs tree pair is large on every class: High -0.1161, Low -0.0632, Medium -0.0926
- But simple average S-093+S-052 BA = 0.966404, which is -0.005877 below S-093 alone (0.972282)

Durable conclusion: S-052 still carries distinct signal even after S-093, but that signal is too noisy
for naive averaging. Any further use of S-052 should rely on a learned combiner rather than a plain average.

## AK-032 — S-094's Gain Over S-093 Is Not a Durable High-Recovery Pattern
source: A-014
at: 2026-04-04

OOF comparison of S-094 (logit LR stacker with S-052 added) vs S-093:
- Balanced accuracy gain is only +0.000018, with just 300 of 630,000 argmax predictions changed
- High recall is unchanged at 0.962683; S-094 recovers 10 true High cases and loses 10 others
- The lift comes from Medium recall (+0.000059) while Low recall slightly worsens (-0.000005)
- S-052 does not explain the recovered Highs: on the 10 recovered High rows, S-052 predicts High 0 times; on the 10 lost High rows, S-052 predicts High 9 times
- Across all changed rows, S-052 matches S-093 233 times and S-094 only 53 times

Durable conclusion: the S-094 over S-093 improvement is a tiny Medium-class reallocation, not a
concentrated High-class recovery pattern attributable to S-052.

## AK-033 — On S-094 vs S-093 Changed Rows, S-052 Aligns with Some Beneficial Medium Corrections but with No High Recoveries
source: A-015
at: 2026-04-04

Within the 300 rows where S-094 and S-093 disagree:
- Beneficial Medium corrections: 134 rows; S-052 also predicts Medium on 31 of them
- High recoveries: 10 rows; S-052 predicts High on 0 of them
- By the same changed-row test, S-052's target-class support is stronger for beneficial Medium corrections than for High recoveries on all three checks used in A-015: argmax support (31 vs 0), target prob > old-pred prob (31 vs 0), and mean target-vs-old margin (-0.3789 vs -0.5885; less negative for Medium)
- S-052's Medium signal is noisy rather than uniformly helpful: it also predicts Medium on 99 of the 120 harmful Medium flips

Durable conclusion: relative to the exact S-094 over S-093 delta, S-052 contributes Medium-oriented signal and no direct High-recovery signal; the observed Medium alignment is real but mixed with substantial noisy Medium preference.
