# Strategy Whitepaper

## Current Date
March 28/29, 2026 (end of March 28 — all 5 slots used; March 29 opens fresh)

## Deadline Assumption
March 31, 2026 — treating the last calendar day of the current competition month as the hard deadline.

## Days Remaining
3 (March 29, March 30, March 31)

## Current Phase
**Consolidation — all major lanes exhausted; optimising around the confirmed best ensemble**

Day 1 exhausted every available GBDT lane and confirmed the diversity wall: LGBM, CatBoost, and XGBoost all land above r=0.990 OOF correlation with each other — near-redundant on this feature set. Feature engineering is closed (three families tried; tree models already find those splits).

The MLP lane is now fully closed. Despite genuine OOF orthogonality (r=0.985 vs LGBM), the MLP solo CV of 0.911 is too far below the GBDT ceiling to contribute net positive signal to the ensemble. The full grid search (CB=0.5/XGB=0.4/MLP=0.1, OOF estimate 0.916575) came in at actual harness CV=0.916228 — worse than the equal 3-way GBDT blend. OOF-grid weights do not transfer reliably to real training; diversity alone is not sufficient when the solo gap is ~0.005.

The current best result is 7b386f5 (equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396). This is the new anchor.

All March 28 slots have been used.

## Submission Budget Posture
**Conservative — protect the confirmed best, spend remaining slots on signal only.**

- March 28: all 5 slots used.
- March 29 (5 slots): Use at most 2–3. One slot for the single most promising remaining experiment (OOF weight optimisation for LGBM+CB+XGB, if it shows CV improvement offline). One insurance resubmission of 7b386f5 if needed. No more than 3 LB probes.
- March 30 (5 slots): 1–2 slots maximum. Only if March 29 produces a new CV leader worth validating.
- March 31 (5 slots): 1–2 slots only — submit the single best candidate and one insurance backup. No new experiments.

Total remaining budget: 15 slots (5+5+5). Realistically plan to use 3–5 of them.

## Strategic Objective
**Defend LB=0.91396 and extract any remaining marginal CV gain from weight optimisation on the confirmed shortlist (LGBM+CB+XGB).**

The realistic ceiling is approximately CV 0.9166–0.9168. All major levers have been pulled. The only remaining question is whether optimised non-equal weights on LGBM+CB+XGB can beat equal-weight by a meaningful margin. Expected upside is less than 0.0001 CV. If the grid search comes up empty, 7b386f5 is the final candidate.

Remaining options, in confidence order:

1. **Optimised LGBM+CB+XGB weights (OOF grid search, all-positive weights)** — grid-search weights in steps of 0.05 or 0.1 over the three GBDT models using genuine OOF predictions. This is offline-only work; spend no LB slot unless the offline CV clearly exceeds 0.9167 (> +0.0003 over current best). Expected upside: < 0.0001 CV. Low priority but essentially free to run.

2. **LR as tiny ensemble weight (0.05)** — very low confidence. MLP at 0.10 weight already hurt despite confirmed orthogonality (r=0.985). LR is even weaker solo and no more orthogonal. Only attempt if GBDT weight optimisation also fails and the team needs a final experiment to close out the run.

3. **Accept 7b386f5 as final** — the most likely outcome. Equal-weight LGBM+CB+XGB (CV=0.916540, LB=0.91396) has beaten every alternative tried. Spend March 29–31 on insurance submissions only: resubmit 7b386f5 once per day as a hedge against any late scoring corrections.

## March 29 Play Order

**(a) Run OOF weight grid search offline (no LB slot).**
Grid-search weights over LGBM/CB/XGB in steps of 0.05 or 0.1, using genuine OOF predictions from commit 7b386f5's fold structure. Record the best weight vector and its offline CV. If the best offline CV exceeds 0.9167 by more than 0.0002, it is a candidate for one LB submission.

**(b) Decide: submit or stand pat.**
If the grid search does not clearly beat 0.9167 offline, do not spend an LB slot — 7b386f5 is the final candidate. If it does beat 0.9167 offline, submit one LB probe on March 29.

**(c) Insurance submission (optional).**
If no new experiment is worth submitting, use one March 29 slot to resubmit 7b386f5 as an insurance copy. This protects against any system anomaly on the original submission.

## Immediate Guidance For The Supervisor

1. **7b386f5 (equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396) is the anchor.** No experiment that does not clearly beat this offline should get an LB slot.

2. **MLP is closed. Do not revisit it.** The ensemble test is definitive: adding MLP at any tested weight (including 10%) reduces harness CV. Diversity is not enough when the solo gap is 0.005. The MLP lane is exhausted.

3. **OOF-grid weights do not reliably transfer to harness training.** This was confirmed by ensemble_cb_xgb_mlp_fixed (OOF estimate 0.916575, actual CV 0.916228) and ensemble_cb_xgb_fixed (OOF-tuned weights, CV 0.916381 — worse than equal 3-way). Any future weight optimisation must be validated with the full harness CV before spending an LB slot.

