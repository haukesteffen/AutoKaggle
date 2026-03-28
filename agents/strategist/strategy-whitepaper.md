# Strategy Whitepaper

## Current Date
March 28, 2026 (end of day 1 — full evidence in)

## Deadline Assumption
March 31, 2026 — treating the last calendar day of the current competition month as the hard deadline.

## Days Remaining
3 (March 29, March 30, March 31)

## Current Phase
**Exploitation / Shortlist Building**

Day 1 exhausted every available lane: hyperparameter tuning, target encoding, interaction feature engineering, four GBDT families (LGBM, CatBoost default, CatBoost tuned, XGBoost), two bagging families (ExtraTrees, RandomForest), and three ensemble weighting schemes. The analyst confirmed that all GBDT models lie above r=0.990 OOF correlation with LGBM — they are near-redundant on this feature set. Feature engineering produced no CV gain because tree models already find those splits internally. The single new development at end-of-day is that the 3-way LGBM+CatBoost+XGBoost simple average (CV 0.916592) is the new best — a marginal +0.000062 above the weighted 2-model ensemble (CV 0.916530).

The run is now in exploitation phase. There are no unexplored model families that are both tractable and likely to add genuine diversity within the remaining budget. The strategy must shift to: **protect what we have, extract the last marginal gains from ensemble composition, and spend remaining LB slots only on well-justified bets.**

## Submission Budget Posture
**Conservative and tightening.**

- March 28 (2 remaining): Use one slot tonight to validate the 3-way ensemble (CV 0.916592) on LB. Hold the second slot unless an unexpected CV gain materialises.
- March 29 (5 slots): Reserve 2–3 slots for one round of well-scoped experiments and their LB validation. Do not chase breadth.
- March 30 (5 slots): 2 slots maximum — shortlist confirmation and one final variation.
- March 31 (5 slots): 1–2 slots only — submit the single best candidate and one insurance backup. No experiments.

Total remaining budget: 17 slots (2+5+5+5). Realistically plan to use 6–8 of them.

## Strategic Objective
**Squeeze the last marginal gains from the 3-component ensemble, then lock and protect.**

The realistic ceiling for this run appears to be approximately CV 0.9166–0.9170. The four remaining levers, in descending order of confidence:

1. **Ensemble weight optimisation** — the 3-way ensemble used simple averaging. A grid search over LGBM / CatBoost / XGBoost weights using OOF scores may yield +0.0001–0.0003 CV. Low effort, low risk, potentially one more CV tick.
2. **Neural network (MLP / TabNet)** — the only model family not yet tried. On this tabular dataset it is unlikely to exceed the GBDT ceiling, but it may be genuinely more orthogonal (r could be < 0.99 with LGBM). The cost is coordination overhead and training time. Only worth attempting on March 29 if a fast implementation is available (e.g. a scikit-learn MLPClassifier as a quick probe).
3. **Logistic regression as a small-weight stacking component** — LR solo CV is 0.9079 (~0.009 below GBDT). As a 5–10% ensemble weight it may add boundary-region diversity. The analyst noted LGBM and CatBoost disagree most on low-probability rows — LR may be more calibrated in that region. Low confidence, but low cost to test.
4. **Accept current best and stop** — if levers 1–3 all fail to produce CV >= 0.9170 or LB >= 0.9145, accept 3-way ensemble as final and spend remaining LB slots only on insurance submissions of the known best.

## Recommended Allocation (Day 2 — March 29)
- Ensemble weight optimisation (3-way grid search over OOF): **30%**
- Neural network / MLP probe (1 experiment only): **25%**
- LR as small-weight stacking component: **15%**
- LB validation of top candidates: **20%**
- Analyst diagnostics (if any new finding is needed): **10%**

## Immediate Guidance For The Supervisor

1. **Submit the 3-way ensemble tonight.** CV 0.916592 is the new best. Use one of the 2 remaining March 28 slots to get the LB score. The expected LB is approximately 0.91400–0.91410 (CV/LB gap has been stable at ~0.0026). This is the insurance anchor for the final submission.

2. **Run a 3-way weight grid search on March 29.** Use the existing OOF predictions from LGBM (cbef1de), CatBoost (81151d8), and XGBoost (16c521c). Grid-search weights in steps of 0.1 (e.g. w_lgbm + w_cb + w_xgb = 1.0). The optimised blend may recover +0.0001–0.0003 CV at essentially zero training cost. If it beats 0.916592 by more than 0.0002, submit to LB.

3. **Try a fast MLP probe on March 29 (one attempt only).** A scikit-learn MLPClassifier (2 hidden layers, 256 units, relu, adam, early stopping) trained on the ordinal-encoded feature set is a tractable 10-minute experiment. The question is not whether MLP beats GBDT solo — it almost certainly will not — but whether its OOF correlation with LGBM is below 0.99. Ask the analyst to check OOF correlation before committing a submission. Only submit if the MLP-inclusive ensemble improves CV above 0.9168.

