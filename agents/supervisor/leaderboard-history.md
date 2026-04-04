# Leaderboard History

## Submission Ledger

| task_id | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|---------|--------------|----------|--------|----------|---------|-----------|
| S-005 | 2026-04-01T22:17Z | 0.969900 | scored | 0.96758 | 92 | XGBoost baseline, calibration submission |
| S-014 | 2026-04-02T00:09Z | 0.970856 | scored | 0.96820 | 86 | XGBoost tuned (depth=5, subsample=0.8, colsample=0.8) + SM² |
| S-083 | 2026-04-04T16:54Z | 0.971177 | scored | 0.96867 | 233 | First positive ensemble signal; validate 0.70×S-014 XGB + 0.30×S-082 LGBM against the S-014 anchor |
| S-089 | 2026-04-04T17:50Z | 0.971927 | scored | 0.97087 | 165 | Diagnostic leaderboard probe for multinomial LR stacker on S-014+S-082 probabilities |
| S-094 | 2026-04-04T18:25Z | 0.972299 | scored | 0.97144 | 157 | Promote the strongest 4-way logit LR stacker after the S-093/S-094 third-leg and fourth-leg gains held locally |

## Notes

- S-005 CV/LB: +0.0020 delta. S-014 CV/LB: -0.0027 delta. S-083 CV/LB: -0.0025 delta. All three submissions remain within the same <0.003 alignment band.
- S-014 improves over S-005: CV +0.000956, LB +0.00062, rank improved 92→86.
- S-083 improves over S-014: CV +0.000321, LB +0.00047. Rank fell from 86 to 233 because the public board moved between April 2 and April 4, 2026, not because the score regressed.
- S-089 improves over S-083 on both local and public metrics: CV +0.000750, LB +0.00220, and rank improved 233→165. Its CV/LB delta is -0.0011, which is tighter than prior submissions and supports the current stacking lane.
- S-094 improves over S-089 on both local and public metrics: CV +0.000372, LB +0.00057, and rank improved 165→157. Its CV/LB delta is -0.00086, the tightest alignment yet in the stacker lane.
- Week 1 day 2: EDA on interactions (A-002) led to SM² feature; XGBoost hyperparameter tuning (depth=5, regularized subsampling) yielded 0.9709 CV; analyst fold analysis (A-003) confirms exceptional stability (std=0.0006) and 95% High-class recall.
