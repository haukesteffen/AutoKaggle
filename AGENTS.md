# AutoKaggle AGENTS

This repository is a file-mediated multi-agent Kaggle workflow optimized for Codex.

## Default Operating Model

- The human interacts with the `Supervisor`.
- `Strategist`, `Analyst`, and `Scientist` are bounded subagents. They should be invoked only for one concrete task at a time.
- Durable state lives in tracked repo files, not in chat history.
- The supervisor should be able to resume from files alone after a fresh Codex session.

## Default Read Order

For normal supervisor work, start with this minimum set:

1. `agents/program.md`
2. `agents/supervisor/role.md`
3. `agents/supervisor/run-state.md`
4. Any active control file with `status: active`

Do not read large histories by default. Only read them when the current decision needs raw detail.

## Token Discipline

- Prefer cold-start-safe workflows over long conversational memory.
- Keep prompts short and specific. Avoid repeating instructions already captured in files.
- Treat `agents/supervisor/run-state.md` as the default restart context.
- Refresh `agents/supervisor/run-state.md` after any durable state change:

```bash
uv run python -m harness.supervisor_snapshot
```

- Do not read `agents/scientist/scientist-results.md`, `agents/analyst/analyst-findings.md`, or `agents/analyst/analyst-knowledge.md` front-to-back during routine wakes.
- If the supervisor thread becomes noisy, finish the current atomic checkpoint, refresh `run-state.md`, and continue in a fresh Codex session.

## Subagent Rules

- Use subagents only when the work is clearly bounded and materially advances the current step.
- When a project-scoped custom agent exists in `.codex/agents/`, prefer that named agent over a generic subagent.
- Give each subagent a minimal read set and one owned output.
- Do not fork the full supervisor thread into a subagent unless the task depends on transient thread-local reasoning.
- Prefer short file-pointer prompts over replaying state in the handoff.
- Do not use subagents for open-ended “go think” work.
- Because subagents consume extra model/tool tokens, prefer a single-agent path unless parallelism or role separation is useful enough to justify the cost.

## Repo Constraints

- Fixed folds in `harness/dataset.py` are part of the experiment contract. Do not change them.
- Binary artifacts stay untracked under `artifacts/<task_id>/`.
- Only the supervisor commits tracked files and submits to Kaggle.
- No agent installs packages or changes dependencies without explicit human approval.

## Research Notes

Rationale and current OpenAI/Codex guidance are summarized in `docs/codex-migration.md`.
