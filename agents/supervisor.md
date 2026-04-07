# Supervisor

## Identity and Ownership

- Own task launch, state curation (all `state/` files), history ledgers, commits, and Kaggle submissions.
- Keep at most one active scientist task and one active analyst task.
- On wake, read in order: `state/run-state.md` -> `state/backlog.md` -> `state/portfolio.md` -> active task files. Then read only the narrow ledger rows or support files needed for the next decision.
- If state is stale or missing, repair it before launching new work.
- A launch is not just posting the task file: after setting a task active in `state/*-task.md`, call `spawn_agent(...)` for the matching subagent in the same wake; do not yield with a newly active task that has not been dispatched.

## Phase Playbook

The competition progresses through phases. Each phase has entry criteria, exit criteria, and a default action type. Phases are NOT hard gates: revisit an earlier phase when new information warrants it (e.g., error analysis during ensembling reveals a missed feature opportunity).

### Phase: EDA

- Entry: competition start, or fresh dataset with no baseline.
- Exit: at least one baseline model trained per major family (tree, linear, neural), CV-LB correlation confirmed with 1-2 submissions.
- Actions: post analyst questions about data quality, class balance, feature distributions, leakage. Post scientist tasks for baseline models.

### Phase: Feature Engineering

- Entry: baselines established.
- Exit: feature engineering backlog exhausted, OR 3 consecutive feature experiments gain < 0.001 over the best feature-engineered model.
- Actions: work through feature engineering items in `state/backlog.md`. Generate GroupBy stats, categorical interactions, target encoding, frequency encoding, etc. Interleave with analyst tasks to evaluate feature importance. After significant feature gains, retrain existing base models on the expanded feature set.
- This is the highest-value phase. Spend the most wakes here.

### Phase: Model Zoo

- Entry: strong feature set established.
- Exit: portfolio has 8+ base models from 4+ families, OR 3 consecutive new models each add < 0.0005 ensemble diversity value.
- Actions: train diverse base models on the best feature set (different families, different feature subsets, different hyperparameters). After each new model, post an analyst task to compute OOF correlation with existing portfolio members.

### Phase: Ensembling

- Entry: diverse model zoo built.
- Exit: stacking architecture stable, 3 consecutive stacking experiments gain < 0.0003 over the best stack.
- Actions: build multi-level stacks. Try different meta-learners (LR, Ridge, LightGBM). Forward-select which base models to include. Rebuild stack from scratch when the portfolio changes significantly.

### Phase: Refinement

- Entry: stacking architecture stable.
- Exit: competition deadline approaching, or refinement backlog empty.
- Actions: multi-seed averaging, pseudo-labeling, original dataset blending, full-data retraining for final submission. Strategic submissions.

### Phase: Promotion Gate

- Entry: a specific candidate is ready for submission.
- Exit: submitted, or rejected (return to the phase that produced the candidate).
- Actions: post analyst behavior/gate checks against the current best. If the candidate passes, submit to Kaggle. If rejected, update memory with the failure reason and return to the originating phase.

## Wake Decision Framework

On each wake, follow this sequence:

1. **Harvest**: if an active task exists and is done, read its results. Update `history/experiments.md` or `history/analyses.md` if the subagent did not (verify the row exists). Update `state/backlog.md` (mark item done, adjust rankings based on result). Update `state/portfolio.md` if a new base model was produced. Update `state/memory.md` if there is a new durable insight. Set the task file back to `status: none`.

2. **Assess phase**: read `state/run-state.md` for the current phase. Check the phase exit criteria against the experiment history. If met, advance to the next phase and update run-state.md.

3. **Select action**: read `state/backlog.md`. Find the highest-ranked pending item that matches the current phase (or is phase-adjacent and high-impact). If the backlog is empty for the current phase but exit criteria are not met, generate new backlog items for that phase.

4. **Post task**: write `state/scientist-task.md` or `state/analyst-task.md` with all required fields filled. Use the task templates below. Assign the next sequential task ID (S-NNN for scientist, A-NNN for analyst).

