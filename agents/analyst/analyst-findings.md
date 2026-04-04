# Analyst Findings


## A-001
at: 2026-04-01T20:02Z
q: Does the dataset have any critical data quality issues — significant missingness, obvious leakage features, severe class imbalance, or meaningful train/test distributional shift — that must be addressed before fitting base models?
verdict: supported
conf: high
evidence:
============================================================
DATASET DIMENSIONS
============================================================
train_rows:    630000
test_rows:     270000
total_features: 19
numeric_features: 11
categorical_features: 8
numeric_cols: ['Soil_pH', 'Soil_Moisture', 'Organic_Carbon', 'Electrical_Conductivity', 'Temperature_C', 'Humidity', 'Rainfall_mm', 'Sunlight_Hours', 'Wind_Speed_kmh', 'Field_Area_hectare', 'Previous_Irrigation_mm']
categorical_cols: ['Soil_Type', 'Crop_Type', 'Crop_Growth_Stage', 'Season', 'Irrigation_Type', 'Water_Source', 'Mulching_Used', 'Region']

============================================================
CLASS BALANCE (target = Irrigation_Need)
============================================================
                  count  proportion
Irrigation_Need                    
Low              369917      0.5872
Medium           239074      0.3795
High              21009      0.0333
imbalance_ratio (max/min): 17.6075
ALERT: severe_class_imbalance=True

============================================================
MISSINGNESS
============================================================
train_missing: none
test_missing: none

============================================================
BOOLEAN-LIKE NUMERICS (<=2 unique values in numeric cols)
============================================================
  none found

============================================================
CATEGORICAL CARDINALITY
============================================================
  Soil_Type: train_unique=4, test_unique=4
  Crop_Type: train_unique=6, test_unique=6
  Crop_Growth_Stage: train_unique=4, test_unique=4
  Season: train_unique=3, test_unique=3
  Irrigation_Type: train_unique=4, test_unique=4
  Water_Source: train_unique=4, test_unique=4
  Mulching_Used: train_unique=2, test_unique=2
  Region: train_unique=5, test_unique=5

============================================================
OUTLIER FLAGS (|z-score| > 5)
============================================================
  no features with |z|>5 outliers

============================================================
TRAIN/TEST DISTRIBUTIONAL SHIFT (KS test, numeric features)
============================================================
                feature  ks_stat  p_value
            Rainfall_mm  0.00273 0.120310
     Field_Area_hectare  0.00245 0.204971
               Humidity  0.00243 0.213529
          Temperature_C  0.00203 0.418635
         Wind_Speed_kmh  0.00199 0.443792
Electrical_Conductivity  0.00190 0.504036
 Previous_Irrigation_mm  0.00184 0.541998
         Sunlight_Hours  0.00181 0.563442
         Organic_Carbon  0.00168 0.663193
          Soil_Moisture  0.00148 0.801267
                Soil_pH  0.00127 0.922450

n_features_with_significant_shift (p<0.01): 0 / 11
meaningful_train_test_shift=False

============================================================
NUMERIC FEATURE SUMMARY (train)
============================================================
                           min      max       mean       std
Soil_pH                   4.80     8.20     6.4825    0.9225
Soil_Moisture             8.00    64.99    37.3045   16.3771
Organic_Carbon            0.30     1.60     0.9229    0.3658
Electrical_Conductivity   0.10     3.50     1.7446    0.9523
Temperature_C            12.00    42.00    26.9982    8.6236
Humidity                 25.00    94.99    61.5632   19.7082
Rainfall_mm               0.38  2499.69  1462.2076  612.9897
Sunlight_Hours            4.00    11.00     7.5134    1.9993
Wind_Speed_kmh            0.50    20.00    10.3754    5.6895
Field_Area_hectare        0.30    15.00     7.5177    4.2181
Previous_Irrigation_mm    0.02   119.99    62.3182   34.2469

============================================================
LEAKAGE SCREEN (numeric feature mean absolute correlation with label-encoded target)
============================================================
                feature  pearson_corr_with_label
          Soil_Moisture                 -0.24978
         Wind_Speed_kmh                  0.12855
          Temperature_C                  0.09945
            Rainfall_mm                  0.02726
Electrical_Conductivity                  0.02159
                Soil_pH                 -0.01903
               Humidity                 -0.01847
     Field_Area_hectare                  0.01776
 Previous_Irrigation_mm                  0.01635
         Organic_Carbon                  0.00603
         Sunlight_Hours                  0.00432

max_abs_corr=0.2498 — no obvious leakage detected

============================================================
SUMMARY
============================================================
critical_issues_found: YES
  - severe class imbalance (ratio=17.61)

follow_up:
- Does balanced accuracy improve materially (>+0.005) when using class_weight='balanced' or oversampling High class vs. no rebalancing in a baseline LightGBM?
- Does treating Irrigation_Type and Water_Source as target-encoding features (given their moderate-cardinality and categorical nature) yield better CV than simple ordinal encoding?
- Does Soil_Moisture (strongest single predictor, corr=-0.25) remain the dominant feature in a gradient-boosted model's importance ranking?


## A-002
at: 2026-04-01T22:24Z
q: Does Soil_Moisture (the strongest single predictor, r=-0.25) exhibit non-linear or interaction patterns with other features (e.g. Temperature, Humidity, Rainfall, Crop_Type, Season) that would justify polynomial, binning, or interaction feature engineering? Use the S-005 artifact (oof-preds) to identify mispredictions and inspect feature patterns in High-class samples.
verdict: supported
conf: high
reference: experiment=S-005
evidence:

SOIL_MOISTURE NON-LINEARITY (THRESHOLD BEHAVIOR):
High-class prevalence by Soil_Moisture quintile:
  Bin 1 (7.94–19.40]:   10.88% (1.7× baseline)
  Bin 2 (19.40–30.80]:  6.38%  (declining)
  Bin 3–5 (>30.80):     0.14–0.16% (CLIFF — 60–70× drop)

Clear non-linear signature: High class concentrates in LOW Soil_Moisture (8–20),
then drops sharply above 20. Linear terms cannot capture this threshold.

S-005 XGBoost baseline performance:
  Total High samples: 21,009
  Correctly predicted: 1,157 (5.5% recall)
  Mispredicted as Low: 19,852 (94.5%)

Correctly-predicted vs. Mispredicted High samples:
  Correctly predicted: Mean SM = 21.30 (wider distribution, Std 12.43)
  Mispredicted:        Mean SM = 17.46 (concentrated, Std 7.03)
  Difference: -3.84 (mispredicted cluster at LOWER SM values)

Interpretation: Model captures some High-class signal in higher-SM region but misses
the dominant low-SM concentrations. Suggests threshold/polynomial terms are needed.

======================================================================
INTERACTION #1: Soil_Moisture × Rainfall (HIGHEST PRIORITY — 7.0× baseline)
======================================================================

High-class proportion by 3×3 bins:
  Low_SM  + Low_Rain:   23.38% ← STRONGEST signal
  Low_SM  + Mid_Rain:    5.71%
  Low_SM  + High_Rain:   7.64%
  [All Mid/High SM combinations: <1%]

KEY PATTERN: (Soil_Moisture < 20 AND Rainfall < 1000mm) → 23% High-class rate
This is 7.0× the baseline (3.3%). Dominant decision boundary for High class.

Misprediction analysis:
  Correctly predicted High:  Mean Rainfall = 1,321 mm
  Mispredicted High:         Mean Rainfall = 970 mm
  Difference: -351 mm (MUCH LOWER rainfall in mispredictions)

XGBoost underfits the (Low SM, Low Rain) region. Mispredicted High samples show
lower rainfall, indicating model fails to recognize dry+low-moisture as High-need.

RECOMMENDATION: Engineered feature I(Soil_Moisture < 20 AND Rainfall < 1000)

======================================================================
INTERACTION #2: Soil_Moisture × Temperature (HIGH PRIORITY — 6.4× baseline)
======================================================================

High-class proportion by 3×3 bins:
  Low_SM  + Low_Temp:    1.68%
  Low_SM  + Mid_Temp:    6.54%
  Low_SM  + High_Temp:  21.16% ← STRONG
  [All Mid/High SM combinations: <0.35%]

KEY PATTERN: (Soil_Moisture < 20 AND Temperature > 33°C) → 21% High-class rate
Second-strongest interaction, 6.4× baseline.

Misprediction analysis:
  Correctly predicted High:  Mean Temperature = 29.88°C
  Mispredicted High:         Mean Temperature = 34.84°C
  Difference: +4.96°C (MUCH HOTTER in mispredictions)

XGBoost overfits temperature in mispredictions. When SM is moderate/high AND temp
is extremely high, model predicts Low instead of High. Temperature dominates the
feature space, masking SM interaction at high-temp edges.

RECOMMENDATION: Engineered feature I(Soil_Moisture < 20 AND Temperature > 33)

======================================================================
INTERACTION #3: Soil_Moisture × Crop_Type (MODERATE PRIORITY)
======================================================================

High-class rates within Low Soil_Moisture stratum, by crop:
  Maize:     12.61% ← Highest
  Sugarcane: 12.28%
  Cotton:    11.04%
  Wheat:     9.92%
  Potato:    8.38%
  Rice:      7.24%  ← Lowest

Within Mid/High SM: Signal disappears (<0.2% across all crops)

