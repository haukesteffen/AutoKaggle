# Strategy Whitepaper

## Current Date
April 4, 2026

## Deadline Assumption
April 30, 2026, assuming the S6E4 Playground competition follows the standard month-end close.

## Days Remaining
26

## Read
The run is near a local optimum on the current stacker family. `S-094` remains the best CV at `0.972299`, but the new evidence materially changes how to treat its components: `S-073` now looks genuinely additive in the exact control recipe, while `S-052` no longer has a strong durability case. The practical read is that the team should stop spending budget on nearby parameter sweeps and treat the decision as a structure choice: either simplify to the nearly equivalent `S-093` 3-way anchor or keep `S-094` only as a thin incumbent while testing low-variance refinements around the `S-093`/`S-073` core.

## Emphasis
Primary: Re-anchor the mainline around the `S-093` structure and test whether `S-073` can be retained without relying on `S-052`.
Secondary: Preserve `S-094` as the incumbent reference until a cleaner 3-way-plus-`S-073` variant either matches or fails clearly.
Background: Keep a small amount of attention on submission readiness and tie-break logic if multiple variants stay within roughly `0.00002` CV.
Hold: Additional local `C` tuning, no-logit variants, and further effort to justify `S-052` as a required durable member.

## Guidance For The Supervisor
1. Make the next checkpoint a narrow structural refinement family centered on `S-093` plus `S-073`, with the explicit goal of separating the value of `S-073` from the now-weakened `S-052` story.
2. Treat `S-093` as the practical mainline for decision-making unless a low-variance follow-up reproduces the `S-094` edge without needing `S-052`; the current `0.000017` gap is too small to justify complexity by itself.
3. Use the following checkpoint after that to decide promotion policy: if a simplified variant lands at or above the `S-093`/`S-094` band, promote simplicity; if not, retain `S-094` as the leaderboard-facing incumbent while freezing further family-local tweaks.

## Refresh Triggers
- A new experiment directly tests a `S-093`-anchored variant that includes `S-073` without `S-052`.
- Any result exceeds `0.972299` CV or produces a repeated gain of at least `0.00002` over both `S-093` and `S-094`.
- Leaderboard evidence contradicts the current assumption that the `S-094` edge is too small and fragile to outweigh its added complexity.
