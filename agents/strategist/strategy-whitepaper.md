# Strategy Whitepaper

## Current Date
April 4, 2026

## Deadline Assumption
April 30, 2026, assuming the competition deadline has not changed.

## Days Remaining
26

## Read
The run is in a productive consolidation phase. `S-094` is now the strongest anchor on both axes, with `0.972299` CV and `0.97144` public LB at rank 157, improving on `S-089` at `0.97087` LB and rank 165. The wake sharpened the signal around ensemble composition rather than broad model churn: `S-091` established that logit features help, `S-093` showed `S-073` still contributes inside a learned stacker, and `S-094` extracted a further but smaller gain from adding `S-052`. The recent negatives are informative rather than alarming: `S-092` underperformed materially, and `S-095` indicates the 4-way stacker is near its useful regularization range because raising `C` to `8.0` did not improve on `S-094`.

## Emphasis
Primary: Exploit the validated `S-094` stacker lane with small, hypothesis-driven composition and calibration adjustments around the proven `S-091`/`S-093`/`S-094` recipe.

Secondary: Preserve leaderboard discipline by treating `S-094` as the submission-quality reference and requiring clear local evidence before spending additional April 2026 submission slots.

Background: Maintain light analyst-style scrutiny on why recovered members such as `S-073` and `S-052` add value, so future stack revisions stay selective instead of expanding blindly.

Hold: Broad base-model diversification, aggressive hyperparameter sweeps, and further `C`-increase probing on the current 4-way stacker unless new evidence contradicts `S-095`.

## Guidance For The Supervisor
1. For the next few checkpoints after April 4, 2026, keep the main lane tightly focused on variants that are one edit away from `S-094`: member inclusion/exclusion tests, modest calibration changes, or equivalent low-variance stacker refinements.
2. Use `S-094` as the decision bar. If a candidate does not beat `0.972299` CV cleanly or does so only within noise, treat it as non-promotable and avoid leaderboard use.
3. Keep quiet lanes quiet until the current stacker lane is exhausted. The wake already produced enough signal to justify depth over breadth, and `S-095` argues against spending near-term checkpoints on larger-`C` retries.

## Refresh Triggers
- A new run exceeds `S-094` on CV by a meaningful margin or produces a materially better public LB result than `0.97144`.
- Two consecutive near-`S-094` variants fail to improve, indicating the current stacker recipe is saturated.
- Any new evidence shows the contribution from `S-073`, `S-052`, or logit features is fold-fragile rather than durable.