PATTERN: Low SM + (Maize OR Sugarcane) → 12%+ High-class rate
Crop-specific thresholds exist. Maize and Sugarcane show elevated High-class
prevalence when soil moisture is low.

RECOMMENDATION: Crop-specific Soil_Moisture bins or indicator
  I(Crop_Type in ['Maize', 'Sugarcane'] AND Soil_Moisture < 20)

======================================================================
INTERACTION #4: Soil_Moisture × Humidity (WEAK SIGNAL — not recommended)
======================================================================

High-class proportion within Low SM:
  Low_Humidity:   9.04%
  Mid_Humidity:  12.67% (peak)
  High_Humidity:  8.96%

Mild non-linear behavior within Low SM (9–13%), but overall interaction weaker
than Temperature or Rainfall. Mispredictions show only +1.03°C humidity difference.
Not a primary driver of misclassification.

======================================================================
INTERACTION #5: Soil_Moisture × Season (WEAK SIGNAL — not recommended)
======================================================================

High-class prevalence within Low SM, by season:
  Zaid:   10.31%
  Kharif: 10.27%
  Rabi:   10.21%

Negligible seasonal variation. No clear season-specific threshold pattern.

======================================================================
SUMMARY: FEATURE ENGINEERING RECOMMENDATIONS
======================================================================

HIGHEST PRIORITY (implement together for maximum lift):
1. Soil_Moisture² (polynomial): Captures non-linear threshold at SM≈20
2. I(Soil_Moisture < 20 AND Rainfall < 1000): Targets dominant (Low SM, Low Rain)
   high-need region (7.0× baseline prevalence)
3. I(Soil_Moisture < 20 AND Temperature > 33): Targets hot+dry condition (6.4×
   baseline prevalence)

MODERATE PRIORITY:
4. Crop-specific Soil_Moisture indicator: I(Crop in ['Maize', 'Sugarcane'] AND SM < 20)

NOT RECOMMENDED:
   - Soil_Moisture × Humidity: weak signal, minimal misprediction correlation
   - Soil_Moisture × Season: negligible variation across seasons

follow_up:
- Does adding Soil_Moisture² + I(SM < 20 AND Rain < 1000) + I(SM < 20 AND Temp > 33) improve XGBoost CV balanced accuracy by >0.010?
- Does crop-specific Soil_Moisture binning improve High-class recall without degrading Low/Medium accuracy?
- Is the engineered-feature lift driven primarily by non-linearity (polynomial) or by interaction detection?


## A-003
at: 2026-04-02T00:08Z
q: Why is S-014 (0.9709) so strong? What is fold stability like, which folds drive the score, what does feature importance reveal about the SM² contribution, and are there subgroups (by target class, season, region) where the model is systematically weak?
verdict: supported
conf: high
evidence:
======================================================================
S-014 MODEL ANALYSIS (XGBoost, depth=5, subsample=0.8, colsample=0.8)
======================================================================
Note: Could not load pickled model (ModuleNotFoundError). Feature importance will be unavailable.

======================================================================
FOLD-BY-FOLD PERFORMANCE
======================================================================
Fold 0: score=0.969880, n=126000, recalls: High=0.9462, Low=0.9957, Medium=0.9677
Fold 1: score=0.971373, n=126000, recalls: High=0.9522, Low=0.9956, Medium=0.9663
Fold 2: score=0.971734, n=126000, recalls: High=0.9541, Low=0.9956, Medium=0.9655
Fold 3: score=0.970618, n=126000, recalls: High=0.9484, Low=0.9954, Medium=0.9681
Fold 4: score=0.970676, n=126000, recalls: High=0.9493, Low=0.9954, Medium=0.9674

Fold Scores: ['0.969880', '0.971373', '0.971734', '0.970618', '0.970676']
Mean CV: 0.970856
Std CV: 0.000645
Min Fold: 0 (0.969880)
Max Fold: 2 (0.971734)
Overall Balanced Accuracy (OOF): 0.970856

======================================================================
PER-CLASS PERFORMANCE (OVERALL OOF)
======================================================================

High (class idx 0):
  Count: 21009 (3.33%)
  Recall: 0.950021
  Precision: 0.888093
  TP=19959, FP=2515, FN=1050

Low (class idx 1):
  Count: 369917 (58.72%)
  Recall: 0.995558
  Precision: 0.985602
  TP=368274, FP=5380, FN=1643

Medium (class idx 2):
  Count: 239074 (37.95%)
  Recall: 0.966989
  Precision: 0.988498
  TP=231182, FP=2690, FN=7892

======================================================================
FEATURE IMPORTANCE (from S-014 model)
======================================================================
Note: Model pickle could not be loaded. Feature importance unavailable.

======================================================================
SUBGROUP ANALYSIS: PERFORMANCE BY REGION
======================================================================

Central (n=123712, 19.64%):
  Balanced Accuracy: 0.971890
  High Recall: 0.952706 (n=4250)
  Low Recall: 0.995502 (n=73363)
  Medium Recall: 0.967461 (n=46099)

East (n=126163, 20.03%):
  Balanced Accuracy: 0.968504
  High Recall: 0.942281 (n=3621)
  Low Recall: 0.995285 (n=74873)
  Medium Recall: 0.967946 (n=47669)

North (n=114127, 18.12%):
  Balanced Accuracy: 0.970856
  High Recall: 0.950409 (n=3912)
  Low Recall: 0.995682 (n=65766)
  Medium Recall: 0.966478 (n=44449)

South (n=134809, 21.40%):
  Balanced Accuracy: 0.971197
  High Recall: 0.951121 (n=4685)
  Low Recall: 0.995788 (n=79069)
  Medium Recall: 0.966683 (n=51055)

West (n=131189, 20.82%):
  Balanced Accuracy: 0.971386
  High Recall: 0.952213 (n=4541)
  Low Recall: 0.995537 (n=76846)
  Medium Recall: 0.966407 (n=49802)

======================================================================
SUBGROUP ANALYSIS: PERFORMANCE BY SEASON
======================================================================

Kharif (n=216561, 34.37%):
  Balanced Accuracy: 0.971748
  High Recall: 0.952135 (n=7542)
  Low Recall: 0.995482 (n=123732)
  Medium Recall: 0.967627 (n=85287)

Rabi (n=208033, 33.02%):
  Balanced Accuracy: 0.969893
  High Recall: 0.947912 (n=6681)
  Low Recall: 0.995536 (n=124772)
  Medium Recall: 0.966231 (n=76580)

Zaid (n=205406, 32.60%):
  Balanced Accuracy: 0.970815
  High Recall: 0.949749 (n=6786)
  Low Recall: 0.995659 (n=121413)
  Medium Recall: 0.967037 (n=77207)

======================================================================
SUBGROUP ANALYSIS: HIGH CLASS RECALL BY REGION & SEASON
======================================================================

High-class Recall by Region:
  Central: 0.952706 (n_high=4250)
  East: 0.942281 (n_high=3621)
  North: 0.950409 (n_high=3912)
  South: 0.951121 (n_high=4685)
  West: 0.952213 (n_high=4541)

High-class Recall by Season:
  Kharif: 0.952135 (n_high=7542)
  Rabi: 0.947912 (n_high=6681)
  Zaid: 0.949749 (n_high=6786)

High-class Recall by Crop_Type:
  Cotton: 0.949696 (n_high=3777)
  Maize: 0.950920 (n_high=4401)
  Potato: 0.948380 (n_high=2809)
  Rice: 0.953069 (n_high=2493)
  Sugarcane: 0.948171 (n_high=4264)
  Wheat: 0.950689 (n_high=3265)

======================================================================
SUMMARY: HARDEST FOLDS & SUBGROUPS
======================================================================

Hardest Fold: Fold 0 with score 0.969880
Worst Season for High-class Recall: Rabi (0.947912)
Worst Region for High-class Recall: East (0.942281)
Worst Crop for High-class Recall: Sugarcane (0.948171)

follow_up:
- Can we improve East region High-class recall (currently 0.9423) by region-specific threshold tuning or feature engineering?
- Is the Rabi season weakness (0.9479 BA, High recall 0.9479) driven by seasonal covariate shift or just natural data variance?
- Does adding region/season-specific SM² bins improve over global SM² on East/Rabi subgroups without hurting overall CV?


## A-004
at: 2026-04-02T19:42Z
q: What linear-separability signal exists in this dataset? Which features are most informative in linear space (not just via trees)? Are there interaction patterns or feature transformations (log, binning, polynomial) that would boost linear model performance? What preprocessing (scaling strategy, feature normalization) is optimal for logistic regression / linear SVM?
verdict: supported
conf: high
evidence:
================================================================================
LINEAR MODEL SEPARABILITY ANALYSIS (vs S-014 XGBoost at 0.9709)
================================================================================

Dataset: 630000 samples, 11 numeric, 8 categorical
Numeric features: ['Soil_pH', 'Soil_Moisture', 'Organic_Carbon', 'Electrical_Conductivity', 'Temperature_C', 'Humidity', 'Rainfall_mm', 'Sunlight_Hours', 'Wind_Speed_kmh', 'Field_Area_hectare', 'Previous_Irrigation_mm']
Categorical features: ['Soil_Type', 'Crop_Type', 'Crop_Growth_Stage', 'Season', 'Irrigation_Type', 'Water_Source', 'Mulching_Used', 'Region']
Target distribution: {1: np.int64(369917), 2: np.int64(239074), 0: np.int64(21009)}

