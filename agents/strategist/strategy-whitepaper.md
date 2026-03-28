# Strategy Whitepaper

## Current Date
March 28, 2026 (end of day 1, wake 2 — MLP result in)

## Deadline Assumption
March 31, 2026 — treating the last calendar day of the current competition month as the hard deadline.

## Days Remaining
3 (March 29, March 30, March 31)

## Current Phase
**MLP Orthogonality Verification → OOF Grid Search → Clean Ensemble Submission**

Day 1 exhausted every available GBDT lane and confirmed the diversity wall: LGBM, CatBoost, and XGBoost all land above r=0.990 OOF correlation with each other — near-redundant on this feature set. Feature engineering is closed (three families tried; tree models already find those splits).

The MLP baseline (commit 442ff2a, CV=0.911625, self-reported OOF r=0.9847 vs LGBM) is the first non-GBDT model to come in below the 0.990 threshold. This matters: if the analyst formally confirms MLP orthogonality (r < 0.990), it is the first genuinely diverse component available for blending. The self-reported r is promising but must be verified before acting on it.

The best OOF ensemble so far is CB=0.5, XGB=0.5, LGBM=0.0 (CV=0.916667, commit c4ea0d1), but that experiment has a build_model bug (fake OOF-loader) and cannot be submitted. It nonetheless confirms that LGBM adds negligible value once CB and XGB are in the blend — consistent with the GBDT correlation wall.

No LB submission has been made this wake. One March 28 slot remains.

## Submission Budget Posture
**Selective and purposeful.**

- March 28 (1 remaining): Hold for the fixed CB+XGB+MLP-inclusive blend if the analyst confirms MLP orthogonality and a clean implementation is ready. If not ready tonight, hold the slot — do not spend it on a known-buggy ensemble or a speculative experiment.
- March 29 (5 slots): Primary execution day. Use 2–3 slots: one for the proper fit/predict ensemble (CB+XGB+MLP or CB+XGB if MLP fails orthogonality), one LB validation of the winner.
- March 30 (5 slots): 2 slots maximum — shortlist confirmation and one final variation if warranted.
- March 31 (5 slots): 1–2 slots only — submit the single best candidate and one insurance backup. No new experiments.

Total remaining budget: 16 slots (1+5+5+5). Realistically plan to use 5–7 of them.

## Strategic Objective
**Confirm MLP orthogonality, build a clean proper-fit ensemble (no OOF-loader bug), optimise CB+XGB+MLP weights, and submit.**

The realistic ceiling remains approximately CV 0.9166–0.9172. The levers, updated with MLP evidence:

1. **MLP orthogonality confirmation** — analyst has posted a hypothesis; verify the OOF r formally. If r < 0.990 is confirmed, MLP is eligible for blending. This is the single most valuable open question.
2. **OOF weight grid search: CB + XGB + MLP** — once MLP orthogonality is confirmed, grid-search weights across CB / XGB / MLP (steps of 0.1, sum = 1.0) using genuine OOF predictions. LGBM can be dropped or held at 0.0 weight based on the existing evidence (CB=0.5, XGB=0.5, LGBM=0.0 was the best OOF blend). Target CV >= 0.9170.
3. **Implement a clean fit/predict ensemble** — the c4ea0d1 result is invalidated by the fake OOF-loader bug. The next ensemble must use a genuine per-fold fit/predict loop so the result is submittable. This is non-negotiable before spending an LB slot.
4. **CB + XGB fallback (no MLP)** — if MLP fails the orthogonality test or cannot be cleanly integrated, fall back to CB=0.5, XGB=0.5 with a proper implementation. CV expectation: ~0.9167 (extrapolated from c4ea0d1, bias-corrected for the OOF-loader bug).

## Day-2 Play Order (March 29)

**(a) Analyst confirms MLP OOF r.**
The analyst hypothesis is already posted. Get the formal confirmation first. Do not proceed to blend design until r is confirmed or rejected. If r < 0.990: MLP enters the shortlist. If r >= 0.990: MLP is redundant; drop it and proceed with CB+XGB only.

**(b) OOF grid search: CB + XGB + MLP (or CB + XGB).**
Grid-search weights in steps of 0.1 using the genuine OOF predictions from each model. Record the best weight vector and its CV. Compare against the 3-way simple average (CV 0.916592) and the buggy-but-informative c4ea0d1 result (CV 0.916667). If the MLP-inclusive blend beats 0.9168, it is the submission candidate.

**(c) Implement the proper fit/predict ensemble.**
Build the ensemble using a genuine per-fold fit/predict loop — no OOF-loader shortcuts. The implementation must produce predictions that can be submitted. The weight vector from step (b) is plugged in directly. This is the last engineering task before submission.

**(d) Submit.**
Use one LB slot (March 28 remaining slot if the implementation is ready tonight, otherwise first March 29 slot) to validate the clean ensemble. Expected LB range: 0.9140–0.9145 for a CV in the 0.9167–0.9172 band.

## Immediate Guidance For The Supervisor

1. **Do not spend the remaining March 28 LB slot until the clean implementation is ready.** A buggy ensemble wastes the slot. If the proper fit/predict loop cannot be completed tonight, hold the slot for March 29 morning.

