# Strategy Whitepaper

## Current Date
April 4, 2026

## Deadline Assumption
April 30, 2026, assuming the competition deadline has not changed.

## Days Remaining
26

## Read
The strongest live signal is still the `S-094` 4-member logit stacker, and the last three probes were informative but non-improving. `S-095` and `S-096` make it unlikely that nearby `C` retuning will unlock more value, while `S-097` reinforces that logit-transformed member outputs are part of the gain rather than an incidental detail. The active opportunity is now narrower: verify whether all four members are still earning their place under the `S-094` recipe, while opening one adjacent refinement lane that preserves the same low-variance structure instead of drifting into broad blend exploration.

## Emphasis
Primary: Selective member-level ablations and composition checks around the exact `S-094` recipe.
Secondary: One adjacent low-variance refinement family that keeps logit features and multinomial LR as the core structure.
Background: Analyst scrutiny on why `S-073` and `S-052` help only under selective stacking and not under naive averaging.
Hold: Further local `C` sweeps and raw-probability variants of the same stacker.

## Guidance For The Supervisor
1. Use the next checkpoint budget on composition evidence, not more regularization tuning. Treat `S-094` as the control and test whether each of `S-073` and `S-052` is still additive under the exact logit-plus-LR recipe before trying broader member changes.
2. In parallel with those ablations, open one refinement lane that is structurally close to `S-094` and low variance, such as controlled feature-space or class-weight handling within the same multinomial logit stacker family. Do not branch into high-churn blend families until this lane is checked.
3. If the first ablation pass shows both marginal members are genuinely useful, then keep the 4-member stacker as the mainline and ask the analyst for a tightly scoped explanation of the diversity pattern before spending more scientist budget on wider ensemble composition.

## Refresh Triggers
- A new experiment beats `0.972299` CV or materially narrows confidence around a simpler composition.
- An ablation shows one current `S-094` member is neutral or harmful under the exact control recipe.
- Analyst evidence changes the interpretation of why selective stacking helps while naive averaging regresses.
