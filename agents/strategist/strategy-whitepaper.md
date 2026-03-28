# Strategy Whitepaper

## Current Date
March 28, 2026 (end of day 1)

## Deadline Assumption
March 31, 2026 — treating the last calendar day of the current competition month as the hard deadline.

## Days Remaining
3 (March 29, March 30, March 31)

## Current Phase
**Narrowing / Evidence Gathering**

Day 1 delivered the model-family comparison quickly and cleanly. Tree models (LGBM +0.008 LB over LR) are clearly dominant. CatBoost and LGBM are both in the shortlist. The current lane is exhausted: hyperparameter tuning, target encoding, count features, and deeper LGBM all failed to improve over the LGBM baseline. The two-component ensemble only adds +0.00064 LB because LGBM and CatBoost are highly correlated. Day 2 must answer a single question: **is there a meaningfully more orthogonal model that can be added to the ensemble, or can CatBoost be tuned to break from LGBM's error structure?**

## Submission Budget Posture
**Deliberate and tightening.** 3 of 5 March 28 slots used. Remaining budget: ~12 slots across 3 days (2 remaining today, 5 on March 29, 5 on March 30/31). Day 2 is the last day for meaningful exploration. From March 30 onward, only shortlist validation and final submission bets should consume slots.

Revised allocation:
- March 28 (today, remaining 2): hold unless a clear CV improvement appears
- March 29: up to 4 submissions — diversity experiments and best candidate validation
- March 30: 2–3 submissions — shortlist narrowing
- March 31 (deadline): 1–2 submissions — final best bet only, no experiments

## Strategic Objective
Find at least one model component that is meaningfully more orthogonal to LGBM than CatBoost currently is. The current ensemble gain (+0.00064 LB) is too small to matter. The goal for day 2 is to either:

1. Identify a more orthogonal model family (ExtraTrees / RandomForest as a direction-different variance reducer; XGBoost as a sanity check; a well-regularized logistic regression stack as a diversity component despite lower raw score), OR
2. Tune CatBoost aggressively enough that its error structure diverges from LGBM (deeper trees, lower learning rate, different border count or feature subsampling), OR
3. Build a richer feature representation that makes one tree model behave differently from the other

If none of these yield a CV gain of >=0.0005 on top of the ensemble, the strategy for March 30–31 is to lock the current best (CV 0.916476, LB 0.91390) and defend it rather than chase speculative gains.

## Recommended Allocation (Day 2)
- Orthogonal diversity experiment: **50%** (ExtraTrees or a tuned CatBoost variant as an orthogonal component)
- Ensemble reconstruction: **25%** (rebuild a 3-component or re-weighted 2-component ensemble if diversity experiment succeeds)
- Feature engineering with analyst guidance: **15%** (only if analyst identifies a concrete structural gap, e.g. interaction terms or frequency-encoded categoricals that tree models are not capturing)
- Leaderboard validation: **10%** (one submission per meaningful CV gain only)

## Immediate Guidance For The Supervisor

1. **ExtraTrees or RandomForest as diversity component.** These are direction-different from LGBM and CatBoost: they use bagging rather than boosting, and their variance reduction mechanism is orthogonal. A properly tuned ExtraTreesClassifier (n_estimators=500, max_features="sqrt", min_samples_leaf=5) is a strong candidate. If CV gains even 0.0003 when added to the ensemble, it is worth a submission. Do not expect it to beat LGBM solo — the target is ensemble diversity.

2. **Tune CatBoost for divergence, not just strength.** The day-1 CatBoost used default settings. To make it more orthogonal to LGBM, try: lower learning rate (0.03), more iterations (1500–2000), higher depth (8–10), and explicit feature subsampling (rsm=0.7). The hypothesis is that CatBoost at default settings behaves like a different skin of LGBM at default settings — both are following the same gradient contours. Making CatBoost deeper and slower may cause it to pick up different feature interactions.

