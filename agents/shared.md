# AutoKaggle Shared Contract

## System

- AutoKaggle is a supervised Kaggle workflow that runs bounded ML experiment and data analysis tasks, records compact results, and promotes reviewed candidates.
- AutoKaggle is perpetual work, not a finite script: each supervisor wake should convert available capacity into the next bounded task or the smallest unblock needed to launch one.
- The supervisor sets direction, posts tasks, invokes subagents, curates all `state/` files, and handles commits and submissions.
- Posting a task file is preparation; the launch happens only when the supervisor also calls `spawn_agent(...)` for the matching subagent during that wake.
- The scientist runs one posted experiment batch and reports one compact result.
- The analyst answers one posted evaluation question and reports one compact result.

## Directories

- `state/` is the active control plane: `run-state.md` (phase, active tasks, focus), `backlog.md` (ranked idea queue), `portfolio.md` (base model inventory), `memory.md` (competition facts, policy, signals), and task files.
- `history/` is the compact append-only ledger: `experiments.md`, `analyses.md`, `submissions.md`.
- `work/` is task-local worker code: `experiment.py`, `analysis.py`.
- `artifacts/<task_id>/` holds bulky outputs (OOF predictions, test predictions, models, logs).

## Protocol

- Use repo files as the source of truth; keep prompts and outputs restart-safe from files alone.
- Read only the smallest file set that can answer the current question.
- Keep each invocation bounded and end it with one compact terminal result.
- Do not improvise strategy outside the posted task.
- Put raw logs, bulky evidence, and long stdout in `artifacts/<task_id>/`.
- If a result suggests a memory or backlog update, return it as a candidate note for the supervisor.

## Competition Strategy Knowledge

Score drivers for tabular Kaggle competitions, ranked by typical impact:

1. **Feature engineering** (highest impact): GroupBy aggregations (mean/std/count/min/max of numerics grouped by each categorical), pairwise categorical interactions, target encoding (within CV folds only), frequency encoding, dual numeric/categorical treatment (bin numerics into quantiles), ratio features, polynomial features, threshold indicators.
2. **Model diversity** (high impact): A slightly worse model that is uncorrelated with the best model is more valuable for ensembling than a slightly better correlated model. Train multiple families (XGBoost, LightGBM, CatBoost, MLP, Ridge, KNN, ExtraTrees, TabPFN) on different feature subsets. Track diversity via OOF prediction correlation.
3. **Ensembling and stacking** (high impact): Level 0 = 10+ diverse base models. Level 1 = meta-learners trained on L0 OOF predictions (LR, Ridge, LightGBM). Level 2 = simple average or weighted blend of L1 outputs.
4. **Hyperparameter tuning** (moderate impact): Tune after features are stable. Use early stopping. Key GBDT parameters: n_estimators, learning_rate, max_depth/num_leaves, min_child_samples, subsample, colsample_bytree, reg_alpha/lambda.
5. **Late-stage refinements** (moderate impact): Multi-seed averaging (train N seeds, average predictions), pseudo-labeling (use confident test predictions as extra training data), original dataset blending (Playground Series data is synthetic; the original real dataset often helps).

Playground Series specifics: data is synthetic from a real source. Blending original + synthetic training data is standard. 5 submissions per day. Trust CV over public LB after establishing correlation with 2-3 calibration submissions.

## Plateau Detection

- If the last 3 experiments in a lane each gained < 0.0005 over that lane's best, the lane is saturated. The supervisor should retire it and pivot to a different approach.
- If the last 5 analyst questions in a row rejected a promotion candidate, the current framing is over-constrained. The supervisor should broaden scope or change phase.
