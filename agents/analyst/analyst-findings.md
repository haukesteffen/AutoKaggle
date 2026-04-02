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
