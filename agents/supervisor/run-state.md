# Supervisor Run State
generated_at: 2026-04-04T18:25Z
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
- total_results: 93
- scored_results: 89
- terminal_non_scored_results: 4
- best_cv: 0.972299 (S-094) | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
- recent_results:
  - S-091 | 0.972013 | Multinomial LR stacker C=4.0 on logit S-014+S-082 probs
  - S-092 | 0.963836 | Logit S-014+S-082 LR stacker with class_weight=None
  - S-093 | 0.972282 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073 probs
  - S-094 | 0.972299 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
  - S-095 | 0.972253 | Multinomial LR stacker C=8.0 on logit S-014+S-082+S-073+S-052 probs

## Analysis Summary
- knowledge_entries: 31
- findings_entries: 13
- recent_knowledge:
  - AK-028 | S-045 MLP is Too Correlated with S-014 XGBoost to Ensemble Beneficially | S-045 MLP (CV=0.9618) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
  - AK-029 | S-052 LR is More Diverse from S-014 XGBoost Than S-045 MLP Was | S-052 LR (CV=0.9286) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
  - AK-030 | S-073 Adds Diversity vs S-014/S-082 but Hurts Simple 3-Way Averaging | OOF artifact comparison across S-014 XGBoost, S-082 LightGBM, S-073 MLP ensemble, and S-083 weighted blend:
  - AK-031 | S-052 Remains Diverse Against S-093, but Naive Averaging Regresses Sharply | OOF artifact comparison across S-093 stacker, S-052 logistic regression, and the
- recent_findings:
  - A-011 | verdict=supported | conf=high | q=Do the S-052 LR OOF predictions (0.9286 CV) show meaningfully different High-class prediction patterns from S-014 XGBoost OOF predictions (0.9709), specifically: does S-052 recover a meaningful fraction of High-class TPs that S-014 misses, suggesting ensemble value?
  - A-012 | verdict=rejected | conf=high | q=Do the S-073 MLP ensemble OOF predictions provide enough complementary signal relative to both S-014 XGBoost and S-082 LightGBM to justify one 3-way stacker checkpoint now, specifically: are its class probabilities materially less correlated with at least one of those models than the XGB/LGBM pair are with each other, and does a simple average over S-014+S-082+S-073 avoid a meaningful regression versus the current S-083 weighted blend baseline?
  - A-013 | verdict=rejected | conf=high | q=Does S-052 remain a plausible additional diversity source after S-093, specifically: are S-052's OOF probabilities still materially less correlated with S-093 than the S-014/S-082 tree pair are with each other, and does a simple average over S-093 and S-052 avoid a large regression versus S-093 alone?

## Leaderboard
- submissions_total: 4
- best_lb: 0.97087 (S-089) | rank 165
- latest_submission: S-089 | 2026-04-04T17:50Z | 0.97087 | Diagnostic leaderboard probe for multinomial LR stacker on S-014+S-082 probabilities

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
