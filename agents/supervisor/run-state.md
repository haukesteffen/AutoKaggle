# Supervisor Run State
generated_at: 2026-04-04T19:03Z
generated_by: harness.supervisor_snapshot

Compact restart context for Codex supervisor sessions. Read this before any full histories.

## Default Read Set
- `AGENTS.md`
- `agents/program.md`
- `agents/supervisor/role.md`
- this file

## Current Strategy
- current_date: April 4, 2026
- deadline_assumption: April 30, 2026, assuming the competition deadline has not changed.
- days_remaining: 26
- primary: Exploit the validated `S-094` stacker lane with small, hypothesis-driven composition and calibration adjustments around the proven `S-091`/`S-093`/`S-094` recipe.
- secondary: Preserve leaderboard discipline by treating `S-094` as the submission-quality reference and requiring clear local evidence before spending additional April 2026 submission slots.
- background: Maintain light analyst-style scrutiny on why recovered members such as `S-073` and `S-052` add value, so future stack revisions stay selective instead of expanding blindly.
- hold: Broad base-model diversification, aggressive hyperparameter sweeps, and further `C`-increase probing on the current 4-way stacker unless new evidence contradicts `S-095`.
- guidance:
  1. For the next few checkpoints after April 4, 2026, keep the main lane tightly focused on variants that are one edit away from `S-094`: member inclusion/exclusion tests, modest calibration changes, or equivalent low-variance stacker refinements.
  2. Use `S-094` as the decision bar. If a candidate does not beat `0.972299` CV cleanly or does so only within noise, treat it as non-promotable and avoid leaderboard use.
  3. Keep quiet lanes quiet until the current stacker lane is exhausted. The wake already produced enough signal to justify depth over breadth, and `S-095` argues against spending near-term checkpoints on larger-`C` retries.

## Control Files
- strategy_request: none
- scientist_task: none
- analyst_hypothesis: none

## Experiment Summary
- total_results: 94
- scored_results: 90
- terminal_non_scored_results: 4
- best_cv: 0.972299 (S-094) | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
- recent_results:
  - S-092 | 0.963836 | Logit S-014+S-082 LR stacker with class_weight=None
  - S-093 | 0.972282 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073 probs
  - S-094 | 0.972299 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
  - S-095 | 0.972253 | Multinomial LR stacker C=8.0 on logit S-014+S-082+S-073+S-052 probs
  - S-096 | 0.972243 | Multinomial LR stacker C=2.0 on logit S-014+S-082+S-073+S-052 probs

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
- submissions_total: 5
- best_lb: 0.97144 (S-094) | rank 157
- latest_submission: S-094 | 2026-04-04T18:25Z | 0.97144 | Promote the strongest 4-way logit LR stacker after the S-093/S-094 third-leg and fourth-leg gains held locally

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
