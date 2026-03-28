# Strategy Whitepaper

## Current Date
March 28–29, 2026 transition

## Deadline
March 31, 2026

## Days Remaining
3 (March 29, March 30, March 31) — 10 slots remaining

## Current Phase
**Reopened exploration — 4 untried lanes identified; attempt sequentially March 29–31**

## Status Summary

All previously known lanes are exhausted. However, research into Kaggle Playground Series S3–S6 winning solutions surfaced 4 genuinely untried techniques. These are not retreads of prior work; they operate at a different level (training data diversity, seed diversity, and test-set information reuse) rather than model architecture or ensemble weighting.

**Current best: 7b386f5, equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396 (scored March 28, 23:25)**

**Confirmed non-starters (do not retry):**
- RidgeCV meta-learner: OOF delta = +0.000077 — same noise-floor result as prior grid search. Closed.
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

### 1. Seed diversity bagging (Priority 1 — March 29)
Train each of LGBM, CatBoost, XGBoost across 5 random seeds (15 models total), then average all predictions.
- **Expected gain:** +0.0005–0.002 LB
- **Effort:** ~1h, 1 LB slot
- **Evidence:** Used by S4E8 1st-place winner (72 OOF models), NVIDIA Grandmaster Playbook
- **Risk:** Low. Pure averaging; cannot hurt unless seed variance is unusually high.
- **Go condition:** Offline harness CV clearly above 0.9166 before submitting.

### 2. Original Telco dataset blend (Priority 2 — March 29/30)
Augment training data with ~7k rows from the IBM Telco Customer Churn dataset (the original source for this Playground series).
- **Expected gain:** +0.0003–0.002 LB
- **Effort:** ~2h, 1 LB slot
- **Evidence:** Standard top-5 technique across multiple Playground seasons.
- **Risk:** Low-medium. Extra rows with slightly different distribution may hurt CV but help LB.
- **Go condition:** LB slot justified even if CV is flat; pattern is well-established.

### 3. Soft pseudo-labeling on test set (Priority 3 — March 30)
Use 7b386f5 test predictions as soft labels; retrain ensemble on combined train + soft-labeled test set.
- **Expected gain:** +0.001–0.004 LB
- **Effort:** ~3h, 1 LB slot
- **Evidence:** High-ceiling technique in multiple Playground top solutions.
- **Risk:** High uncertainty — CV is **uninformative** here (model has seen test labels during training). Only LB tells the truth.
- **Go condition:** Always spend the slot if capacity allows; CV cannot be used as a gate.

### 4. Two-feature-set blending (Priority 4 — March 30/31)
Train the GBDT trio on two distinct feature representations; blend the resulting ensembles.
- **Expected gain:** +0.001–0.003 LB
- **Effort:** ~3h, 1 LB slot
- **Evidence:** Useful when Branch B OOF correlation with Branch A is <0.97, even if solo CV does not improve.
- **Risk:** Medium. Correlation check must be done offline before spending a slot.
- **Go condition:** Run correlation check first; only submit if cross-branch OOF correlation <0.97.

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
*Refreshed: March 28–29, 2026 transition. Exploration reopened: 4 untried lanes from S3–S6 research. 10 slots remaining. Current best: 7b386f5, equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396.*
