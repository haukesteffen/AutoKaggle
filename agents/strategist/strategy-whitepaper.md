# Strategy Whitepaper

## Current Date
April 5, 2026

## Deadline Assumption
April 30, 2026, assuming the S6E4 Playground competition follows the standard month-end close.

## Days Remaining
25

## Read
The run is near a local CV ceiling: `S-101`, `S-102`, and `S-103` all fail to exceed `S-094` despite being close. Recent analyst work removes the easiest simplification path by showing `S-102` is not a safe replacement and that its Medium regressions are distributed rather than isolated to one fold. Current evidence still supports `S-052` as a useful but unstable contributor inside `S-094`, so the highest-value lane is controlled replacement or stabilization of that Medium-oriented edge, not more attribution cleanup and not leaderboard probing.

## Emphasis
Primary: Build a stronger `S-094` successor that preserves Medium lift while reducing fold-level instability and avoiding true-Medium regressions.
Secondary: Run behavior-first comparisons against `S-094`, with acceptance based on both CV improvement and cleaner classwise error shape.
Background: Keep a low-volume fallback lane for conservative de-risking variants that retain most of the `S-094` recipe.
Hold: Further analyst attribution on `S-102` and near-tie simplification work without a credible path to better Medium behavior.

## Guidance For The Supervisor
1. Set the next scientist cycle around one bounded objective: replace or stabilize the noisy `S-052` contribution inside the `S-094` blend while keeping the rest of the stack close enough to isolate behavioral change.
2. Gate promotion on two conditions together: offline balanced accuracy must beat `0.972299` by a real margin or match it with clearly better true-Medium behavior, and the fold pattern must look safer than `S-102`.
3. Use analyst capacity only after a new candidate exists and only to answer a narrow promotion question about whether the new variant's Medium gains are robust enough to justify replacing `S-094`.

## Refresh Triggers
- A new scientist run exceeds `0.972299` or matches it with materially cleaner Medium-class behavior than `S-094`.
- A candidate improves CV but still shows unstable Medium behavior that makes replacement risk unclear.
- The deadline assumption changes from April 30, 2026 or leaderboard evidence materially diverges from the current offline ordering.
