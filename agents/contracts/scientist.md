# Scientist Contract

## Inputs

Required:

- `agents/scientist/scientist-task.md`

Useful compact context:

- `agents/supervisor/run-state.md`

## Outputs

Editable tracked files:

- `agents/scientist/experiment.py`
- `agents/scientist/scientist-results.md`

## Task Shape

```markdown
# Active Scientist Task
status: active
id: S-018
at: 2026-03-29T12:00Z
goal: <one concrete experiment goal>
reference: <optional short reference>
```

## Results Shape

```markdown
# Scientist Results

| id | score | std | delta_best | desc |
|----|-------|-----|------------|------|
| S-018 | 0.916540 | 0.001083 | +0.000000 | short description |
```

## Workflow Rules

- One invocation = one task = one terminal row.
- Run `uv run python -m harness.experiment_runner`.
- Retry locally if the runner reports `status: invalid`.
- Log only terminal outcomes, never invalid attempts.
- Use `-` for `score`, `std`, and `delta_best` on timeout/error/blocker rows.
- Keep `desc` short.
- Do not read the full results ledger unless needed to audit an older run.
