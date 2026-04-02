# Strategy Request
status: active
id: T-003
at: 2026-04-02T03:50Z
trigger: plateau_assessment

## Volume
- scientist_runs_total: 24
- scientist_runs_last_hour: 6
- analyst_sessions_total: 3
- analyst_sessions_last_hour: 0
- submissions_total: 2
- submissions_scored: 2
- submissions_pending: 0

## Coverage
- analyst_topics: class_imbalance, interaction_nonlinearity, model_strength_stability
- preprocess: StandardScaler, OrdinalEncoder, OHE, PolynomialFeatures (tested; most hurt)
- features: SM² (polynomial, works), regional/crop-specific interactions (hurt)
- models: LR, RF, LGBM, HistGBM, XGB (tuned), CatBoost (all tested with SM²)
- ensembles: none (deferred per directive)
- moonshots: none

## Current
- best_cv: 0.970856 (S-014 XGBoost)
- best_lb: 0.96820 (S-014, rank 86, excellent -0.0027 CV/LB alignment)
- active_scientist_lane: attempted feature engineering and regularization tuning; all recent experiments (S-020–S-024) underperform S-014
- active_analyst_topic: none

## Durable Facts
- S-014 is a strong local optimum (depth=5, subsample/colsample=0.8, SM² feature, n_estimators=500, lr=0.05)
- Fold stability excellent (std=0.0006, range 0.9699–0.9717)
- High-class recall 95% (17× improvement over baseline)
- Every deviation from S-014 config tested so far has hurt CV (feature engineering, regularization, n_estimators adjustment)
- CV/LB correlation is excellent (within 0.003 for both submissions)
- 29 days, 5 submissions/day, 2 of 5 submissions used today
