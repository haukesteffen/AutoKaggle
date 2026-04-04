# AutoKaggle

1. Ensure `uv` is installed.

2. Ensure Kaggle auth is already set up.

3. Refresh the compact supervisor restart context:

```bash
uv run python -m harness.supervisor_snapshot
```

4. Start Codex in this repo and say:

```text
Resume AutoKaggle as the supervisor. Read `AGENTS.md`, `agents/program.md`, `agents/supervisor/role.md`, and `agents/supervisor/run-state.md`, then continue from there.
```

Project-scoped custom agents are available under `.codex/agents/`:

- `strategist`
- `analyst`
- `scientist`

The supervisor should prefer those named agents for delegation rather than spawning generic subagents with copied context.

Recommended operating style:

- Prefer a fresh Codex supervisor session after each completed checkpoint or when the thread starts feeling noisy.
- Refresh `agents/supervisor/run-state.md` before resuming in a new session.
