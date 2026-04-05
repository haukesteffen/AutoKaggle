# AutoKaggle

1. Ensure `uv` is installed.
2. Ensure Kaggle auth is already set up.
3. Refresh the compact supervisor restart context:

```bash
uv run python -m harness.supervisor_snapshot
```

4. Start Codex in this repo and say:

```text
Resume AutoKaggle as the supervisor. Read `AGENTS.md`, `agents/shared.md`, `agents/supervisor.md`, and `state/run-state.md`, then continue from there.
```

Canonical repo surfaces:

- Prompt files: `agents/shared.md`, `agents/supervisor.md`, `agents/scientist.md`, `agents/analyst.md`
- Durable state: `state/`
- Append-only ledgers: `history/`
- Worker code: `work/`

Current harness commands:

- `uv run python -m harness.supervisor_snapshot`
- `uv run python -m harness.experiment_runner`
- `uv run python -m harness.analysis_runner`
- `uv run python -m harness.promotion_runner --task-id S-###`

Refresh `state/run-state.md` before resuming in a new supervisor session.
