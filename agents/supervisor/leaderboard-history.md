# Leaderboard History

## Submission Ledger

| task_id | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|---------|--------------|----------|--------|----------|---------|-----------|
| S-005 | 2026-04-01T22:17Z | 0.969900 | scored | 0.96758 | 92 | XGBoost baseline, calibration submission |

## Notes

- S-005 CV/LB correlation: +0.002 (CV slightly high). Excellent alignment; can trust local CV for model selection.
- Week 1 complete: EDA identified class imbalance (High=3.3%); 6-family base sweep (LR→RF→LGBM→HistGBM→XGB→CatBoost) shows gradient boosted trees cluster at 0.967–0.970 CV.
