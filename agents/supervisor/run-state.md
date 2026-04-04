# Supervisor Run State
generated_at: 2026-04-04T19:16Z
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
- primary: Re-anchor the mainline around the `S-093` structure and test whether `S-073` can be retained without relying on `S-052`.
- secondary: Preserve `S-094` as the incumbent reference until a cleaner 3-way-plus-`S-073` variant either matches or fails clearly.
- background: Keep a small amount of attention on submission readiness and tie-break logic if multiple variants stay within roughly `0.00002` CV.
- hold: Additional local `C` tuning, no-logit variants, and further effort to justify `S-052` as a required durable member.
- guidance:
  1. Make the next checkpoint a narrow structural refinement family centered on `S-093` plus `S-073`, with the explicit goal of separating the value of `S-073` from the now-weakened `S-052` story.
  2. Treat `S-093` as the practical mainline for decision-making unless a low-variance follow-up reproduces the `S-094` edge without needing `S-052`; the current `0.000017` gap is too small to justify complexity by itself.
  3. Use the following checkpoint after that to decide promotion policy: if a simplified variant lands at or above the `S-093`/`S-094` band, promote simplicity; if not, retain `S-094` as the leaderboard-facing incumbent while freezing further family-local tweaks.

## Control Files
- strategy_request: none
- scientist_task: none
- analyst_hypothesis: none

## Experiment Summary
- total_results: 97
- scored_results: 93
- terminal_non_scored_results: 4
- best_cv: 0.972299 (S-094) | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
- recent_results:
  - S-095 | 0.972253 | Multinomial LR stacker C=8.0 on logit S-014+S-082+S-073+S-052 probs
  - S-096 | 0.972243 | Multinomial LR stacker C=2.0 on logit S-014+S-082+S-073+S-052 probs
  - S-097 | 0.971843 | Multinomial LR stacker C=4.0 on raw S-014+S-082+S-073+S-052 probs
  - S-098 | 0.972097 | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-052 probs
  - S-099 | 0.963954 | Multinomial LR stacker C=4.0 class_weight=None on logit S-014+S-082+S-073 probs

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
