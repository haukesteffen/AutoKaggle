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