2. **Wait for analyst confirmation before building the MLP blend.** The self-reported OOF r=0.9847 is promising but must be formally verified against LGBM OOF using the same fold structure. The analyst hypothesis is in-flight — let it resolve.

3. **If MLP passes: build CB + XGB + MLP ensemble with optimised weights.** Use the grid search output from step (b) above. Do not default to equal weights — the existing evidence suggests LGBM contributes little and MLP may need a non-trivial weight to provide diversity benefit.

4. **If MLP fails: build CB + XGB ensemble (equal or optimised weights).** CV expectation ~0.9167. This is still a marginal improvement over the 3-way simple average (0.916592) and avoids the LGBM dilution effect confirmed by c4ea0d1.

5. **Do not attempt any new model families.** MLP is the last candidate in the diversity pipeline. TabNet, PyTorch, or any model requiring >30 minutes per fold is out of scope given the deadline.

6. **Do not attempt any new feature engineering.** Feature engineering is closed. Tree models find the splits; no manual features have improved CV across three separate attempts.

7. **Do not use ExtraTrees or RandomForest in any ensemble.** Confirmed too weak (CV 0.910–0.911 solo); all tested blends with bagging models dragged the ensemble below the GBDT baseline.

## Priority Plays From The Cookbook

- **Orthogonality test before adding any new component** — MLP is the live test case; wait for the analyst result before committing engineering effort
- **Fix the OOF-loader bug before any LB submission** — the c4ea0d1 result is informative for weight selection but the implementation is not submittable
- **Shortlist-only ensembles late in the competition** — shortlist is now CB + XGB + MLP (pending confirmation) or CB + XGB (fallback); LGBM weight is 0.0 based on existing evidence
- **Spend submissions on signal extraction, not speculative breadth** — each remaining LB slot answers a concrete question
- **Reduce novelty near deadline** — March 30 onward touches only the confirmed shortlist

## Deprioritize For Now

- **LGBM in ensembles** — OOF evidence (c4ea0d1) shows LGBM weight 0.0 is optimal in CB+XGB blends; near-redundant with CB and XGB given confirmed r > 0.990 across all three
- **ExtraTrees / RandomForest** — confirmed too weak; tested and discarded
- **CatBoost tuning for divergence** — OOM at depth 8–9; depth=7 more correlated with LGBM; this lane is closed
- **LGBM hyperparameter tuning** — exhausted; all variants within ±0.0001 CV of baseline
- **Feature engineering** — three families tried; none improved CV; closed
- **XGBoost solo tuning** — XGBoost is in the shortlist; further tuning increases correlation with LGBM without CV gain
- **Neural network with long training time** — only the existing fast MLPClassifier (scikit-learn, 2 layers, 256 units, adam, early stopping) is in scope; no TabNet or PyTorch
- **Stacked meta-learners** — deadline too near; weighted averaging is the right ensemble family
- **LR as ensemble component** — lower priority than MLP; only revisit if MLP fails and CB+XGB fallback also underperforms

## Pivot Conditions

- If analyst confirms MLP r < 0.990: proceed with CB+XGB+MLP grid search immediately
- If analyst finds MLP r >= 0.990: MLP is redundant; proceed with CB+XGB two-component blend
- If clean CB+XGB+MLP ensemble CV >= 0.9170: submit to LB (use remaining March 28 slot or first March 29 slot)
- If clean ensemble CV falls below 0.9166: investigate whether the OOF-loader bug inflated the c4ea0d1 result; flag to analyst before spending an LB slot
- If LB for the clean ensemble comes back below 0.9135: flag CV/LB gap widening to analyst before spending further slots
- If March 29 experiments produce no CV gain above 0.9168: enter final submission discipline — no new experiments on March 30 or 31; submit the best known clean ensemble as the final candidate

## Why

Day 1 produced exceptionally clean evidence across 25 experiments. The CV/LB gap is stable at ~0.0026 across all scored submissions — CV is a reliable proxy for LB. The GBDT diversity wall is confirmed: all three boosting families are above r=0.990 OOF correlation with each other. Bagging models are more orthogonal but too weak solo. The MLP result (CV=0.911625, self-reported r=0.9847) is the first promising signal outside the GBDT family: solo CV is only ~0.005 below the GBDT ceiling (comparable to or better than bagging models) and the reported OOF correlation is comfortably below 0.990. If formally confirmed, this makes MLP the first genuinely diverse component eligible for the shortlist.

The critical path is: confirm orthogonality → grid-search weights → implement cleanly → submit. The buggy c4ea0d1 ensemble (CB=0.5, XGB=0.5, CV=0.916667) provides a useful target weight vector but cannot itself be submitted. With one March 28 slot and five March 29 slots available, there is adequate budget to execute this path without rushing or overextending. The team should keep moving through the day-2 play order without waiting for explicit permission at each step — if the analyst result comes in, proceed directly to grid search.

---
*Refreshed: end of March 28, 2026 (wake 2 — MLP result in). Based on 25+ experiments, 3+ LB submissions, analyst-confirmed GBDT correlation wall (all r > 0.990), MLP baseline completed (CV=0.911625, self-reported r=0.9847), and best OOF blend CB=0.5 XGB=0.5 LGBM=0.0 (CV=0.916667, c4ea0d1 — not submittable due to build_model bug). Analyst orthogonality hypothesis in-flight.*
