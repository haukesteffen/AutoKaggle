# Leaderboard History

## Submission Ledger

| hash | submitted_at | cv_score | status | lb_score | lb_rank | rationale |
|------|--------------|----------|--------|----------|---------|-----------|
| 4bc520f | 2026-03-28T13:06Z | 0.907919 | scored | 0.90504 | — | LR anchor — unmodified baseline_logistic_regression |
| cbef1de | 2026-03-28T13:15Z | 0.915855 | scored | 0.91326 | — | LightGBM baseline n_estimators=500 lr=0.05 num_leaves=31 |
| 9b27313 | 2026-03-28T14:10Z | 0.916476 | scored | 0.91390 | — | Simple average ensemble LGBM+CatBoost |
| 393f8aa | 2026-03-28T~18:00Z | 0.916592 | scored | 0.50400 | — | ⚠️ BROKEN — 3-way LGBM+CatBoost+XGBoost; build_model returned fake OOF-loader, test preds were garbage |
| 7b386f5 | 2026-03-28T18:46Z | 0.916540 | scored | 0.91396 | — | ensemble_lgbm_cb_xgb_fixed equal-weight proper fit/predict — **best LB** |
| 48a125b | 2026-03-28T23:16Z | 0.916321 | scored | 0.91340 | — | pseudo-label test rows from 7b386f5 — worse on both CV and LB; lane closed |

## Notes

- CV/LB gaps (valid submissions): LR 0.00288, LGBM 0.00260, LGBM+CB 0.00258, LGBM+CB+XGB 0.00258 — gap is remarkably stable. CV is a reliable proxy for LB.
- 393f8aa LB=0.504 is NOT a real score — discard (fake OOF-loader bug).
- Best valid LB: **0.91396** (7b386f5, ensemble_lgbm_cb_xgb_fixed)
- OOF grid showed CB=0.5/XGB=0.5/LGBM=0.0 as optimal, but real training of CB+XGB only (3963ca3, cv=0.916381) scored worse than equal 3-way (7b386f5, cv=0.916540). OOF-grid weights don't transfer to real training.
- March 28 budget exhausted (5/5). March 29: 5 fresh slots.
- All post-best lanes exhausted: seed bagging (0.916382), orig blend (0.916341), pseudo-labeling (LB 0.9134), CB+XGB+MLP (0.916228), two-stage residual (0.909887) — all worse. Two-feature-set lane closed (zero-lift pattern from all prior feature engineering; too high risk with 2 days left).
- **Final answer: 7b386f5 (CV=0.916540, LB=0.91396).** Remaining slots for insurance only.
- Remaining: 5 slots March 29 (unused), 5 March 30, 5 March 31 = 15 slots. Reserve 1 slot March 31 for clean final re-submit of 7b386f5.
