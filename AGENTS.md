# AutoKaggle AGENTS

## Repo Map

- `agents/` holds the canonical prompt files.
- `state/` holds hot durable state and active task files.
- `history/` holds compact append-only ledgers.
- `work/` holds task-local worker code.
- `artifacts/` holds untracked task outputs under `artifacts/<task_id>/`.

## Default Read Order

1. `AGENTS.md`
2. `agents/shared.md`
3. `agents/supervisor.md`
4. `state/run-state.md`
5. Any active task file in `state/`

## Hard Constraints

- Do not change the fixed folds in `harness/dataset.py`.
- Keep binary artifacts untracked under `artifacts/<task_id>/`.
- Only the supervisor curates `state/`, `state/memory.md`, `history/`, commits tracked files, and submits to Kaggle.
- No agent installs packages or changes dependencies without explicit human approval.
