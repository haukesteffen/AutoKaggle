# Codex Migration Notes

Updated: April 5, 2026

AutoKaggle now uses a flat prompt and ledger layout so the supervisor can cold-start from files instead of thread memory.

## Canonical Read Order

1. `AGENTS.md`
2. `agents/shared.md`
3. `agents/supervisor.md`
4. `state/run-state.md`
5. Only the active task file or the narrow `history/*` row needed for the next decision

## Canonical Repo Surfaces

- Prompt files live in `agents/*.md`
- Hot durable state lives in `state/`
- Append-only ledgers live in `history/`
- Task-local worker code lives in `work/`
- Task outputs live in `artifacts/<task_id>/`

## Current Harness Commands

```bash
uv run python -m harness.supervisor_snapshot
uv run python -m harness.experiment_runner
uv run python -m harness.analysis_runner
uv run python -m harness.promotion_runner --task-id S-###
```

## Operating Notes

- Refresh `state/run-state.md` after each durable state change.
- Scientists execute one bounded batch from `state/scientist-task.md` and append one row to `history/experiments.md`.
- Analysts answer one bounded question from `state/analyst-task.md`, write artifacts under `artifacts/<task_id>/`, and append one row to `history/analyses.md`.
- Submission and leaderboard history lives in `history/submissions.md`.
- Prefer a fresh supervisor session after a clean checkpoint instead of carrying a long thread.
