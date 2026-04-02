# Leaderboard History

## Submission Ledger

| task_id | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|---------|--------------|----------|--------|----------|---------|-----------|
| S-005 | 2026-04-01T22:17Z | 0.969900 | scored | 0.96758 | 92 | XGBoost baseline, calibration submission |
| S-014 | 2026-04-02T00:09Z | 0.970856 | scored | 0.96820 | 86 | XGBoost tuned (depth=5, subsample=0.8, colsample=0.8) + SM² |

## Notes

- S-005 CV/LB: +0.002 delta. S-014 CV/LB: -0.0027 delta. Both show excellent alignment (<0.003).
- S-014 improves over S-005: CV +0.000956, LB +0.00062, rank improved 92→86.
- Week 1 day 2: EDA on interactions (A-002) led to SM² feature; XGBoost hyperparameter tuning (depth=5, regularized subsampling) yielded 0.9709 CV; analyst fold analysis (A-003) confirms exceptional stability (std=0.0006) and 95% High-class recall.