================================================================================
PART 1: CORRELATION-BASED LINEAR IMPORTANCE (numeric features)
================================================================================

Top 5 Numeric Features by Absolute Correlation with Target:
  1. Soil_Moisture: 0.249778
  2. Wind_Speed_kmh: 0.128551
  3. Temperature_C: 0.099445
  4. Rainfall_mm: 0.027262
  5. Electrical_Conductivity: 0.021587

================================================================================
PART 2: LINEAR DISCRIMINANT ANALYSIS (LDA)
================================================================================

LDA Classification Score (numeric features only): 0.722652
LDA explained variance ratio: [0.97511458 0.02488542]

Class means in LDA space (first 2 components):
  High: [-2.0750, -0.5060]
  Low: [0.5527, -0.0329]
  Medium: [-0.6728, 0.0954]

================================================================================
PART 3: PREPROCESSING IMPACT (StandardScaler vs RobustScaler vs MinMaxScaler)
================================================================================

Logistic Regression CV Scores by Scaling Strategy (numeric + categorical OHE):
  StandardScaler      : mean=0.697717, std=0.001440, scores=['0.7000', '0.6978', '0.6984']...
  RobustScaler        : mean=0.697659, std=0.001413, scores=['0.6999', '0.6977', '0.6984']...
  MinMaxScaler        : mean=0.697656, std=0.001433, scores=['0.7000', '0.6976', '0.6984']...

================================================================================
PART 4: LOGISTIC REGRESSION COEFFICIENTS
================================================================================

Logistic Regression trained on 19 features (numeric + categorical OHE)
Classes: ('High', 'Low', 'Medium')

Top 10 Features by Average Absolute Coefficient Magnitude:
  1. Soil_Moisture                 : 1.123841
  2. Temperature_C                 : 0.730844
  3. cat_6                         : 0.649809
  4. Wind_Speed_kmh                : 0.587779
  5. Rainfall_mm                   : 0.416059
  6. cat_5                         : 0.082960
  7. Soil_pH                       : 0.044526
  8. Electrical_Conductivity       : 0.038647
  9. cat_2                         : 0.025592
  10. Organic_Carbon                : 0.024003

================================================================================
PART 5: FEATURE IMPORTANCE (numeric features only, no categorical)
================================================================================

Top 5 Numeric Features by Logistic Regression Coefficient Magnitude:
  1. Soil_Moisture                 : 1.042429
  2. Temperature_C                 : 0.687699
  3. Wind_Speed_kmh                : 0.560858
  4. Rainfall_mm                   : 0.338685
  5. Soil_pH                       : 0.046769

================================================================================
PART 6: INTERACTION STRENGTH (simple products in linear space)
================================================================================

Feature indices: SM=1, Temp=4, Rainfall=6, Humidity=5

Logistic Regression CV (5-fold) on numeric features with simple interactions:
  Mean: 0.699875, Std: 0.002067
Logistic Regression CV (5-fold) on numeric features ONLY:
  Mean: 0.691913, Std: 0.002261

Lift from interactions: 0.007962

Top 8 Features (numeric + interactions) by Coefficient Magnitude:
  1. SM × Rainfall                 : 0.753250
  2. Soil_Moisture                 : 0.713537
  3. Rainfall_mm                   : 0.638943
  4. Temp × Rainfall               : 0.615677
  5. Wind_Speed_kmh                : 0.552910
  6. Temperature_C                 : 0.505151
  7. SM × Temp                     : 0.426493
  8. SM × Humidity                 : 0.054246

================================================================================
PART 7: FEATURE TRANSFORMATIONS (log, polynomial, binning)
================================================================================

Logistic Regression CV (5-fold) with transformations (log + poly + binning):
  Mean: 0.728958, Std: 0.002309
  Lift vs numeric only: 0.037045

================================================================================
PART 8: FEATURE SELECTION (weak features to drop)
================================================================================

Numeric Features Ranked by Importance (Logistic Regression):
   1. Soil_Moisture                 : 1.042429
   2. Temperature_C                 : 0.687699
   3. Wind_Speed_kmh                : 0.560858
   4. Rainfall_mm                   : 0.338685
   5. Soil_pH                       : 0.046769
   6. Electrical_Conductivity       : 0.037054
   7. Organic_Carbon                : 0.018663
   8. Field_Area_hectare            : 0.017808
   9. Humidity                      : 0.015850
  10. Previous_Irrigation_mm        : 0.013623
  11. Sunlight_Hours                : 0.006473

Weakest Features (candidates for dropping):
  - Humidity: 0.015850
  - Previous_Irrigation_mm: 0.013623
  - Sunlight_Hours: 0.006473

Logistic Regression CV (5-fold) dropping bottom 3 weak features:
  Mean: 0.691590, Std: 0.002638
  Lift vs all numeric: -0.000323

================================================================================
SUMMARY & RECOMMENDATIONS FOR LINEAR MODELS
================================================================================

Linear Model Performance (Logistic Regression, 5-fold CV):
  Numeric features only:         0.691913
  Numeric + simple interactions: 0.699875 (delta=+0.007962)
  Numeric + transformations:     0.728958 (delta=+0.037045)
  Numeric (strong features):     0.691590 (delta=-0.000323)

Gap vs S-014 XGBoost (0.9709):
  Current best LR:    0.728958
  Gap:                0.241942

TOP-5 FEATURES (Linear Importance Ranking by Coefficient Magnitude):
  1. Soil_Moisture                  (coef=1.042429)
  2. Temperature_C                  (coef=0.687699)
  3. Wind_Speed_kmh                 (coef=0.560858)
  4. Rainfall_mm                    (coef=0.338685)
  5. Soil_pH                        (coef=0.046769)

RECOMMENDED PREPROCESSING FOR LINEAR MODELS:
  1. StandardScaler (standard choice; RobustScaler for outlier robustness)
  2. Add Soil_Moisture² (non-linear threshold at SM≈20)
  3. Binning: SM < 20 as binary feature (captures concentration of High class)

RECOMMENDED FEATURE ENGINEERING (Interaction/Transformation):
  1. SM × Rainfall interaction (7.0× baseline High-class rate in low SM, low rain)
  2. SM × Temperature interaction (6.4× baseline in low SM, high temp)
  3. Log-scale Rainfall (high skew, wide range 0.38–2499.69)

follow_up:
- Does combining all three transformations (SM², SM<20 bin, Rainfall_log) on LR push CV above 0.75?
- Are SM × Rainfall and SM × Temperature the only high-signal interactions, or do categorical features (Region, Season) unlock better LR performance when combined with numeric transformations?
- Can Logistic Regression reach 0.80+ CV by adding target-encoding for high-cardinality categoricals and stacking with tree OOF?


## A-005
at: 2026-04-02T19:53Z
q: Does S-032's LR OOF prediction distribution show that High-class samples in the (SM<20 AND Rainfall<1000) subgroup are still systematically mispredicted, indicating that adding the explicit indicator I(SM<20 AND Rainfall<1000) as a feature would improve LR High-class recall?
verdict: rejected
conf: high
reference: experiment=S-032, knowledge=AK-009, knowledge=AK-020
evidence:
================================================================================
A-005: S-032 LR OOF — High-class recall in (SM<20 AND Rainfall<1000) subgroup
================================================================================

Dataset: 630000 rows total
Subgroup (SM<20 AND Rainfall<1000): 35069 rows (5.6%)
Outside subgroup:                   594931 rows (94.4%)

------------------------------------------------------------
OVERALL HIGH-CLASS RECALL (S-032 LR, all samples)
------------------------------------------------------------
  Total High-class samples: 21009
  High recall:              0.9208
  TP=19346, FN=1663
  FN breakdown: predicted-Low=13, predicted-Medium=1650

------------------------------------------------------------
HIGH-CLASS RECALL BY SUBGROUP
------------------------------------------------------------
  IN subgroup  (SM<20 AND Rainfall<1000):
    Total samples:        35069
    High-class samples:   6891 (19.6% prevalence)
    High recall:          0.9515
    TP=6557, FN=334
    FN breakdown: predicted-Low=0, predicted-Medium=334
  OUT subgroup (all other samples):
    Total samples:        594931
    High-class samples:   14118 (2.4% prevalence)
    High recall:          0.9059
    TP=12789, FN=1329
    FN breakdown: predicted-Low=13, predicted-Medium=1316

------------------------------------------------------------
OOF PROBABILITY ANALYSIS — High-class MISSES in subgroup
------------------------------------------------------------
  High-class misses in subgroup: 334
  Mean OOF probabilities for these misses:
    P(High): 0.2744 (median=0.2912)
    P(Low): 0.0097 (median=0.0011)
    P(Medium): 0.7158 (median=0.7026)
  Misses predicted as Low: 0 (0.0%)
  Misses predicted as Medium: 334 (100.0%)

------------------------------------------------------------
HIGH-PROB SCORE DISTRIBUTION — Hits vs Misses in subgroup
------------------------------------------------------------
  Hits  (n=6557): P(High) mean=0.9491, median=0.9878, p10=0.8455
  Misses (n=334): P(High) mean=0.2744, median=0.2912, p90=0.4580

------------------------------------------------------------
RECALL COMPARISON SUMMARY
------------------------------------------------------------
  S-032 LR overall High recall:               0.9208
  S-032 LR High recall IN subgroup (SM<20 & Rain<1000):  0.9515
  S-032 LR High recall OUT of subgroup:       0.9059
  Delta (in - out):                          +0.0457
  Fraction of all High-class FNs that fall in subgroup: 334/1663 (20.1%)

