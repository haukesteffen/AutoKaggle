# Run State

as_of: 2026-04-05
stage: feature_engineering
lane: feature-expansion
active_scientist_task: none
active_analyst_task: none

## Current Focus

- best_offline_candidate: S-105 | 0.972308 | Multinomial LR C=4.0 balanced on S-094 OVR logits + shrunk S-052 High/Low
- best_submitted_candidate: S-094 | 2026-04-04T18:25Z | 0.97144 LB | rank 157
- next_decision: Begin feature engineering phase. The stacking layer plateaued after 18 experiments (+0.0004 total). Expand the base with new features and diverse models before rebuilding the stack.
- next_batch: First backlog item: GroupBy aggregation features (mean/std/count of numerics grouped by each categorical) on XGBoost baseline (S-014 config).
