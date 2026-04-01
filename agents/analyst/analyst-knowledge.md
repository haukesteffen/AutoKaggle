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
