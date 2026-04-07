# Model Portfolio

Base models with OOF predictions in artifacts/. Supervisor updates after each new base model or stacking rebuild.

## Active Base Models

| model_id | family | feature_set | cv_score | role_in_stack | diversity_notes |
|----------|--------|-------------|----------|---------------|-----------------|
| S-014 | XGBoost | SM^2 + basic numerics + OHE cats | 0.970856 | L0 primary | Anchor model; strong fold stability; depth=5 subsample=0.8 colsample=0.8 |
| S-082 | LGBM | SM^2 + OrdinalEncoder cats | 0.970657 | L0 base | n=1500 lr=0.02 leaves=15; moderate diversity vs XGB |
| S-073 | MLP 3-seed | poly3 top-4 + raw + OHE cats | 0.964422 | L0 base | tanh (64,32) 3-seed avg; high diversity, different feature space |
| S-052 | LR poly4 | poly4 top-4 + raw + log1p(Rain) + I_SM_low + OHE | 0.928573 | L0 base | C=10 lbfgs balanced; linear diversity, mainly Medium signal |

## Current Stack

| stack_id | architecture | base_models | cv_score | lb_score | status |
|----------|-------------|-------------|----------|----------|--------|
| S-094 | L1 Multinomial LR C=4 balanced on OVR logits | S-014, S-082, S-073, S-052 | 0.972299 | 0.97144 | best submitted (rank 157) |

## Gaps

- No CatBoost (timed out at iter=500+ in S-029/S-030; untested at lower budget)
- No KNN, Ridge, SVR, or other non-tree diversity models
- No TabPFN (would need subsampling to <=10K rows)
- Only 4 base models (grandmaster standard: 10-30+)
- All models trained on similar basic features (SM^2, raw numerics, OHE/OrdinalEncoder cats)
- No GroupBy aggregation features, no target encoding, no frequency encoding, no categorical interactions
- Stack is single-level LR only; no tree-based or NN meta-learners tried at L1
