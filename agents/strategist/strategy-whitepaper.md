# Strategy Whitepaper

## Current Date
March 28, 2026

## Deadline Assumption
March 31, 2026 — treating the last calendar day of the current competition month as the hard deadline.

## Days Remaining
3

## Current Phase
**Bootstrap / Anchor-Finding**

This is day one of the run. No experiments have been run, no leaderboard submissions have been made, and no analyst findings exist. The first priority is to establish a reliable validation anchor so all subsequent work can be ranked confidently.

## Submission Budget Posture
**Tight.** With 3 days remaining at 5 submissions per day, the total remaining budget is at most 15 Kaggle submissions. In practice, submission slots should be treated as information resources with a high bar for use. Each submission should either validate a CV jump of meaningful size, confirm a model-family comparison, or provide late-phase signal between shortlisted candidates. Do not submit minor variants. Save at least 2 slots per day for final shortlist runs on March 30–31.

Suggested allocation across the run:
- March 28: 1–2 submissions, anchor confirmation only
- March 29: 2–3 submissions, best single-model variants
- March 30: 2–3 submissions, ensemble or shortlist confirmation
- March 31 (deadline): 1–2 submissions, final best bet only

## Strategic Objective
Reach a strong, stable single-model anchor as fast as possible, then spend most of the remaining time building one or two complementary model-family members for a lightweight ensemble. Final submission should be the highest-confidence ensemble or single model in the shortlist.

The competition is **Predict Customer Churn** (playground-series-s6e3), evaluated on **ROC-AUC**. This is a binary classification problem with a mix of numeric and categorical features. The baseline in `experiment.py` is a logistic regression pipeline with median imputation and one-hot encoding. Achieving and surpassing that anchor is the first gate.

## Recommended Allocation
- Strong single-model baselines: **40%** (logistic regression anchor + first tree model)
- Diversity-building models: **25%** (second model family, e.g. LightGBM or CatBoost)
- Ensembling: **20%** (simple average first; weighted or stacked only if time allows)
- Diagnostics / analysis: **10%** (fold stability check, CV/LB mismatch investigation if behavior is surprising)
- Leaderboard validation: **5%** (deliberate, high-bar submissions only)

## Immediate Guidance For The Supervisor
1. Direct the scientist to run the existing `baseline_logistic_regression` experiment first. This establishes the floor. Record the CV score precisely and submit to get an LB score — this is the anchor against which all future work is measured.
2. Once the logistic regression anchor is recorded, immediately direct the scientist toward a LightGBM experiment with minimal tuning. This is the most valuable information the team can have on day one: whether tree models are clearly better, roughly equal, or surprisingly worse than linear models on this churn task.
3. After those two anchors exist, ask the analyst a targeted yes/no hypothesis: does LightGBM gain meaningfully from adding interaction or target-encoded features, or does the raw feature set already capture most of the signal?
4. Do not spend submissions on hyperparameter sweeps until the model-family comparison is resolved.
5. If tree models are clearly dominant by end of day one, pivot all remaining bandwidth to LightGBM refinement and a single CatBoost diversity component. If models are roughly equivalent, build a simple average ensemble of the best available variants.

## Priority Plays From The Cookbook
- **First strong tree baseline** — no tree experiment has been run yet; this is the single highest-value next step once the linear anchor is confirmed
- **Simple averaging** — with only 3 days left there is no time for elaborate stacking; a two-model average of the best logistic regression and best LightGBM is the most realistic ensemble path
- **Fold instability investigation** — request from the analyst after first results arrive; if fold variance is high the team cannot trust CV comparisons and must resolve this before spending more submissions
- **Spend submissions on signal extraction, not speculative breadth** — the budget is tight; each LB slot should resolve a concrete question about model quality, not be spent on incremental tuning

## Deprioritize For Now
- Deep hyperparameter searches on any single model family — there is not enough time for reliable tuning cycles given the 3-day window
- Neural network or transformer-based models — tabular Playground tasks rarely reward this investment in 3 days; tree models plus ensembling is a better use of bandwidth
- Stacked meta-learners — requires stable OOF predictions and careful validation; the coordination cost is too high given the deadline
- Feature engineering for rare categorical interactions — analyst should assess whether the raw feature set is sufficient before the scientist invests here
- Preprocessing diversity experiments — only worth pursuing if the first two anchors suggest feature representation is a bottleneck

## Pivot Conditions
- If the logistic regression CV and the LightGBM CV are within 0.002 of each other, treat the task as linear-friendly and shift more budget toward ensemble diversity rather than further tree tuning
- If CV gains stop translating to LB gains after the first two submissions, halt further single-model work and immediately route an analyst hypothesis about CV/LB mismatch
- If any experiment shows fold-score standard deviation greater than 0.005, halt feature engineering and resolve the instability before continuing
- If time reaches March 30 and no ensemble has been attempted, drop all exploration work immediately and commit bandwidth to assembling the best available shortlist into a simple average
- If the current best CV exceeds 0.800 and LB confirms this, consider a CatBoost diversity run on March 29 to strengthen the ensemble before the deadline

## Why
This run starts cold: no experiments, no analyst findings, no leaderboard history. The competition is binary churn classification scored on ROC-AUC, which is a well-understood Playground Series problem type. Historical evidence from similar Playground tasks strongly suggests that gradient-boosted tree models (LightGBM, XGBoost, CatBoost) dominate on the final leaderboard, with the gap over logistic regression typically between 0.02 and 0.06 ROC-AUC. The baseline experiment in `experiment.py` provides an excellent reproducible floor via a proper sklearn Pipeline with imputation, scaling, and one-hot encoding. With only 3 days remaining, the strategy must be front-loaded: anchor fast, compare model families on day one, and spend the remaining time on the highest-confidence combination. Speculative breadth is the primary risk to avoid. The submission budget (up to 15 total, but effectively fewer to leave margin on March 31) forces deliberate LB use.

---
*Missing inputs at time of writing: `scientist-results.md` (not yet created), `analyst-findings.md` (not yet created). Strategy written from harness code, competition metadata, and cookbook alone. Refresh this whitepaper after the first two experiment results are available.*
