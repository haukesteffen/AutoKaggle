# Strategy Whitepaper

## Current Date
April 4, 2026

## Deadline Assumption
April 30, 2026, assuming the S6E4 Playground competition follows the standard month-end close.

## Days Remaining
26

## Read
The run is in a narrow-margin regime. S-094 still leads both CV and LB, and the latest direct simplification check, S-101, reproduced S-093 rather than improving on it. That result reinforces the existing read that S-094's advantage is small but presently real, while the specific S-052 recovery story is not the durable source of that edge. Submission capacity is already exhausted for April 4, 2026, so the immediate value is in offline discrimination work rather than leaderboard probing.

## Emphasis
Primary: isolate the true source of S-094's 0.000017 CV edge over the S-093/S-101 family and decide whether it is structurally reproducible.
Secondary: queue one or two high-information offline variants that test interaction effects around the S-094 stack rather than further simplification-only checks.
Background: preserve submission discipline and hold S-094 as the current deployment baseline.
Hold: additional direct no-S-052 or near-duplicate simplification experiments unless they test a clearly different causal hypothesis.

## Guidance For The Supervisor
1. Treat S-101 as confirmation that the next lane is attribution, not more blind simplification. The highest-value question is which exact component or interaction makes S-094 better than both S-093 and S-101.
2. Spend the next scientist cycle on one bounded ablation lane centered on S-094 versus S-093/S-101, with success defined as either reproducing the edge in a cleaner form or proving the edge is too brittle to prioritize.
3. Use the next available submission only for a model that is either the standing S-094 baseline or a new offline winner with a clear causal story and non-trivial CV separation.

## Refresh Triggers
- A new offline result matches or exceeds S-094 with a simpler or better-attributed construction.
- Evidence shows the S-094 edge is fold-noise-level and not reproducible across targeted ablations.
- A submission slot opens after April 4, 2026 and there is a credible challenger to S-094.
