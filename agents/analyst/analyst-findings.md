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
