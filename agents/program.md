# AutoKaggle Shared Contract

This repository runs a file-mediated agent team for Kaggle competition work.

## Mission

Win the current Playground Series competition by combining disciplined experimentation, targeted analysis, and selective leaderboard submissions.

Current competition:

- Name: Predicting Irrigation Need (S6E4)
- Task: multiclass classification
- Labels: `High`, `Low`, `Medium`
- Metric: balanced accuracy
- Kaggle submission limit: 5 per day

## Roles

- `Supervisor`: the human interface, orchestrator, submission owner, and only committer.
- `Strategist`: produces near-term strategy guidance from run facts.
- `Analyst`: answers one concrete yes/no hypothesis and curates durable knowledge.
- `Scientist`: executes one concrete experiment task and records one terminal result.

`Strategist`, `Analyst`, and `Scientist` are episodic subagents, not permanent terminals.

## Durable Files

Control files:

- `agents/strategist/strategy-request.md`
- `agents/scientist/scientist-task.md`
- `agents/analyst/analyst-hypothesis.md`

Durable outputs:

- `agents/strategist/strategy-whitepaper.md`
- `agents/scientist/scientist-results.md`
- `agents/analyst/analyst-findings.md`
- `agents/analyst/analyst-knowledge.md`
- `agents/supervisor/leaderboard-history.md`
- `agents/supervisor/run-state.md`

## Runtime Rules

- Fixed folds from `harness/dataset.py` must not change.
- Binary artifacts are untracked and live under `artifacts/<task_id>/`.
- The supervisor is the only role that commits tracked files or submits to Kaggle.
- No agent installs packages or changes dependencies without human approval.
- The supervisor should be able to resume from repo files alone after a fresh Codex session.

## Token Rules

- Default to the compact restart context in `agents/supervisor/run-state.md`.
- Do not load large histories unless the current decision requires raw detail.
- Refresh `agents/supervisor/run-state.md` after every durable state change:

```bash
uv run python -m harness.supervisor_snapshot
```

## Role Docs

- `agents/supervisor/role.md`
- `agents/strategist/role.md`
- `agents/analyst/role.md`
- `agents/scientist/role.md`

Detailed file-shape contracts live under `agents/contracts/`.
