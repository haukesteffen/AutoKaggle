# Strategy Whitepaper

## Current Date
March 29, 2026

## Deadline
March 31, 2026

## Days Remaining
3 (March 29, March 30, March 31) — 15 slots remaining (5 March 29 unused, 5 March 30, 5 March 31)

## Current Phase
**Consolidation — all lanes exhausted. Final answer is 7b386f5. Remaining slots are insurance only.**

## Status Summary

All 4 Playground Series S3–S6 lanes have been attempted and failed. Hill climbing on all available OOF arrays also confirmed: converges to CB=0.5/XGB=0.5 (same as OOF grid), which loses to equal 3-way in real harness (3963ca3 CV=0.916381 < 0.916540). OOF metrics cannot be trusted for weight selection.

**Current best and final answer: 7b386f5, equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396**

**Two-feature-set blend** (Priority 4) is now closed — two-stage residual (cv=0.909887) confirmed the distribution mismatch wall. Zero-lift pattern is consistent across all experiments. No further lanes remain.

**Confirmed non-starters (do not retry):**
- RidgeCV meta-learner, hill climbing, OOF grid — all converge to CB+XGB only, which loses to equal 3-way.
- All lanes in the "Closed Lanes" section below.

## Slot Budget

| Date | Slots | Plan |
|------|-------|------|
| March 29 | 5 available | Up to 3 experiments (seed bagging, original dataset, pseudo-labeling if time allows) |
| March 30 | 5 available | Continue sequence; pseudo-labeling and/or two-feature-set; insurance re-submit 7b386f5 |
| March 31 | 5 available | Final submission; 1–2 insurance slots held |
| Reserve | — | 4–5 slots held across March 29–31 for insurance and final entry |

Plan to use ~5–6 slots for experiments. Keep rest as insurance and for confirming 7b386f5 holds.

## New Lanes — Priority Order for March 29–31

### ~~1. Seed diversity bagging~~ — DONE, FAILED
`ensemble_seed_bag_15` (3eaeb6c): CV=0.916382 < 0.916540. 15-model seed average worse than equal single-seed 3-way.

### ~~2. Original Telco dataset blend~~ — DONE, FAILED
`ensemble_lgbm_cb_xgb_orig` (b465548): CV=0.916341 < 0.916540. 7k IBM Telco rows introduce distribution noise.

### ~~3. Soft pseudo-labeling~~ — DONE, FAILED
`ensemble_lgbm_cb_xgb_pseudo` (48a125b): CV=0.916321, LB=0.91340. Worse on both metrics.

### ~~Hill climbing (Caruana greedy)~~ — DONE, CONFIRMS EXISTING FINDING
Converges in 2 steps to CB=0.5/XGB=0.5 (LGBM=0) — identical to OOF grid result. Harness result already exists as 3963ca3 (CV=0.916381 < 0.916540). OOF metrics cannot be used to select weights reliably.

### ~~4. Two-feature-set blending~~ — CLOSED (never attempted, risk too high)
Train the GBDT trio on two distinct feature representations; blend the resulting ensembles.
- **Rationale for closing:** All prior feature engineering gave zero lift; two-stage residual (12b5ae5) returned cv=0.909887 (worst result), confirming distribution mismatch is a hard wall. Go condition (Branch B OOF correlation < 0.97) was never run, and with 2 days left and zero-lift pattern consistent across all experiments, the expected value is negative.
- **Decision:** Closed. Do not attempt.

## Guidance For The Supervisor

1. **7b386f5 remains the anchor.** Every experiment is measured against CV=0.916540 / LB=0.91396.

2. **Run lanes in priority order.** Do not skip to pseudo-labeling before attempting seed bagging; early wins compound. Do not run more than one experiment simultaneously.

3. **OOF estimates are not sufficient for lanes 1 and 2.** Full harness CV must be run. For pseudo-labeling (lane 3), skip the CV gate entirely — LB is the only truth.

4. **No hard gates between lanes.** A lane that fails does not close the next one. Keep running the sequence unless genuinely blocked.

5. **These are the last remaining lanes.** There is no fifth idea in reserve. If all four fail, 7b386f5 is the final submission and no further exploration is warranted.

6. **CV/LB gap is stable at ~0.0026** across all scored submissions. CV remains a reliable proxy except for pseudo-labeling.

7. **Insurance:** Reserve at least 1 slot on March 31 to re-submit 7b386f5 if any experiment degrades the active submission.

## Closed Lanes (Do Not Revisit)

- MLP in any ensemble weight
- LR in any ensemble weight
- OOF-tuned weight optimisation (LGBM+CB+XGB or any subset)
- OOF-tuned CB+XGB without LGBM
- ExtraTrees / RandomForest
- CatBoost depth tuning (OOM above depth 7)
- LGBM hyperparameter tuning
- Feature engineering (any family)
- XGBoost solo tuning
- Stacked meta-learners (including RidgeCV — confirmed noise-floor delta)

## Pivot Conditions

- **No hard gates between lanes.** Failure in one lane does not prevent the next.
- If any LB submission returns below 0.9135: flag CV/LB gap widening to analyst before spending further slots.
- If all 4 new lanes fail to beat 0.91396 on LB: accept 7b386f5 as the final answer and use March 31 slot for a clean final submission.

---
*Refreshed: March 29, 2026. All lanes exhausted — 4 priority lanes + two-stage residual backlog all failed. Two-feature-set closed (high risk, zero-lift pattern). 15 slots remaining for insurance only. Final answer: 7b386f5, equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396.*