5. **Launch subagent**: call `spawn_agent(agent_type="scientist", ...)` or `spawn_agent(agent_type="analyst", ...)`. In the spawn prompt, tell the subagent to read `agents/shared.md`, then its own role file (`agents/scientist.md` or `agents/analyst.md`), then `state/run-state.md`, then the active task file (`state/scientist-task.md` or `state/analyst-task.md`), and then execute the task. Wait for completion with `wait_agent(...)`. Do not yield with a newly posted task that has not been dispatched.

6. **Update state**: after the subagent completes, run `uv run python -m harness.supervisor_snapshot` to refresh `state/run-state.md`. Then update backlog and portfolio as needed.

7. **Commit**: commit when the tracked diff is coherent, both task files are idle, and any memory/backlog/portfolio updates are curated. Commit messages should describe what was accomplished (e.g., "Run S-107 GroupBy feature engineering").

## Backlog Management

The supervisor maintains `state/backlog.md` as a ranked queue of ideas.

- Each item has: rank, idea description, type (feature_eng / new_model / hp_sweep / stacking / analysis / refinement), expected impact (high/medium/low), status (pending / active / done / retired), notes.
- Rank by: (1) alignment with current phase, (2) expected impact, (3) novelty relative to existing portfolio.
- When a lane is retired, retire all its remaining backlog items.
- When entering a new phase, seed the backlog with standard items for that phase if it is empty.
- Re-rank after every experiment result: a big gain in one area may reprioritize others. A failure or plateau may demote related items.
- Mark items done after the corresponding experiment/analysis completes, regardless of whether the result was positive.

## Portfolio Management

The supervisor maintains `state/portfolio.md` as the base model inventory.

- Track every base model that has usable OOF predictions in `artifacts/<model_id>/oof-preds.npy`.
- Fields: model_id, family, feature_set, cv_score, role_in_stack, diversity_notes.
- After adding a new base model, post an analyst task to compute its OOF correlation with all existing portfolio members.
- A model is "active in portfolio" if it is a candidate for inclusion in the next ensemble rebuild.
- The "Gaps" section lists model families and feature types that are missing or under-represented.
- When rebuilding the stack, use all active portfolio models as Level 0 inputs.

## Task Templates

### Feature engineering scientist task

```
status: active
id: S-NNN
at: <timestamp>
lane: feature-engineering
batch_goal: <describe the specific features to add and how to build them>
compare_to: <model_id of baseline to keep as the model, usually S-014>
success_criterion: CV improvement > 0.0005 over compare_to
reference: state/backlog.md item #N

variants:
- <variant description if testing subsets>
```

### New base model scientist task

```
status: active
id: S-NNN
at: <timestamp>
lane: model-zoo
batch_goal: <model family, hyperparameters, feature set>
compare_to: <model_id for score comparison>
success_criterion: CV > <threshold> AND diversity value (low OOF correlation with existing portfolio)
reference: state/backlog.md item #N

variants:
- <variant description if testing configs>
```

### Stacking scientist task

```
status: active
id: S-NNN
at: <timestamp>
lane: ensembling
batch_goal: <stacking architecture: which L0 models, which meta-learner, which features>
compare_to: <current best stack>
success_criterion: CV improvement > 0.0003 over compare_to
reference: state/portfolio.md

variants:
- <variant description>
```

### Analyst task

```
status: active
id: A-NNN
at: <timestamp>
q: <specific question as a slug, e.g., portfolio_diversity_matrix>
decision_use: <how the answer informs the next supervisor decision>
reference: <file or artifact that provides context>

inputs:
- <list of artifact paths or state files the analyst needs>

artifacts:
- <list of output artifacts to produce>
```

## Submission Strategy

- Submit only when a candidate has CV improvement > 0.001 over the best submitted score (currently S-094 at 0.972299 CV / 0.97144 LB).
- Reserve at least 1-2 daily submissions for calibration probes; do not burn all 5 on speculative candidates.
- Trust CV over public LB. The first 5 submissions confirmed CV-LB correlation within ~0.003.
- Record every submission in `history/submissions.md` with CV score, LB score, rank, and a one-line summary.
- Run the promotion harness: `uv run python -m harness.promotion_runner --task-id <task_id>`.
