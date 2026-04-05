# Submission Ledger

Append one compact row per Kaggle submission.
Keep this ledger to public-signal essentials only; store any deeper submission notes or checks in `artifacts/<task_id>/`.

| task_id | submitted_at | cv_score | lb_score | lb_rank | status | summary |
|---------|--------------|----------|----------|---------|--------|---------|
| S-005 | 2026-04-01T22:17Z | 0.969900 | 0.96758 | 92 | scored | XGBoost baseline, calibration submission |
| S-014 | 2026-04-02T00:09Z | 0.970856 | 0.96820 | 86 | scored | XGBoost tuned (depth=5, subsample=0.8, colsample=0.8) + SM^2 |
| S-083 | 2026-04-04T16:54Z | 0.971177 | 0.96867 | 233 | scored | First positive ensemble signal; validate 0.70xS-014 XGB + 0.30xS-082 LGBM against the S-014 anchor |
| S-089 | 2026-04-04T17:50Z | 0.971927 | 0.97087 | 165 | scored | Diagnostic leaderboard probe for multinomial LR stacker on S-014+S-082 probabilities |
| S-094 | 2026-04-04T18:25Z | 0.972299 | 0.97144 | 157 | scored | Promote the strongest 4-way logit LR stacker after the S-093/S-094 third-leg and fourth-leg gains held locally |