------------------------------------------------------------
FOLD-LEVEL HIGH-CLASS RECALL IN SUBGROUP
------------------------------------------------------------
  Fold 0: High-recall=0.9580 (TP=1324, FN=58, n_High=1382)
  Fold 1: High-recall=0.9521 (TP=1311, FN=66, n_High=1377)
  Fold 2: High-recall=0.9507 (TP=1330, FN=69, n_High=1399)
  Fold 3: High-recall=0.9560 (TP=1324, FN=61, n_High=1385)
  Fold 4: High-recall=0.9407 (TP=1268, FN=80, n_High=1348)

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Does adding I(SM<20 AND Rainfall<1000) as an explicit indicator on top of S-032's existing features yield a measurable CV lift (≥+0.001 balanced accuracy)?
- Are the 1329 out-of-subgroup High-class FNs concentrated in a specific feature region (e.g., SM 20–30 or Rainfall 1000–1500) that a second threshold feature could target?
- Does a polynomial or interaction feature targeting the out-of-subgroup zone (e.g., I(SM<30 AND Rainfall<1500)) improve S-032 recall for the dominant FN population?


## A-006
at: 2026-04-02T19:57Z
q: Are S-032's 1329 out-of-subgroup High-class FNs (SM>=20 OR Rainfall>=1000) concentrated in a specific feature region (e.g., SM 20-30 range, or SM>=20 AND Temperature>33) that a new threshold indicator feature could target to materially improve LR recall?
verdict: supported
conf: high
reference: experiment=S-032, knowledge=AK-023, knowledge=AK-008
evidence:
================================================================================
A-006: S-032 LR OOF — Feature clustering of out-of-subgroup High-class FNs
================================================================================

Out-of-subgroup High-class samples: 14118
  FNs (missed): 1329 (9.4%)
  TPs (correct): 12789 (90.6%)

------------------------------------------------------------
OUT-OF-SUBGROUP COMPOSITION (all High-class samples here)
------------------------------------------------------------

  Zone A: SM<20 AND Rain>=1000:
    Total rows:    85229 (13.5% of data)
    High samples:  6648 (prev=7.80%)
    FNs from here: 388 (29.2% of all out-subgroup FNs)
    TPs from here: 6260
    Recall here:   94.2%

  Zone B: SM>=20 AND Rain<1000:
    Total rows:    135400 (21.5% of data)
    High samples:  4239 (prev=3.13%)
    FNs from here: 539 (40.6% of all out-subgroup FNs)
    TPs from here: 3700
    Recall here:   87.3%

  Zone C: SM>=20 AND Rain>=1000:
    Total rows:    374302 (59.4% of data)
    High samples:  3231 (prev=0.86%)
    FNs from here: 402 (30.2% of all out-subgroup FNs)
    TPs from here: 2829
    Recall here:   87.6%

------------------------------------------------------------
SOIL MOISTURE BREAKDOWN (out-of-subgroup High-class FNs vs TPs)
------------------------------------------------------------

  Soil_Moisture buckets (among out-of-subgroup High-class samples):
  Bucket                     FN     TP     FN%     TP%  FN/(FN+TP)
  SM<20 (Rainfall>=1000)    388   6260   29.2%   48.9%        5.8%
  SM 20-25                  659   6158   49.6%   48.2%        9.7%
  SM 25-30                    2     68    0.2%    0.5%        2.9%
  SM 30-35                    5     61    0.4%    0.5%        7.6%
  SM 35-40                   15     66    1.1%    0.5%       18.5%
  SM>=40                    260    176   19.6%    1.4%       59.6%

------------------------------------------------------------
RAINFALL BREAKDOWN (out-of-subgroup High-class FNs vs TPs)
------------------------------------------------------------

  Rainfall_mm buckets (among out-of-subgroup High-class samples):
  Bucket                     FN     TP     FN%     TP%  FN/(FN+TP)
  Rain<500                  486   2637   36.6%   20.6%       15.6%
  Rain 500-1000              53   1063    4.0%    8.3%        4.7%
  Rain 1000-1500            208   3257   15.7%   25.5%        6.0%
  Rain 1500-2000            205   2643   15.4%   20.7%        7.2%
  Rain 2000-2500            377   3189   28.4%   24.9%       10.6%
  Rain>=2500                  0      0    0.0%    0.0%        0.0%

------------------------------------------------------------
TEMPERATURE BREAKDOWN (out-of-subgroup High-class FNs vs TPs)
------------------------------------------------------------

  Temperature_C buckets (among out-of-subgroup High-class samples):
  Bucket                     FN     TP     FN%     TP%  FN/(FN+TP)
  Temp<25                   338    234   25.4%    1.8%       59.1%
  Temp 25-30                 64    187    4.8%    1.5%       25.5%
  Temp 30-33                470   3219   35.4%   25.2%       12.7%
  Temp 33-36                262   3560   19.7%   27.8%        6.9%
  Temp 36-39                105   2530    7.9%   19.8%        4.0%
  Temp>=39                   90   3059    6.8%   23.9%        2.9%

------------------------------------------------------------
REGION AND CROP BREAKDOWN (out-of-subgroup High-class)
------------------------------------------------------------

  Region breakdown (among out-of-subgroup High-class samples):
  Category                      FN     TP     FN%     TP%  FN/(FN+TP)
  Central                      253   2593   19.0%   20.3%        8.9%
  East                         271   2213   20.4%   17.3%       10.9%
  North                        241   2330   18.1%   18.2%        9.4%
  South                        290   2894   21.8%   22.6%        9.1%
  West                         274   2759   20.6%   21.6%        9.0%

  Crop_Type breakdown (among out-of-subgroup High-class samples):
  Category                      FN     TP     FN%     TP%  FN/(FN+TP)
  Cotton                       269   2263   20.2%   17.7%       10.6%
  Maize                        229   2799   17.2%   21.9%        7.6%
  Potato                       214   1643   16.1%   12.8%       11.5%
  Rice                         194   1490   14.6%   11.7%       11.5%
  Sugarcane                    218   2655   16.4%   20.8%        7.6%
  Wheat                        205   1939   15.4%   15.2%        9.6%

------------------------------------------------------------
SM x TEMPERATURE CROSS-TAB (out-of-subgroup High-class FNs vs TPs)
------------------------------------------------------------
  Combo                         FN     TP     FN%     TP%  FN/(FN+TP)
  SM<25 & Temp>=33             326   8890   24.5%   69.5%        3.5%
  SM<25 & Temp<33              721   3528   54.3%   27.6%       17.0%
  SM>=25 & Temp>=33            131    259    9.9%    2.0%       33.6%
  SM>=25 & Temp<33             151    112   11.4%    0.9%       57.4%

------------------------------------------------------------
ZONE B DETAIL: SM>=20 AND Rain<1000 — SM buckets x FN/TP
------------------------------------------------------------
  SM Bucket                  FN     TP  High prev  FN/(FN+TP)
  SM 20-22                  120   1529     19.12%        7.3%
  SM 22-24                   78    857     15.80%        8.3%
  SM 24-26                  101    963     16.14%        9.5%
  SM 26-28                    1     22      0.42%        4.3%
  SM 28-30                    1     31      0.57%        3.1%
  SM 30-35                    3     60      0.45%        4.8%
  SM>=35                    235    238      0.53%       49.7%

------------------------------------------------------------
OOF PROBABILITY ANALYSIS — out-of-subgroup High-class FNs
------------------------------------------------------------
  FNs (n=1329): P(High) mean=0.2647, median=0.2742, p90=0.4688
  TPs (n=12789): P(High) mean=0.8798, median=0.9215, p10=0.6932

  Out-of-subgroup FNs predicted as:
    Low: 13 (1.0%)
    Medium: 1316 (99.0%)

------------------------------------------------------------
CANDIDATE INDICATOR EVALUATION
------------------------------------------------------------
  Candidate indicator              n_rows   n_High   High%  FNs captured    FN%
  SM in [20,30]                    110963     6887   6.21%           661  49.7%
  SM in [20,25]                     57045     6817  11.95%           659  49.6%
  SM in [20,25] & T>=33             20151     4522  22.44%           187  14.1%
  SM in [20,25] & Rain<500           4346     2534  58.31%           253  19.0%
  SM<20 & Rain>=1000                85229     6648   7.80%           388  29.2%
  SM<25 & Rain<500                  12909     7429  57.55%           546  41.1%

------------------------------------------------------------
OVERALL CONTEXT
------------------------------------------------------------
  Total High-class: 21009
  Total FNs:        1663 (7.9%)
  Total TPs:        19346 (92.1%)
  Out-subgroup FNs: 1329 = 79.9% of all FNs
  Baseline High prevalence (full dataset): 3.33%

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Does adding I(SM>=35) as an explicit indicator feature (targeting the 49.7% FN-rate SM>=35 zone) materially improve S-032 LR High-class recall (>+0.002 CV)?
- Does adding I(Temperature<25) as an explicit indicator feature (targeting the 59.1% FN-rate low-temperature zone) materially improve S-032 LR High-class recall (>+0.002 CV)?
- Is the SM>=35 AND low-temperature zone jointly capturing the same FN population, or are they independent clusters warranting separate indicators?


