# Supervisor Run State
generated_at: 2026-04-04T18:03Z
generated_by: harness.supervisor_snapshot

Compact restart context for Codex supervisor sessions. Read this before any full histories.

## Default Read Set
- `AGENTS.md`
- `agents/program.md`
- `agents/supervisor/role.md`
- this file

## Current Strategy
- current_date: April 4, 2026
- deadline_assumption: April 30, 2026, assuming the S6E4 competition closes on April 30, 2026 and the current run should optimize for the remaining 26-day window.
- days_remaining: 26
- primary: Extend the multinomial LR stacker family in a narrow, high-signal way that preserves comparability with S-089 and S-090.
- secondary: Run one complementary third-leg search to test whether the stacker lane is missing an orthogonal source of lift.
- background: Keep submission discipline tight and use leaderboard slots only for changes that beat the current stacker reference by a credible margin.
- hold: Broad baseline rework, diffuse model-family exploration, and any work that breaks comparability with the current stacker evidence.
- guidance:
  1. Through April 6, 2026, prioritize one or two tightly scoped stacker-family checkpoints around the S-090 recipe so the run can determine whether the 0.971946 CV edge is reproducible and large enough to justify a submission.
  2. In parallel or immediately after, allocate exactly one scientist checkpoint to a complementary third-leg search that is explicitly judged on incremental value relative to the current stacker family, not on standalone novelty.
  3. Do not spend a leaderboard submission on S-090-class movement alone unless a follow-up checkpoint shows clearer separation above 0.971946 CV or the candidate adds a distinct ensemble leg that changes portfolio risk versus S-089.

## Control Files
- strategy_request: none
- scientist_task: none
- analyst_hypothesis: none

## Experiment Summary
- total_results: 88
- scored_results: 84
- terminal_non_scored_results: 4
- best_cv: 0.971946 (S-090) | Multinomial LR stacker C=4.0 on S-014+S-082 probs
- recent_results:
  - S-086 | 0.969934 | HistGBM max_iter=1500 lr=0.02 max_leaf_nodes=15 min_samples_leaf=50 l2_reg=0.1 class_weight=balanced, SM²+OrdinalEncoder — tuned toward LGBM params; 0.969934 close to S-018 (0.969459) but below XGB/LGBM best; note subsample not available in sklearn HistGBM, removed; marginal improvement over S-018 (+0.000475) insufficient for 3-way blend at current best 0.971177
  - S-087 | 0.971124 | Weighted blend XGB+LGBM+HistGBM: sweep [(0.6,0.3,0.1),(0.6,0.25,0.15),(0.5,0.35,0.15),(0.55,0.3,0.15),(0.65,0.25,0.10)] on S-014/S-082/S-086 OOF; best at (0.55,0.30,0.15), slightly below S-083 (0.971177)
  - S-088 | 0.971161 | Fine XGB+LGBM blend sweep on S-014/S-082 OOF over alpha=[0.64,0.66,0.68,0.69,0.70,0.71,0.72,0.74,0.76]; near-anchor search stayed just below S-083
  - S-089 | 0.971927 | Multinomial LR stacker on S-014+S-082 OOF/test probs
  - S-090 | 0.971946 | Multinomial LR stacker C=4.0 on S-014+S-082 probs

## Analysis Summary
- knowledge_entries: 29
- findings_entries: 11
- recent_knowledge:
  - AK-025 | Candidate Threshold Indicators from A-006 Are DEPLETED Zones (Not Enriched) | The three A-006 candidate indicators are in heavily depleted High-class zones, not enriched ones:
  - AK-027 | MLP(64,32) is Strongly Diverse from LR on S-040 Feature Set | MLPClassifier(hidden=(64,32), relu, max_iter=500, early_stopping=True) on the S-040 feature set:
  - AK-028 | S-045 MLP is Too Correlated with S-014 XGBoost to Ensemble Beneficially | S-045 MLP (CV=0.9618) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
  - AK-029 | S-052 LR is More Diverse from S-014 XGBoost Than S-045 MLP Was | S-052 LR (CV=0.9286) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
- recent_findings:
  - A-009 | verdict=supported | conf=high | q=Does the MLPClassifier (2-layer shallow neural net, hidden layers 64 and 32) have a structural advantage over Logistic Regression on the S-040 feature set — specifically, does it produce meaningfully different OOF predictions from LR (correlation < 0.97), suggesting it would add diversity value for ensembling even if CV score is similar?
  - A-010 | verdict=rejected | conf=high | q=Do the S-045 MLP OOF predictions (0.9618 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: do the two models disagree on a material fraction of High-class samples in a way that suggests ensemble gains are possible?
  - A-011 | verdict=supported | conf=high | q=Do the S-052 LR OOF predictions (0.9286 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: does S-052 recover a meaningful fraction of High-class TPs that S-014 misses, suggesting ensemble value?

## Leaderboard
- submissions_total: 4
- best_lb: 0.97087 (S-089) | rank 165
- latest_submission: S-089 | 2026-04-04T17:50Z | 0.97087 | Diagnostic leaderboard probe for multinomial LR stacker on S-014+S-082 probabilities

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
