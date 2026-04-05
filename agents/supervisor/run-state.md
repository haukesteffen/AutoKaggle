# Supervisor Run State
generated_at: 2026-04-05T07:47Z
generated_by: harness.supervisor_snapshot

Compact restart context for Codex supervisor sessions. Read this before any full histories.

## Default Read Set
- `AGENTS.md`
- `agents/program.md`
- `agents/supervisor/role.md`
- this file

## Current Strategy
- current_date: April 5, 2026
- deadline_assumption: April 30, 2026, assuming the S6E4 Playground competition follows the standard month-end close.
- days_remaining: 25
- primary: Build a stronger `S-094` successor that preserves Medium lift while reducing fold-level instability and avoiding true-Medium regressions.
- secondary: Run behavior-first comparisons against `S-094`, with acceptance based on both CV improvement and cleaner classwise error shape.
- background: Keep a low-volume fallback lane for conservative de-risking variants that retain most of the `S-094` recipe.
- hold: Further analyst attribution on `S-102` and near-tie simplification work without a credible path to better Medium behavior.
- guidance:
  1. Set the next scientist cycle around one bounded objective: replace or stabilize the noisy `S-052` contribution inside the `S-094` blend while keeping the rest of the stack close enough to isolate behavioral change.
  2. Gate promotion on two conditions together: offline balanced accuracy must beat `0.972299` by a real margin or match it with clearly better true-Medium behavior, and the fold pattern must look safer than `S-102`.
  3. Use analyst capacity only after a new candidate exists and only to answer a narrow promotion question about whether the new variant's Medium gains are robust enough to justify replacing `S-094`.

## Control Files
- strategy_request: none
- scientist_task: none
- analyst_hypothesis: none

## Experiment Summary
- total_results: 102
- scored_results: 98
- terminal_non_scored_results: 4
- best_cv: 0.972299 (S-094) | Multinomial LR stacker C=4.0 on logit S-014+S-082+S-073+S-052 probs
- recent_results:
  - S-100 | 0.972208 | Multinomial LR stacker C=4.0 balanced on HM/LM log-odds S-014+S-082+S-073
  - S-101 | 0.972282 | Multinomial LR C=4.0 balanced on full OVR logits S-014+S-082+S-073
  - S-102 | 0.972297 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium OVR
  - S-103 | 0.972279 | Multinomial LR C=4.0 balanced on S-101 OVR logits + S-052 Medium pairwise
  - S-104 | 0.972271 | Multinomial LR C=4.0 balanced on S-101 OVR logits + shrunk S-052 Medium pairwise

## Analysis Summary
- knowledge_entries: 35
- findings_entries: 17
- recent_knowledge:
  - AK-032 | S-094's Gain Over S-093 Is Not a Durable High-Recovery Pattern | OOF comparison of S-094 (logit LR stacker with S-052 added) vs S-093:
  - AK-033 | On S-094 vs S-093 Changed Rows, S-052 Aligns with Some Beneficial Medium Corrections but with No High Recoveries | Within the 300 rows where S-094 and S-093 disagree:
  - AK-034 | S-102 Matches S-094 in CV but Not in Exact High/Changed-Row Behavior | OOF comparison of S-102 (multinomial LR on S-101 OVR logits + S-052 Medium OVR) vs S-094:
  - AK-035 | S-102's Harmful True-Medium Regressions Are Spread Across Folds, Not Driven by One Split | For the 82 rows where the truth is Medium, S-094 predicts Medium, and S-102 regresses to another class:
- recent_findings:
  - A-015 | verdict=supported | conf=high | q=Is the tiny S-094 over S-093 lift primarily explained by S-052's Medium-class probability signal rather than its High-class probability signal, specifically: on the rows where S-094 and S-093 disagree, does S-052 align more with the beneficial Medium corrections than with any recoveries in High?
  - A-016 | verdict=rejected | conf=high | q=Does S-102 preserve the practical behavior of S-094 closely enough to count as a credible simplified incumbent, specifically: compared with S-094, does S-102 keep balanced accuracy within 0.00001, leave High recall unchanged, and keep any changed-row differences concentrated mainly in Medium-class reallocations rather than new High-class regressions?
  - A-017 | verdict=rejected | conf=high | q=Are the harmful true-Medium changes in S-102 versus S-094 concentrated in a single fixed fold rather than spread across the cross-validation split, specifically: among the true-Medium rows that flip from Medium under S-094 to another class under S-102, does any one fold account for a clear majority of those regressions?

## Leaderboard
- submissions_total: 5
- best_lb: 0.97144 (S-094) | rank 157
- latest_submission: S-094 | 2026-04-04T18:25Z | 0.97144 | Promote the strongest 4-way logit LR stacker after the S-093/S-094 third-leg and fourth-leg gains held locally

## Reset Policy
- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.
- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.