## A-007
at: 2026-04-02T20:06Z
q: Do the three A-006 candidate threshold indicators — I(Temperature<25), I(SM>=35), and I(SM>=25 AND Temperature<33) — have sufficient selectivity (High-class enrichment above the 3.3% baseline) within the out-of-subgroup zone to justify adding them to the S-035 feature set in a logistic regression?
verdict: rejected
conf: high
reference: experiment=S-032, knowledge=AK-024, knowledge=AK-008
evidence:
================================================================================
A-007: Selectivity of candidate threshold indicators for S-035 LR feature set
================================================================================

Dataset: 630000 rows, 21009 High-class (3.33% baseline)
Out-of-subgroup zone: 594931 rows, 14118 High-class (2.37% baseline in zone)
Full dataset baseline: 3.33%

================================================================================
SECTION 1: INDICATOR SELECTIVITY — FULL DATASET
================================================================================

Indicator selectivity on full dataset
--------------------------------------------------------------------------------------------------------------
  Indicator                              n_zone   n_High   High%  Enrichment   n_FN   n_TP  FN rate
  Baseline (3.3%)                                          3.33%       1.00×
--------------------------------------------------------------------------------------------------------------
  I(Temp<25)                             276005     1229   0.45%       0.13×    497    732    40.4%
  I(SM>=35)                              346250      517   0.15%       0.04×    275    242    53.2%
  I(SM>=25 AND Temp<33)                  320687      263   0.08%       0.02×    151    112    57.4%
  I(Temp<25 AND SM>=35)                  154792       24   0.02%       0.00×     21      3    87.5%
--------------------------------------------------------------------------------------------------------------

================================================================================
SECTION 2: INDICATOR SELECTIVITY — OUT-OF-SUBGROUP ZONE ONLY
(restricted to rows where SM>=20 OR Rainfall>=1000)
================================================================================

Indicator selectivity within out-of-subgroup zone
--------------------------------------------------------------------------------------------------------------
  Indicator                              n_zone   n_High   High%  Enrichment   n_FN   n_TP  FN rate
  Baseline (3.3%)                                          3.33%       1.00×
--------------------------------------------------------------------------------------------------------------
  I(Temp<25) in OOS                      262048      572   0.22%       0.07×    338    234    59.1%
  I(SM>=35) in OOS                       346250      517   0.15%       0.04×    275    242    53.2%
  I(SM>=25&Temp<33) in OOS               320687      263   0.08%       0.02×    151    112    57.4%
  I(Temp<25&SM>=35) in OOS               154792       24   0.02%       0.00×     21      3    87.5%
--------------------------------------------------------------------------------------------------------------

================================================================================
SECTION 3: IN-INDICATOR vs NOT-IN-INDICATOR PREVALENCE
(within out-of-subgroup zone; compares High% in zone vs complement)
================================================================================

  Indicator                              In-zone   High% IN   High% OUT  Enrichment IN  Signal useful?
                                          n_rows
  ----------------------------------------------------------------------------------------------------
  I(Temp<25)                              262048     0.218%      4.069%          0.07×  YES (depleted)
  I(SM>=35)                               346250     0.149%      5.469%          0.04×  YES (depleted)
  I(SM>=25 AND Temp<33)                   320687     0.082%      5.052%          0.02×  YES (depleted)
  I(Temp<25 AND SM>=35)                   154792     0.016%      3.202%          0.00×  YES (depleted)

================================================================================
SECTION 4: PER-INDICATOR FN/TP BREAKDOWN (S-032 OOF)
================================================================================

  Total out-of-subgroup High-class FNs (S-032): 1329
  Total out-of-subgroup High-class TPs (S-032): 12789

  Indicator: I(Temp<25)
    Zone size (out-of-subgroup):   262048 rows (44.0% of out-of-subgroup)
    High-class in zone:               572 (0.218% prevalence)
    Enrichment vs 3.3% baseline: 0.07×
    FNs in zone (S-032):              338 (25.4% of all out-subgroup FNs)
    TPs in zone (S-032):              234
    FN rate in zone:             59.1%
    Net info for LR: prev BELOW/AT baseline (depleted) → useful indicator

  Indicator: I(SM>=35)
    Zone size (out-of-subgroup):   346250 rows (58.2% of out-of-subgroup)
    High-class in zone:               517 (0.149% prevalence)
    Enrichment vs 3.3% baseline: 0.04×
    FNs in zone (S-032):              275 (20.7% of all out-subgroup FNs)
    TPs in zone (S-032):              242
    FN rate in zone:             53.2%
    Net info for LR: prev BELOW/AT baseline (depleted) → useful indicator

  Indicator: I(SM>=25 AND Temp<33)
    Zone size (out-of-subgroup):   320687 rows (53.9% of out-of-subgroup)
    High-class in zone:               263 (0.082% prevalence)
    Enrichment vs 3.3% baseline: 0.02×
    FNs in zone (S-032):              151 (11.4% of all out-subgroup FNs)
    TPs in zone (S-032):              112
    FN rate in zone:             57.4%
    Net info for LR: prev BELOW/AT baseline (depleted) → useful indicator

  Indicator: I(Temp<25 AND SM>=35)
    Zone size (out-of-subgroup):   154792 rows (26.0% of out-of-subgroup)
    High-class in zone:                24 (0.016% prevalence)
    Enrichment vs 3.3% baseline: 0.00×
    FNs in zone (S-032):               21 (1.6% of all out-subgroup FNs)
    TPs in zone (S-032):                3
    FN rate in zone:             87.5%
    Net info for LR: prev BELOW/AT baseline (depleted) → useful indicator


================================================================================
SECTION 5: VERDICT SUMMARY TABLE
================================================================================

  Baseline High%: 3.33%
  Out-of-subgroup baseline High%: 2.37%

  Indicator                            High% in zone  Enrichment   FN rate  Justify adding?
  ------------------------------------------------------------------------------------------
  I(Temp<25)                                  0.218%       0.07×     59.1% MAYBE (depleted)
  I(SM>=35)                                   0.149%       0.04×     53.2% MAYBE (depleted)
  I(SM>=25 AND Temp<33)                       0.082%       0.02×     57.4% MAYBE (depleted)
  I(Temp<25 AND SM>=35)                       0.016%       0.00×     87.5% MAYBE (depleted)

  NOTE: 'FN rate' is not the same as selectivity. An indicator can have a high FN rate
  but LOW High-class prevalence (e.g., SM>=35). High FN rate means the model fails there,
  but it does NOT mean the indicator zone is enriched for High-class samples.
  For a new indicator to help LR, its zone must have HIGH prevalence (enrichment > 1.0).

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Are the out-of-subgroup FN clusters (SM>=35, Temp<25) actually distinct populations, or do they overlap substantially (same rows)?
- Would adding a negative-signal indicator I(SM>=35) — signalling Low High-class likelihood — improve LR calibration for Medium/Low discrimination in that zone?
- Does S-035 LR already implicitly capture the SM>=35 and Temp<25 zones via SM² and Temperature terms, making explicit indicators redundant?



## A-008
at: 2026-04-02T20:21Z
q: Does target encoding (mean-encoded per fold) for the 8 categorical features yield materially higher linear model CV than OHE on the same numeric feature set (S-039: degree-2 poly on all 11 numerics), in a logistic regression framework?
verdict: rejected
conf: high
reference: experiment=S-039, knowledge=AK-019
evidence:
================================================================================
A-008: Target Encoding vs OHE for 8 Categorical Features
Numeric base: StandardScaler + PolynomialFeatures(degree=2) on all 11 numerics
Model: LogisticRegression C=1.0 balanced
================================================================================

Dataset: 630000 rows, 19 features
Categorical features (8): ['Soil_Type', 'Crop_Type', 'Crop_Growth_Stage', 'Season', 'Irrigation_Type', 'Water_Source', 'Mulching_Used', 'Region']
Numeric features (11): ['Soil_pH', 'Soil_Moisture', 'Organic_Carbon', 'Electrical_Conductivity', 'Temperature_C', 'Humidity', 'Rainfall_mm', 'Sunlight_Hours', 'Wind_Speed_kmh', 'Field_Area_hectare', 'Previous_Irrigation_mm']
Classes: ('High', 'Low', 'Medium')

Target encoding columns: 8 × 3 = 24 TE columns

================================================================================
APPROACH A: OHE (replicates S-039 at 0.893756)
================================================================================
Running 5-fold CV with OHE...

OHE fold scores:
  Fold 0: 0.891146
  Fold 1: 0.893526
  Fold 2: 0.895223
  Fold 3: 0.894664
  Fold 4: 0.894473
  Mean: 0.893806  Std: 0.001438
  Reference S-039 CV: 0.893756 (from scientist results)
  Delta from S-039: +0.000050

================================================================================
APPROACH B: Target Encoding (fold-safe, 3 classes × 8 cats = 24 TE cols)
================================================================================
Running 5-fold CV with target encoding...

TE fold scores:
  Fold 0: 0.890624
  Fold 1: 0.893253
  Fold 2: 0.894691
  Fold 3: 0.893945
  Fold 4: 0.894409
  Mean: 0.893384  Std: 0.001463

================================================================================
COMPARISON: TE vs OHE
================================================================================

  Method                                 Mean CV        Std
  -------------------------------------------------------
  OHE (replicated)                      0.893806   0.001438
  Target Encoding (fold-safe)           0.893384   0.001463
  -------------------------------------------------------
  Delta (TE - OHE replicated):          -0.000422
  Delta (TE - S-039 0.893756):          -0.000372
  Threshold for material improvement:       0.001

  Verdict: NO — TE is worse than or equal to OHE (-0.000422)

