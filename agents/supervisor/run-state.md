# Supervisor Run State
generated_at: 2026-04-04T20:04Z
generated_by: harness.supervisor_snapshot

Compact restart context for Codex supervisor sessions. Read this before any full histories.

## Default Read Set
- `AGENTS.md`
- `agents/program.md`
- `agents/supervisor/role.md`
- this file

## Current Strategy
- current_date: April 4, 2026
- deadline_assumption: April 30, 2026, assuming the S6E4 Playground competition follows the standard month-end close.
- days_remaining: 26
- primary: isolate the true source of S-094's 0.000017 CV edge over the S-093/S-101 family and decide whether it is structurally reproducible.
- secondary: queue one or two high-information offline variants that test interaction effects around the S-094 stack rather than further simplification-only checks.
- background: preserve submission discipline and hold S-094 as the current deployment baseline.
- hold: additional direct no-S-052 or near-duplicate simplification experiments unless they test a clearly different causal hypothesis.
- guidance:
  1. Treat S-101 as confirmation that the next lane is attribution, not more blind simplification. The highest-value question is which exact component or interaction makes S-094 better than both S-093 and S-101.
  2. Spend the next scientist cycle on one bounded ablation lane centered on S-094 versus S-093/S-101, with success defined as either reproducing the edge in a cleaner form or proving the edge is too brittle to prioritize.
  3. Use the next available submission only for a model that is either the standing S-094 baseline or a new offline winner with a clear causal story and non-trivial CV separation.

## Control Files
- strategy_request: none
- scientist_task: none
- analyst_hypothesis: none

## Experiment Summary
- total_results: 99
- scored_results: 95
- terminal_non_scored_results: 4
- best_cv: 0.972299 (S-094) | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
- recent_results:
  - S-097 | 0.971843 | Multinomial LR stacker C=4.0 on raw S-014+S-082+S-073+S-052 probs
  - S-098 | 0.972097 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-052 probs
  - S-099 | 0.963954 | Multinomial LR stacker C=4.0 class_weight=None on logit S-014+S-082+S-073 probs
  - S-100 | 0.972208 | Multinomial LR stacker C=4.0 balanced on HM/LM log-odds S-014+S-082+S-073
  - S-101 | 0.972282 | Multinomial LR C=4.0 balanced on full OVR logits S-014+S-082+S-073

## Analysis Summary
- knowledge_entries: 32
- findings_entries: 14
- recent_knowledge:
  - AK-029 | S-052 LR is More Diverse from S-014 XGBoost Than S-045 MLP Was | S-052 LR (CV=0.9286) vs S-014 XGBoost (CV=0.9709) — OOF artifact comparison:
  - AK-030 | S-073 Adds Diversity vs S-014/S-082 but Hurts Simple 3-Way Averaging | OOF artifact comparison across S-014 XGBoost, S-082 LightGBM, S-073 MLP ensemble, and S-083 weighted blend:
  - AK-031 | S-052 Remains Diverse Against S-093, but Naive Averaging Regresses Sharply | OOF artifact comparison across S-093 stacker, S-052 logistic regression, and the
  - AK-032 | S-094's Gain Over S-093 Is Not a Durable High-Recovery Pattern | OOF comparison of S-094 (logit LR stacker with S-052 added) vs S-093:
- recent_findings:
  - A-012 | verdict=rejected | conf=high | q=Do the S-073 MLP ensemble OOF predictions provide enough complementary signal relative to both S-014 XGBoost and S-082 LightGBM to justify one 3-way stacker checkpoint now, specifically: are its class probabilities materially less correlated with at least one of those models than the XGB/LGBM pair are with each other, and does a simple average over S-014+S-082+S-073 avoid a meaningful regression versus the current S-083 weighted blend baseline?
  - A-013 | verdict=rejected | conf=high | q=Does S-052 remain a plausible additional diversity source after S-093, specifically: are S-052's OOF probabilities still materially less correlated with S-093 than the S-014/S-082 tree pair are with each other, and does a simple average over S-093 and S-052 avoid a large regression versus S-093 alone?
  - A-014 | verdict=rejected | conf=high | q=Does adding S-052 to the S-093 stacker create a durable recovery pattern rather than noise, specifically: when comparing S-094 against S-093 on OOF predictions, does S-094 recover a meaningful number of true High cases or otherwise improve classwise correctness in a concentrated way that plausibly explains the +0.000017 balanced-accuracy lift?

## Leaderboard
- submissions_total: 5
- best_lb: 0.97144 (S-094) | rank 157
- latest_submission: S-094 | 2026-04-04T18:25Z | 0.97144 | Promote the strongest 4-way logit LR stacker after the S-093/S-094 third-leg and fourth-leg gains held locally

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
