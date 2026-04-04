# Supervisor Run State
generated_at: 2026-04-04T20:14Z
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
- total_results: 101
- scored_results: 97
- terminal_non_scored_results: 4
- best_cv: 0.972299 (S-094) | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
- recent_results:
  - S-099 | 0.963954 | Multinomial LR stacker C=4.0 class_weight=None on logit S-014+S-082+S-073 probs
  - S-100 | 0.972208 | Multinomial LR stacker C=4.0 balanced on HM/LM log-odds S-014+S-082+S-073
  - S-101 | 0.972282 | Multinomial LR C=4.0 balanced on full OVR logits S-014+S-082+S-073
  - S-102 | 0.972297 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium OVR
  - S-103 | 0.972279 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium pairwise

## Analysis Summary
- knowledge_entries: 34
- findings_entries: 16
- recent_knowledge:
  - AK-031 | S-052 Remains Diverse Against S-093, but Naive Averaging Regresses Sharply | OOF artifact comparison across S-093 stacker, S-052 logistic regression, and the
  - AK-032 | S-094's Gain Over S-093 Is Not a Durable High-Recovery Pattern | OOF comparison of S-094 (logit LR stacker with S-052 added) vs S-093:
  - AK-033 | On S-094 vs S-093 Changed Rows, S-052 Aligns with Some Beneficial Medium Corrections but with No High Recoveries | Within the 300 rows where S-094 and S-093 disagree:
  - AK-034 | S-102 Matches S-094 in CV but Not in Exact High/Changed-Row Behavior | OOF comparison of S-102 (multinomial LR on S-101 OVR logits + S-052 Medium OVR) vs S-094:
- recent_findings:
  - A-014 | verdict=rejected | conf=high | q=Does adding S-052 to the S-093 stacker create a durable recovery pattern rather than noise, specifically: when comparing S-094 against S-093 on OOF predictions, does S-094 recover a meaningful number of true High cases or otherwise improve classwise correctness in a concentrated way that plausibly explains the +0.000017 balanced-accuracy lift?
  - A-015 | verdict=supported | conf=high | q=Is the tiny S-094 over S-093 lift primarily explained by S-052's Medium-class probability signal rather than its High-class probability signal, specifically: on the rows where S-094 and S-093 disagree, does S-052 align more with the beneficial Medium corrections than with any recoveries in High?
  - A-016 | verdict=rejected | conf=high | q=Does S-102 preserve the practical behavior of S-094 closely enough to count as a credible simplified incumbent, specifically: compared with S-094, does S-102 keep balanced accuracy within 0.00001, leave High recall unchanged, and keep any changed-row differences concentrated mainly in Medium-class reallocations rather than new High-class regressions?

## Leaderboard
- submissions_total: 5
- best_lb: 0.97144 (S-094) | rank 157
- latest_submission: S-094 | 2026-04-04T18:25Z | 0.97144 | Promote the strongest 4-way logit LR stacker after the S-093/S-094 third-leg and fourth-leg gains held locally

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