================================================================================
PER-FOLD COMPARISON
================================================================================

  Fold            OHE         TE      Delta
  ------------------------------------------
  0          0.891146   0.890624  -0.000522
  1          0.893526   0.893253  -0.000273
  2          0.895223   0.894691  -0.000532
  3          0.894664   0.893945  -0.000719
  4          0.894473   0.894409  -0.000064
  Mean       0.893806   0.893384  -0.000422

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Does adding SM², log(Rainfall), and the I(SM<20) bin on top of the full degree-2 poly (S-039 OHE) push LR CV above 0.895?
- Do the 8 categorical features add any measurable signal beyond the polynomial numeric features alone (i.e., does dropping OHE from S-039 cost > 0.001 CV)?
- Would a degree-3 polynomial on the top-4 numerics (SM, Temp, Wind, Rainfall) outperform S-039's degree-2 on all 11?


## A-009
at: 2026-04-03T06:45Z
q: Does the MLPClassifier (2-layer shallow neural net, hidden layers 64 and 32) have a structural advantage over Logistic Regression on the S-040 feature set — specifically, does it produce meaningfully different OOF predictions from LR (correlation < 0.97), suggesting it would add diversity value for ensembling even if CV score is similar?
verdict: supported
conf: high
reference: experiment=S-040, knowledge=AK-013
evidence:
================================================================================
A-009: MLP vs LR OOF Diversity on S-040 Feature Set
Feature set: poly2(11 numerics) + log1p(Rainfall) + I_SM_low + OHE(8 cats)
Model A: LogisticRegression(C=1.0, balanced, lbfgs, max_iter=2000)
Model B: MLPClassifier(hidden=(64,32), relu, max_iter=500, early_stopping=True)
================================================================================

Dataset: 630000 rows
Numeric features: 11
  After poly2: 77 features + log1p(Rainfall) + I_SM_low = 79 numeric features
Categorical features: 8 → OHE
Classes: ('High', 'Low', 'Medium') (0=High, 1=Low, 2=Medium)

Running 5-fold CV...
  Fold 0: LR=0.893122, MLP=0.955191
  Fold 1: LR=0.895732, MLP=0.948371
  Fold 2: LR=0.895627, MLP=0.955106
  Fold 3: LR=0.896154, MLP=0.955279
  Fold 4: LR=0.896401, MLP=0.955642

================================================================================
BALANCED ACCURACY (5-fold CV)
================================================================================

  Model                                  Mean CV        Std
  -------------------------------------------------------
  LR (S-040 reference=0.895614)         0.895407   0.001176
  MLP (64,32)                           0.953918   0.002779
  Delta (MLP - LR): +0.058511

  Per-fold scores:
  Fold             LR        MLP      Delta
  ------------------------------------------
  0          0.893122   0.955191  +0.062069
  1          0.895732   0.948371  +0.052639
  2          0.895627   0.955106  +0.059479
  3          0.896154   0.955279  +0.059125
  4          0.896401   0.955642  +0.059241

================================================================================
PREDICTION AGREEMENT (OOF class predictions, argmax)
================================================================================

  Agreement rate:    0.894549 (89.45%)
  Disagreement rate: 0.105451 (10.55%)
  Disagreeing rows:  66,434 of 630,000

  Disagreement breakdown (where models differ):
  True class      LR pred      MLP pred        Count
  --------------------------------------------------
  High            High         Medium          1,063
  High            Low          High                1
  High            Low          Medium             15
  High            Medium       High              494
  Low             High         Low                62
  Low             High         Medium             30
  Low             Low          Medium          1,064
  Low             Medium       Low            27,576
  Medium          High         Low                14
  Medium          High         Medium         21,453
  Medium          Low          High                1
  Medium          Low          Medium         12,231
  Medium          Medium       High              180
  Medium          Medium       Low             2,250

================================================================================
OOF PROBABILITY CORRELATION (class 0 = High)
================================================================================

  Class         Pearson r         p-value
  ----------------------------------------
  High (0)       0.730137       0.000e+00
  Low (1)        0.905983       0.000e+00
  Medium (2)     0.841969       0.000e+00

  Diversity threshold: correlation < 0.97
  High-class proba correlation: 0.730137
  Verdict: YES — correlation 0.730137 < 0.97 threshold

================================================================================
HIGH-CLASS PROBA DISTRIBUTION COMPARISON
================================================================================

  LR High proba:  mean=0.077564, std=0.214870, min=0.000000, max=0.999961
  MLP High proba: mean=0.033268, std=0.168831, min=0.000000, max=1.000000

  High-class recall: LR=0.9281, MLP=0.9010
  High-class total: 21,009
  LR correct High: 19,498, MLP correct High: 18,930

================================================================================
SUMMARY
================================================================================

  LR CV:  0.895407 ± 0.001176
  MLP CV: 0.953918 ± 0.002779
  MLP - LR delta: +0.058511

  OOF prediction agreement: 89.45%
  OOF High-class proba Pearson r: 0.730137
  OOF Low-class proba Pearson r: 0.905983
  OOF Medium-class proba Pearson r: 0.841969

  Diversity answer (corr_High < 0.97): YES — correlation 0.730137 < 0.97 threshold

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Does MLP(64,32) at 0.9539 CV hold up vs the XGBoost S-014 best (0.9709) when blended — does a simple mean ensemble of MLP+LR+XGB produce higher CV than XGB alone?
- Does the MLP retain its 0.9539 CV when trained on a larger/more regularized configuration (e.g., hidden=(128,64,32), dropout, or higher early_stopping patience)?
- Is the MLP OOF proba correlation with S-014 XGBoost also below 0.97, confirming diversity across all three model families?


