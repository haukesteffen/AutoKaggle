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