3. **Consider a feature engineering pass targeted at tree diversity.** The target encoding experiment failed for solo LGBM. But target-encoded features may behave differently in CatBoost or ExtraTrees compared to in LGBM — this could be a source of ensemble divergence even if it does not help solo performance. Ask the analyst whether there are high-cardinality or structured categorical features where a different encoding would create materially different splits.

4. **XGBoost is a low-priority sanity check.** XGBoost with similar hyperparameters to LGBM will almost certainly be highly correlated. Only try it if ExtraTrees and CatBoost tuning both fail to produce meaningful ensemble gain.

5. **Logistic regression as a stack member is worth revisiting only if tree diversity fails.** LR CV is 0.9079, roughly 0.008 below LGBM. Even as a small-weight ensemble member it is probably not helpful. Do not pursue this unless all tree-family diversity approaches are exhausted.

6. **Hard gate on March 30.** If no experiment on March 29 adds >=0.0003 CV to the ensemble (on top of 0.916476), lock the current best and stop exploration. March 30 and March 31 are for confirmation and final submission selection only.

## Priority Plays From The Cookbook

- **Model-family diversification (ExtraTrees / bagging family)** — LGBM and CatBoost are both boosting-family models; a bagging-family model has structurally different error patterns; this is the highest-value diversity play available with 2 days left
- **CatBoost / native categoricals (with tuning for divergence)** — CatBoost at default is too correlated with LGBM; deeper, slower CatBoost with subsampling may diverge enough to improve ensemble gain
- **Shortlist-only ensembles late in the competition** — from March 30 onward, only ensemble the top 2–3 validated components; no new exploratory models
- **Spend submissions on signal extraction, not speculative breadth** — with ~12 slots remaining, each LB use should resolve a concrete question

## Deprioritize For Now

- **LGBM hyperparameter tuning** — thoroughly exhausted on day 1; no further gains expected
- **Target encoding on LGBM** — tried, no gain; only reconsider as a diversity feature for CatBoost or ExtraTrees
- **XGBoost solo tuning** — structurally too similar to LGBM; a low-priority sanity check at best
- **Neural networks or transformer-based models** — coordination cost and training time are too high for 2 remaining days
- **Stacked meta-learners** — deadline is too near; simple or weighted averaging is the right ensemble family
- **Feature count experiments (e.g. num_services)** — already tried, no CV gain

## Pivot Conditions

- If ExtraTrees or tuned CatBoost adds >=0.0005 CV to the ensemble above 0.916476: submit on March 29 and build a 3-component ensemble for the shortlist
- If no diversity experiment yields >=0.0003 CV gain by end of March 29: lock current best (LB 0.91390) and treat it as the primary final submission candidate
- If a new model adds strong CV but LB does not confirm (gap > 0.005 from expected): halt exploration and flag a CV/LB mismatch to the analyst
- If fold standard deviation rises above 0.0015 on any new experiment: treat the result as unreliable and do not submit

## Why

Day 1 produced a clean, well-calibrated result set. The CV/LB gap is consistently ~0.0026–0.0029 across all four submitted models — this means the 5-fold CV is a reliable proxy for LB performance. Tree models dominate decisively (+0.008 LB over LR). The ceiling appears to be somewhere around 0.916–0.917 for standard tree models on this feature set, since all tuning attempts returned to approximately 0.9158–0.9165. The only realistic path to a meaningful improvement is ensemble diversity — but the current LGBM+CatBoost pairing is highly correlated (both are gradient boosting with similar default settings), yielding only +0.00064 LB. The single most important question for day 2 is whether a more orthogonal component exists. ExtraTrees is the strongest candidate because it is structurally different (bagging vs boosting), naturally variance-reducing, and requires minimal tuning to produce a useful ensemble ingredient. A well-tuned CatBoost (slower, deeper, with subsampling) is the secondary candidate. If neither produces meaningful ensemble gain, the strategy must accept 0.91390 as the ceiling for this run and protect it through disciplined final submission selection.

---
*Refreshed: end of March 28, 2026. Based on 8 experiments (6 LGBM variants, 1 CatBoost baseline, 1 ensemble), 3 LB submissions, CV/LB gap confirmed stable.*
