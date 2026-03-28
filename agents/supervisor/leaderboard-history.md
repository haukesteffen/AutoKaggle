# Leaderboard History

## Submission Ledger

| hash | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|------|--------------|----------|--------|----------|---------|-----------|
| 4bc520f | 2026-03-28T13:06Z | 0.907919 | scored | 0.90504 | — | LR anchor — unmodified baseline_logistic_regression |
| cbef1de | 2026-03-28T13:15Z | 0.915855 | scored | 0.91326 | — | LightGBM baseline n_estimators=500 lr=0.05 num_leaves=31 |

## Notes

- CV/LB gaps: LR 0.00288, LGBM 0.00260 — consistent and small. CV tracking LB reliably.
- Tree models clearly dominant: +0.008 CV, +0.008 LB over LR. Remaining focus: LGBM refinement + CatBoost diversity.
- March 28 budget used: 2/5. Reserve remaining slots for meaningful jumps only.