4. **Try LR as a small-weight component (weight 0.05–0.10).** The LR OOF scores exist already (4bc520f). A 4-component blend of LGBM + CatBoost + XGBoost + LR with a 5–10% LR weight costs nothing to test offline. If CV improves above 0.9167, it is worth an LB validation slot.

5. **Hard gate: end of March 29.** If none of the above yields CV >= 0.9170 and confirmed LB >= 0.9142, lock the 3-way simple average ensemble (CV 0.916592, expected LB ~0.91405) as the final submission candidate. March 30 and 31 are for confirmation and insurance only.

6. **Do not attempt any new feature engineering.** Three separate feature engineering paths failed on day 1 (target encoding, count features, mtm_fiber interaction bins). The tree models have already learned these representations. Feature engineering is closed.

7. **Do not attempt ExtraTrees or RandomForest in ensembles.** Analyst-confirmed: ExtraTrees solo CV 0.911426, RF solo CV 0.910269. In all tested ensemble combinations, they dragged the blend below the 2-model ensemble baseline. The gap between their solo CV and the GBDT ceiling is too large for diversity to overcome.

## Priority Plays From The Cookbook

- **Shortlist-only ensembles late in the competition** — we are in this phase now; the shortlist is LGBM + CatBoost + XGBoost; no new components should be added unless an orthogonality test passes first
- **Spend submissions on signal extraction, not speculative breadth** — each remaining LB slot should answer a concrete question (does the 3-way ensemble hold on LB? does the MLP add diversity? is the optimised blend better?)
- **Reduce novelty near deadline** — March 30 onward should only touch the known shortlist
- **Prioritize reproducible high-confidence models** — the 3-way ensemble is stable (CV 0.916592, std 0.001030); it is the safe anchor

## Deprioritize For Now

- **ExtraTrees / RandomForest in any ensemble** — confirmed too weak (CV 0.910–0.911); tested and discarded
- **CatBoost tuning for divergence** — OOM at depth 8–9; depth=7 actually more correlated with LGBM (r=0.9972 vs 0.9953 default); this lane is closed
- **LGBM hyperparameter tuning** — thoroughly exhausted; all variants within ±0.0001 CV of baseline
- **Feature engineering** — three families tried (target encoding, count features, mtm_fiber interaction bins); none improved CV; the models already learn these splits
- **XGBoost solo tuning** — XGBoost baseline already in the shortlist; further XGBoost tuning would increase correlation with LGBM without meaningful CV gain
- **Neural network with long training time** — only a fast MLPClassifier probe is justified; avoid TabNet, PyTorch, or any model requiring >30 minutes to train per fold
- **Stacked meta-learners** — deadline too near; simple / weighted averaging is the right ensemble family

## Pivot Conditions

- If LB for the 3-way ensemble confirms >= 0.9141: this is the anchor; protect it as the primary final submission
- If LB for the 3-way ensemble comes back below 0.9135 (i.e. CV/LB gap widens above 0.003): flag a CV/LB mismatch to the analyst before spending more slots
- If the weight-optimised ensemble adds >= 0.0003 CV above 0.916592 and LB confirms: submit that as the new anchor
- If MLP probe passes orthogonality test (OOF r < 0.990 with LGBM) and ensemble CV >= 0.9168: submit the MLP-inclusive blend
- If all March 29 experiments fail to move CV above 0.9168: immediately enter final submission discipline mode; no new experiments on March 30 or 31

## Why

Day 1 produced exceptionally clean evidence across 25 experiments. The CV/LB gap is stable at ~0.0026 across all four scored submissions — CV is a reliable proxy for LB. The tree model ceiling on this feature set is approximately 0.9164–0.9166 for a well-tuned single model. The GBDT diversity wall has been hit: analyst-confirmed OOF correlations of r=0.9953–0.9972 across CatBoost default, CatBoost tuned, and XGBoost mean that all three boosting models are finding essentially the same prediction surface. Bagging models (ExtraTrees, RF) are genuinely more orthogonal but their solo CV is ~0.005 below the GBDT ceiling — too large a gap for diversity to overcome.

The 3-way LGBM+CatBoost+XGBoost ensemble (CV 0.916592) is the current best and the marginal gain from adding a fourth component is likely to be small. The only realistic paths to further improvement are: (a) ensemble weight optimisation using OOF (near-zero cost, bounded upside), (b) a fast MLP probe that happens to be genuinely orthogonal (uncertain, worth one experiment), or (c) accepting the current best and defending it. With 3 days and 17 slots remaining, the budget is adequate but the risk of overextending into speculative territory is real. The conservative call — submit the 3-way ensemble tonight, run two focused experiments on March 29, then lock — is the right posture.

---
*Refreshed: end of March 28, 2026 (full day 1 evidence). Based on 25 experiments, 3 LB submissions, analyst-confirmed GBDT correlation wall (all r > 0.990), and confirmed feature engineering failure across 3 families. New best: 3-way ensemble CV 0.916592.*
