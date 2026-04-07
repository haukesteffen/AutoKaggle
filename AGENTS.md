# AutoKaggle AGENTS

## Repo Map

- `agents/` holds the canonical prompt files: `shared.md` (all agents), `supervisor.md`, `scientist.md`, `analyst.md`.
- `state/` holds hot durable state: `run-state.md` (phase, active tasks, focus), `backlog.md` (ranked idea queue), `portfolio.md` (base model inventory), `memory.md` (competition facts, policy, signals), `scientist-task.md`, `analyst-task.md`.
- `history/` holds compact append-only ledgers: `experiments.md`, `analyses.md`, `submissions.md`.
- `work/` holds task-local worker code: `experiment.py`, `analysis.py`.
- `artifacts/` holds untracked task outputs under `artifacts/<task_id>/`.

## Hard Constraints

- Do not change the fixed folds in `harness/dataset.py`.
- Keep binary artifacts untracked under `artifacts/<task_id>/`.
- No agent installs packages or changes dependencies without explicit human approval.
- Only the supervisor curates `state/` files: `run-state.md`, `backlog.md`, `portfolio.md`, `memory.md`, and task files.
- Only the supervisor runs git commands.
- Only the supervisor submits to Kaggle.
- Only the analyst edits `work/analysis.py` and runs `harness/analysis_runner.py`.
- Only the scientist edits `work/experiment.py` and runs `harness/experiment_runner.py`.
- The analyst may read `state/portfolio.md` and `state/backlog.md` for context but must not modify them.