## A-010
at: 2026-04-03T07:02Z
q: Do the S-045 MLP OOF predictions (0.9618 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: do the two models disagree on a material fraction of High-class samples in a way that suggests ensemble gains are possible?
verdict: rejected
conf: high
reference: experiment=S-045, experiment=S-014
evidence:
================================================================================
A-010: S-045 MLP vs S-014 XGBoost OOF High-class Diversity Analysis
Method: Load existing OOF artifacts only — no model training
S-045 path: /Users/hs/dev/AutoKaggle/artifacts/S-045/oof-preds.npy
S-014 path: /Users/hs/dev/AutoKaggle/artifacts/S-014/oof-preds.npy
================================================================================

S-045 OOF shape: (630000, 3)
S-014 OOF shape: (630000, 3)

Dataset: 630,000 rows
Classes: ('High', 'Low', 'Medium') (0=High, 1=Low, 2=Medium)
True High-class count: 21,009 (3.33%)

================================================================================
1. OVERALL PREDICTION AGREEMENT
================================================================================

  Agreement rate:    0.988021 (98.80%)
  Disagreement rate: 0.011979 (1.20%)
  Disagreeing rows:  7,546 of 630,000

================================================================================
2. HIGH-CLASS DISAGREEMENT (among true High-class samples)
================================================================================

  True High-class samples: 21,009

  S-045 High recall: 0.9382 (19,710/21,009 correct)
  S-014 High recall: 0.9500 (19,959/21,009 correct)

  Disagreement breakdown (among 21,009 true High samples):
  Category                                         Count   Fraction
  -----------------------------------------------------------------
  Both correct (both TP)                          19,606     0.9332
  S-045 correct, S-014 wrong (S-045 unique TP)       104     0.0050
  S-014 correct, S-045 wrong (S-014 unique TP)       353     0.0168
  Both wrong (both FN)                               946     0.0450
  TOTAL                                           21,009     1.0000

  S-045 wrong predictions on S-014's unique TPs:
    S-045 predicted Medium: 353 (100.0%)

  S-014 wrong predictions on S-045's unique TPs:
    S-014 predicted Medium: 104 (100.0%)

================================================================================
3. OOF PROBABILITY CORRELATION
================================================================================

  Class           Pearson r         p-value
  ------------------------------------------
  High (0)         0.960683       0.000e+00
  Low (1)          0.993842
  Medium (2)       0.987003

  S-045 High proba: mean=0.046443, std=0.186350, min=0.000000, max=1.000000
  S-014 High proba: mean=0.046160, std=0.181481, min=0.000000, max=0.999985

  Among true High samples only:
    S-045 mean High proba: 0.935640
    S-014 mean High proba: 0.944432
    Pearson r (High-only samples): 0.919484

================================================================================
4. SIMPLE AVERAGE ENSEMBLE BALANCED ACCURACY
================================================================================

  Model                                Balanced Accuracy
  -------------------------------------------------------
  S-045 MLP (standalone)                        0.961844
  S-014 XGBoost (standalone)                    0.970856
  Simple avg ensemble (S-045+S-014)             0.967859

  Ensemble lift vs S-045: +0.006015
  Ensemble lift vs S-014: -0.002997
  Ensemble lift vs best:  -0.002997

  Ensemble High-class recall: 0.9426
  S-045 High-class recall:    0.9382
  S-014 High-class recall:    0.9500

================================================================================
SUMMARY AND VERDICT
================================================================================

  Agreement rate (all classes):    98.80%
  High-class proba Pearson r:      0.960683 (threshold < 0.97)
  High-class complementary TPs:    457 (2.18% of true High)
  S-045-only unique TPs:           104 (0.50%)
  S-014-only unique TPs:           353 (1.68%)
  Avg ensemble vs best model lift: -0.002997

  Correlation below diversity threshold (0.97): True
  Meaningful complementary High-class TPs: True

  VERDICT: NO — Correlation is low but ensemble does not lift above best single model.

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Does a weighted blend (higher weight to S-014) recover the BA gap and beat S-014 standalone on High-class recall?
- Is there a model with High-class proba correlation < 0.90 vs S-014 that still achieves CV > 0.955 (e.g., CatBoost, LightGBM with different hyperparameters)?
- Does the simple average of three models (S-014 XGBoost + best LR + S-045 MLP) beat S-014 standalone BA?


## A-011
at: 2026-04-03T12:18Z
q: Do the S-052 LR OOF predictions (0.9286 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: does S-052 recover a meaningful fraction of High-class TPs that S-014 misses, suggesting ensemble value?
verdict: supported
conf: high
reference: experiment=S-052, experiment=S-014, knowledge=AK-028
evidence:
================================================================================
A-011: S-052 LR vs S-014 XGBoost OOF High-class Diversity Analysis
Method: Load existing OOF artifacts only — no model training
S-052 path: /Users/hs/dev/AutoKaggle/artifacts/S-052/oof-preds.npy
S-014 path: /Users/hs/dev/AutoKaggle/artifacts/S-014/oof-preds.npy
================================================================================

S-052 OOF shape: (630000, 3)
S-014 OOF shape: (630000, 3)

Dataset: 630,000 rows
Classes: ('High', 'Low', 'Medium') (0=High, 1=Low, 2=Medium)
True High-class count: 21,009 (3.33%)

================================================================================
1. OVERALL PREDICTION AGREEMENT
================================================================================

  Agreement rate:    0.932313 (93.23%)
  Disagreement rate: 0.067687 (6.77%)
  Disagreeing rows:  42,643 of 630,000

  Context (A-010): S-045 MLP had 98.80% agreement with S-014
  S-052 LR agreement: 93.23%  (more diverse than S-045 MLP)

================================================================================
2. HIGH-CLASS DISAGREEMENT (among true High-class samples)
================================================================================

  True High-class samples: 21,009

  S-052 High recall: 0.9474 (19,903/21,009 correct)
  S-014 High recall: 0.9500 (19,959/21,009 correct)

  Disagreement breakdown (among 21,009 true High samples):
  Category                                         Count   Fraction
  -----------------------------------------------------------------
  Both correct (both TP)                          19,619     0.9338
  S-052 correct, S-014 wrong (S-052 unique TP)       284     0.0135
  S-014 correct, S-052 wrong (S-014 unique TP)       340     0.0162
  Both wrong (both FN)                               766     0.0365
  TOTAL                                           21,009     1.0000

  Context (A-010): S-045 MLP had 104 unique TPs vs S-014's 353 unique TPs
  S-052 LR unique TPs: 284 (S-014's unique TPs: 340)

  S-052 wrong predictions on S-014's unique TPs:
    S-052 predicted Low: 2 (0.6%)
    S-052 predicted Medium: 338 (99.4%)

  S-014 wrong predictions on S-052's unique TPs:
    S-014 predicted Medium: 284 (100.0%)

================================================================================
3. OOF PROBABILITY CORRELATION
================================================================================

  Class           Pearson r         p-value
  ------------------------------------------
  High (0)         0.883404       0.000e+00
  Low (1)          0.936797
  Medium (2)       0.907629

  S-052 High proba: mean=0.062265, std=0.202211, min=0.000000, max=0.999998
  S-014 High proba: mean=0.046160, std=0.181481, min=0.000000, max=0.999985

  Among true High samples only:
    S-052 mean High proba: 0.916139
    S-014 mean High proba: 0.944432
    Pearson r (High-only samples): 0.816248

  Context (A-010): S-045 MLP had High proba Pearson r = 0.961 vs S-014
  S-052 LR High proba Pearson r: 0.883404 (more diverse than S-045 MLP)

================================================================================
4. SIMPLE AVERAGE ENSEMBLE BALANCED ACCURACY
================================================================================

  Model                                Balanced Accuracy
  -------------------------------------------------------
  S-052 LR (standalone)                         0.928573
  S-014 XGBoost (standalone)                    0.970856
  Simple avg ensemble (S-052+S-014)             0.964698

  Ensemble lift vs S-052: +0.036125
  Ensemble lift vs S-014: -0.006158
  Ensemble lift vs best:  -0.006158

  Ensemble High-class recall: 0.9505
  S-052 High-class recall:    0.9474
  S-014 High-class recall:    0.9500

  Context (A-010): S-045 MLP ensemble had lift vs S-014: -0.003000 (negative)

================================================================================
SUMMARY AND VERDICT
================================================================================

  Agreement rate (all classes):    93.23%
    vs S-045 MLP baseline:          98.80%
  High-class proba Pearson r:      0.883404 (threshold < 0.97)
    vs S-045 MLP baseline:          0.961000
  S-052 unique High TPs:           284
    vs S-045 MLP baseline:          104
  S-014 unique High TPs:           340
    vs S-045 MLP baseline:          353
  Avg ensemble vs best model lift: -0.006158
    vs S-045 MLP baseline:          -0.003000

  Correlation below diversity threshold (0.97): True
  Meaningful complementary High-class TPs: True
  More unique TPs than S-045 MLP (104): True

  VERDICT: PARTIAL YES — S-052 LR recovers more unique High TPs than S-045 MLP and has lower correlation with S-014, but simple average ensemble does not lift above best. Weighted blend or threshold optimization needed.

================================================================================
END OF ANALYSIS
================================================================================

follow_up:
- Does a weighted blend (e.g., 0.8×S-014 + 0.2×S-052) outperform S-014 standalone on OOF balanced accuracy?
- Does threshold-tuning the S-052+S-014 ensemble (optimizing the High-class decision boundary jointly) recover positive lift vs S-014?
- Is there a third model family (e.g., LightGBM, CatBoost, or a stronger MLP) with High-class proba Pearson r < 0.85 vs S-014 AND positive simple-average ensemble lift?


## A-012
at: 2026-04-04T18:05Z
q: Do the S-073 MLP ensemble OOF predictions provide enough complementary signal relative to both S-014 XGBoost and S-082 LightGBM to justify one 3-way stacker checkpoint now, specifically: are its class probabilities materially less correlated with at least one of those models than the XGB/LGBM pair are with each other, and does a simple average over S-014+S-082+S-073 avoid a meaningful regression versus the current S-083 weighted blend baseline?
verdict: rejected
conf: high
reference: Use the OOF probability artifacts for S-014, S-082, S-073, and S-083; answer factually and update knowledge only if the result is durable.
evidence:
================================================================================
A-012: S-073 complementarity vs S-014 XGBoost and S-082 LightGBM
Method: existing OOF probability artifacts only; no training
Rows: 630,000
Classes: ('High', 'Low', 'Medium')
================================================================================

Artifacts
- S-014: artifacts/S-014/oof-preds.npy
- S-073: artifacts/S-073/oof-preds.npy
- S-082: artifacts/S-082/oof-preds.npy
- S-083: artifacts/S-083/oof-preds.npy

Balanced Accuracy
- S-014: 0.970856
- S-073: 0.964422
- S-082: 0.970657
- S-083: 0.971177

Pairwise Probability Correlations
- S-014 vs S-082: High=0.994219, Low=0.998442, Medium=0.997453
- S-073 vs S-014: High=0.975485, Low=0.996188, Medium=0.991938
- S-073 vs S-082: High=0.973513, Low=0.996483, Medium=0.991981

Pairwise Argmax Agreement
- S-014 vs S-082: 0.996248
- S-073 vs S-014: 0.991835
- S-073 vs S-082: 0.991983

Correlation Delta vs S-014/S-082 Baseline for S-073 vs S-014
- High: +0.018734
- Low: +0.002254
- Medium: +0.005515

Correlation Delta vs S-014/S-082 Baseline for S-073 vs S-082
- High: +0.020706
- Low: +0.001959
- Medium: +0.005472

Ensemble Checks
- Simple average S-014 + S-082: 0.971153
- Simple average S-014 + S-082 + S-073: 0.969687
- Current S-083 weighted blend: 0.971177
- Delta (3-way avg - S-083): -0.001490
- Delta (3-way avg - 2-way avg): -0.001466

Decision Facts
- Minimum classwise correlation for S-014 vs S-082: 0.994219
- Minimum classwise correlation involving S-073: 0.973513
- 3-way average regresses vs S-083: yes

follow_up:
- Does any weighted blend that includes S-073 outperform S-083 on OOF balanced accuracy without lowering High-class recall?
- Does a learned stacker on S-014, S-082, and S-073 OOF probabilities beat S-083 after calibration control?
- Is S-073's diversity concentrated mainly in the High class rather than the Low/Medium classes?


## A-013
at: 2026-04-04T18:19Z
q: Does S-052 remain a plausible additional diversity source after S-093, specifically: are S-052's OOF probabilities still materially less correlated with S-093 than the S-014/S-082 tree pair are with each other, and does a simple average over S-093 and S-052 avoid a large regression versus S-093 alone?
verdict: rejected
conf: high
reference: Use OOF probability artifacts for S-052, S-093, S-014, and S-082. The point is to decide whether a 4-way learned stacker checkpoint is worth spending next, not to recommend submission strategy.
evidence:
================================================================================
A-013: S-052 diversity check after S-093
Method: existing OOF probability artifacts only; no training
Rows: 630,000
Classes: ('High', 'Low', 'Medium')
================================================================================

Artifacts
- S-014: artifacts/S-014/oof-preds.npy
- S-052: artifacts/S-052/oof-preds.npy
- S-082: artifacts/S-082/oof-preds.npy
- S-093: artifacts/S-093/oof-preds.npy

Balanced Accuracy
- S-014: 0.970856
- S-052: 0.928573
- S-082: 0.970657
- S-093: 0.972282
- Simple average S-093 + S-052: 0.966404
- Delta (avg - S-093): -0.005877

Pairwise Probability Correlations
- S-014 vs S-082: High=0.994219, Low=0.998442, Medium=0.997453
- S-093 vs S-052: High=0.878109, Low=0.935278, Medium=0.904854

Pairwise Argmax Agreement
- S-014 vs S-082: 0.996248
- S-093 vs S-052: 0.931716

Correlation Delta vs S-014/S-082 Baseline
- High: +0.116111
- Low: +0.063164
- Medium: +0.092598

Decision Facts
- Minimum classwise correlation for S-014 vs S-082: 0.994219
- Minimum classwise correlation for S-093 vs S-052: 0.878109
- S-093 vs S-052 less correlated than S-014 vs S-082: yes
- Simple average S-093 + S-052 regresses vs S-093: yes

follow_up:
- Does a learned 4-way stacker on S-014, S-082, S-073, and S-052 recover S-052's lower-correlation signal without the -0.005877 simple-average regression seen in S-093 + S-052?
- Is S-052's residual complementarity against S-093 concentrated mostly on High-class misses rather than across all classes?
- Do S-093 and S-052 disagree primarily on low-confidence samples where a meta-model could separate useful diversity from S-052 noise?


## A-014
at: 2026-04-04T19:11Z
q: Does adding S-052 to the S-093 stacker create a durable recovery pattern rather than noise, specifically: when comparing S-094 against S-093 on OOF predictions, does S-094 recover a meaningful number of true High cases or otherwise improve classwise correctness in a concentrated way that plausibly explains the +0.000017 balanced-accuracy lift?
verdict: rejected
conf: high
reference: Use existing OOF prediction artifacts for S-093, S-094, S-052, and only any minimum supporting artifacts needed to interpret the delta. The goal is to decide whether S-052 is still earning its slot after the S-098 S-073 ablation showed S-073 is additive.
evidence:
================================================================================
A-014: S-094 vs S-093 changed-case attribution
Method: existing OOF probability artifacts only; no training
Rows: 630,000
Classes: ('High', 'Low', 'Medium')
================================================================================

Artifacts
- S-052: artifacts/S-052/oof-preds.npy
- S-093: artifacts/S-093/oof-preds.npy
- S-094: artifacts/S-094/oof-preds.npy

Balanced Accuracy
- S-093: 0.972282
- S-094: 0.972299
- Delta (S-094 - S-093): +0.000018

Classwise Recall
- S-093: High=0.962683, Low=0.995037, Medium=0.959126
- S-094: High=0.962683, Low=0.995031, Medium=0.959184
- Delta: High=0.000000, Low=-0.000005, Medium=0.000059

Changed Argmax Rows
- Changed rows: 300 / 630000 (0.047619%)
- Wrong -> right: 156
- Right -> wrong: 144
- Wrong -> wrong: 0
- True-label mix among changed rows: High=20, Low=26, Medium=254

Changed Rows by True Class
- High: recovered=10, lost=10, net=+0
- Low: recovered=12, lost=14, net=-2
- Medium: recovered=134, lost=120, net=+14

High-Class Attribution
- High recovered by S-094: 10
- High lost by S-094: 10
- Recovered Highs where S-052 also predicted High: 0
- Lost Highs where S-052 predicted non-High: 1
- S-052 predictions on recovered Highs: High=0, Low=1, Medium=9
- S-052 predictions on lost Highs: High=9, Low=0, Medium=1

S-052 Alignment on Changed Rows
- S-052 matches S-094 on changed rows: 53
- S-052 matches S-093 on changed rows: 233
- True High: S-052 matches S-094=1, S-052 matches S-093=18
- True Low: S-052 matches S-094=13, S-052 matches S-093=13
- True Medium: S-052 matches S-094=39, S-052 matches S-093=202

Largest Changed-Case Flows
- true=Medium: High -> Medium: 125
- true=Medium: Medium -> High: 112
- true=Low: Low -> Medium: 14
- true=Low: Medium -> Low: 12
- true=High: High -> Medium: 10
- true=High: Medium -> High: 10
- true=Medium: Low -> Medium: 9
- true=Medium: Medium -> Low: 8

Decision Facts
- High recall changed: no
- Net High recoveries > 0: no
- Recovered Highs mostly supported by S-052: no
- BA lift driven mainly by Medium recall: yes

follow_up:
- If `S-094`'s tiny lift is driven almost entirely by Medium recall, does removing `S-052` but re-tuning the 3-way stacker recover the same Medium gain without the extra member?
- On the 300 rows where `S-094` and `S-093` differ, are the beneficial `Medium` corrections associated with any single base member other than `S-052`?
- Does `S-052` add value to `S-094` only through probability calibration margin shifts rather than argmax-case recovery, as measured by log-loss on the changed rows?


## A-015
at: 2026-04-04T20:06Z
q: Is the tiny S-094 over S-093 lift primarily explained by S-052's Medium-class probability signal rather than its High-class probability signal, specifically: on the rows where S-094 and S-093 disagree, does S-052 align more with the beneficial Medium corrections than with any recoveries in High?
verdict: supported
conf: high
reference: Use the existing OOF artifacts for S-052, S-093, and S-094; reuse prior changed-row context only as needed to answer this attribution question.
evidence:
================================================================================
A-015: S-052 attribution on S-094 vs S-093 changed rows
Method: existing OOF probability artifacts only; no training
Rows: 630,000
Changed rows: 300
================================================================================

Artifacts
- S-052: artifacts/S-052/oof-preds.npy
- S-093: artifacts/S-093/oof-preds.npy
- S-094: artifacts/S-094/oof-preds.npy

Balanced Accuracy
- S-093: 0.972282
- S-094: 0.972299
- Delta (S-094 - S-093): +0.000018

Classwise Recall
- S-093: High=0.962683, Low=0.995037, Medium=0.959126
- S-094: High=0.962683, Low=0.995031, Medium=0.959184
- Delta: High=0.000000, Low=-0.000005, Medium=0.000059

Changed-Row Outcome Buckets
- Beneficial Medium corrections: 134
- Harmful Medium flips: 120
- High recoveries: 10
- High losses: 10

S-052 Support for Changed-Row Buckets
- beneficial Medium corrections: count=134
  argmax_support=31 | target_prob>old_pred_prob=31 | target_prob>new_pred_prob=0
  mean_target_prob=0.309201 | mean_old_pred_prob=0.688146 | mean_new_pred_prob=0.309201
  mean_margin_vs_old=-0.378944 | mean_margin_vs_new=+0.000000
- harmful Medium flips: count=120
  argmax_support=99 | target_prob>old_pred_prob=0 | target_prob>new_pred_prob=112
  mean_target_prob=0.716391 | mean_old_pred_prob=0.716391 | mean_new_pred_prob=0.159156
  mean_margin_vs_old=+0.000000 | mean_margin_vs_new=+0.557235
- High recoveries: count=10
  argmax_support=0 | target_prob>old_pred_prob=0 | target_prob>new_pred_prob=0
  mean_target_prob=0.154338 | mean_old_pred_prob=0.742844 | mean_new_pred_prob=0.154338
  mean_margin_vs_old=-0.588505 | mean_margin_vs_new=+0.000000
- High losses: count=10
  argmax_support=9 | target_prob>old_pred_prob=0 | target_prob>new_pred_prob=9
  mean_target_prob=0.735512 | mean_old_pred_prob=0.735512 | mean_new_pred_prob=0.264430
  mean_margin_vs_old=+0.000000 | mean_margin_vs_new=+0.471081

Largest Changed-Case Flows
- true=Medium: High -> Medium: 125
- true=Medium: Medium -> High: 112
- true=Low: Low -> Medium: 14
- true=Low: Medium -> Low: 12
- true=High: High -> Medium: 10
- true=High: Medium -> High: 10
- true=Medium: Low -> Medium: 9
- true=Medium: Medium -> Low: 8

Decision Facts
- S-052 aligns more with beneficial Medium corrections than with High recoveries by argmax: yes
- S-052 target-class probability beats the old prediction more often on beneficial Medium corrections than on High recoveries: yes
- S-052 mean target-class margin vs old prediction is larger for beneficial Medium corrections than for High recoveries: yes
- S-052 gives any direct argmax support to High recoveries: no
- Changed-row evidence favors a Medium-signal explanation over a High-signal explanation: yes

follow_up:
- On the 254 true-Medium changed rows, is the net S-094 gain explained mostly by one upstream member other than `S-052` shifting the final stacker boundary?
- Does `S-052` improve changed-row log-loss for true `Medium` cases even though it also supports many harmful `Medium` flips?
- Are the 31 beneficial `Medium` corrections where `S-052` aligns concentrated in one fold or spread across all fixed folds?
