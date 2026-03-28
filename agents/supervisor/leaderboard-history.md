# Leaderboard History

## Submission Ledger

| hash | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|------|--------------|----------|--------|----------|---------|-----------|
| 4bc520f | 2026-03-28T13:06Z | 0.907919 | scored | 0.90504 | — | LR anchor — unmodified baseline_logistic_regression |
| cbef1de | 2026-03-28T13:15Z | 0.915855 | scored | 0.91326 | — | LightGBM baseline n_estimators=500 lr=0.05 num_leaves=31 |
| 9b27313 | 2026-03-28T14:10Z | 0.916476 | scored | 0.91390 | — | Simple average ensemble LGBM+CatBoost |

## Notes

- CV/LB gaps: LR 0.00288, LGBM 0.00260, Ensemble 0.00258 — consistent and small. CV tracking LB reliably.
- Tree models clearly dominant over LR (+0.008 LB).
- LGBM and CatBoost are highly correlated: ensemble only adds +0.00064 LB over LGBM alone.
- Current lane exhausted: hyperparameter tuning, target encoding, deeper LGBM all showed no CV gain.
- March 28 budget used: 3/5. 2 remaining today — hold for end-of-day if a better result appears.
- Day-2 priority: seek more orthogonal model component or better features to improve ensemble diversity.
