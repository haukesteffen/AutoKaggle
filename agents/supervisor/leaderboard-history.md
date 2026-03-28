# Leaderboard History

## Submission Ledger

| hash | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|------|--------------|----------|--------|----------|---------|-----------|
| 4bc520f | 2026-03-28T13:06Z | 0.907919 | scored | 0.90504 | — | LR anchor — unmodified baseline_logistic_regression |
| cbef1de | 2026-03-28T13:15Z | 0.915855 | scored | 0.91326 | — | LightGBM baseline n_estimators=500 lr=0.05 num_leaves=31 |
| 9b27313 | 2026-03-28T14:10Z | 0.916476 | scored | 0.91390 | — | Simple average ensemble LGBM+CatBoost |
| 393f8aa | 2026-03-28T~18:00Z | 0.916592 | scored | 0.50400 | — | ⚠️ BROKEN — 3-way LGBM+CatBoost+XGBoost; build_model returned fake OOF-loader, test preds were garbage |

## Notes

- CV/LB gaps (valid submissions): LR 0.00288, LGBM 0.00260, LGBM+CB ensemble 0.00258 — consistent. CV is a reliable proxy for LB.
- Tree models clearly dominant over LR (+0.008 LB).
- 393f8aa LB=0.504 is NOT a real score — discard. The experiment's build_model loaded precomputed OOF preds for CV but returned a nonfunctional estimator; harness test predictions were garbage (training took 0.8s instead of >10min).
- 1 submission slot remaining on March 28. Hold for fixed ensemble or weight-optimized result only.
- Day-2 priority: (1) fix 3-way ensemble with real fit/predict estimator, (2) weight grid search, (3) MLP probe.
