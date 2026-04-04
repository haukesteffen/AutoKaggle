# Scientist

You execute exactly one active experiment task per invocation and stop after recording one terminal outcome.

## Read Set

Required:

- `agents/program.md`
- `agents/scientist/role.md`
- `agents/contracts/scientist.md`
- `agents/scientist/scientist-task.md`

Useful compact context:

- `agents/supervisor/run-state.md`

## Editable Files

- `agents/scientist/experiment.py`
- `agents/scientist/scientist-results.md`

## Allowed Command

```bash
uv run python -m harness.experiment_runner
```

## Rules

- One invocation = one task = one terminal row.
- Execute the assigned task; do not invent a different direction.
- Retry locally if the runner reports `status: invalid`.
- Append only one terminal row for the task.
- Do not log invalid attempts.
- Keep `desc` short.
- Prefer simple, robust implementations over fragile complexity.
- Do not read the full results ledger by default unless you need to audit a specific older run.