4. **Do not attempt any new model families.** All non-GBDT lanes are closed. The GBDT diversity wall is confirmed at r > 0.990. The only open question is weight optimisation within the existing shortlist.

5. **Do not attempt any new feature engineering.** Three families tried; none improved CV; closed.

6. **Do not use ExtraTrees or RandomForest in any ensemble.** Confirmed too weak (CV 0.910–0.911 solo).

7. **If the March 29 weight grid search produces no CV gain: treat 7b386f5 as final.** Spend March 30 and 31 on insurance submissions only. Do not invent new experiments to fill slots.

## Priority Plays From The Cookbook

- **Offline validation before any LB slot** — OOF-grid transfer failures have now happened twice; always confirm harness CV before submitting
- **Shortlist-only ensembles late in the competition** — shortlist is LGBM + CB + XGB only; no new components
- **Spend submissions on signal extraction, not speculative breadth** — each remaining LB slot must answer a concrete question with a clear expected CV range
- **Reduce novelty near deadline** — March 30 onward touches only 7b386f5 or a confirmed CV improvement over it

## Deprioritize For Now

- **MLP in any ensemble** — CLOSED. Diversity does not overcome the 0.005 solo CV gap. Adding MLP at 10% weight reduced harness CV by 0.0003 vs the equal 3-way GBDT blend.
- **OOF-tuned CB+XGB (no LGBM)** — CLOSED. CB=0.5, XGB=0.5 gave CV=0.916381 — worse than equal 3-way including LGBM.
- **ExtraTrees / RandomForest** — confirmed too weak; tested and discarded
- **CatBoost tuning for divergence** — OOM at depth 8–9; depth=7 more correlated with LGBM; closed
- **LGBM hyperparameter tuning** — exhausted; all variants within ±0.0001 CV of baseline
- **Feature engineering** — three families tried; none improved CV; closed
- **XGBoost solo tuning** — XGBoost is in the shortlist; further tuning increases correlation without CV gain
- **LR as ensemble component** — very low confidence; MLP at 10% already hurt; LR is not stronger. Only as a last-resort experiment after all other options are exhausted.
- **Stacked meta-learners** — deadline too near; weighted averaging is the right ensemble family
- **Any model requiring >30 minutes per fold** — out of scope given deadline

## Pivot Conditions

- If OOF weight grid search for LGBM+CB+XGB shows offline CV >= 0.9170: build a clean ensemble with those weights and submit one LB probe on March 29
- If OOF weight grid search shows no improvement over 0.9167: accept 7b386f5 as final; move to insurance-only posture for March 30–31
- If LR experiment (last resort) offline CV beats 0.9167 clearly: submit one LB probe, otherwise drop
- If any LB submission comes back below 0.9135: flag CV/LB gap widening to analyst before spending further slots
- If March 29 produces no CV gain above 0.9167: enter final submission discipline — no new experiments on March 30 or 31; submit 7b386f5 as the final candidate

## Why

All 5 March 28 slots are spent. The team has now exhausted every major strategy lane: feature engineering (3 families, all closed), GBDT solo tuning (all variants within ±0.0001), bagging models (too weak), MLP (solo CV gap too large despite confirmed orthogonality), OOF-tuned CB+XGB (worse than equal 3-way), and MLP-inclusive blend (worse than equal 3-way despite OOF estimate suggesting otherwise). The equal-weight LGBM+CB+XGB ensemble (7b386f5) has beaten every alternative and is now the confirmed best.

The CV/LB gap is stable at ~0.0026 across all scored submissions — CV is a reliable proxy for LB. The GBDT diversity wall is confirmed: all three boosting families are above r=0.990 OOF correlation. The MLP orthogonality test (r=0.985) proved that correlation reduction alone is not enough — the solo CV gap of 0.005 is decisive.

The remaining upside is small. Weight optimisation within LGBM+CB+XGB is the only surviving experiment with any theoretical basis, and the expected gain is less than 0.0001 CV. The team should run this offline, evaluate the result honestly, and if it does not beat 0.9167 clearly, commit to 7b386f5 as the final answer. The LB=0.91396 is a strong result given the exhausted search space.

---
*Refreshed: end of March 28 / start of March 29, 2026 (all 5 March 28 slots used). Based on 30+ experiments, 5 LB submissions, confirmed GBDT correlation wall (all r > 0.990), MLP lane closed (CV=0.911, diversity insufficient), OOF weight transfer failures confirmed (ensemble_cb_xgb_mlp_fixed, ensemble_cb_xgb_fixed). Current best: 7b386f5, equal-weight LGBM+CB+XGB, CV=0.916540, LB=0.91396.*
