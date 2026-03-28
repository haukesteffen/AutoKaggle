# AutoKaggle

## Audience

This document is the human/operator entry point.

- Read this file if you are starting, monitoring, or stopping a run.
- Agents should use [program.md](program.md) for shared context.
- Each agent should use its own role spec under [roles/](roles).

## What This Repo Is

AutoKaggle is an experiment in running a small team of Claude Code agents against a Kaggle Playground competition.

The repository has two layers:

- fixed harness code under [harness/](harness)
- agent-edited task files such as [experiment.py](experiment.py) and [promotion.py](promotion.py)

The current documented operating model on `main` uses four long-lived roles:

- supervisor
- scientist
- analyst
- engineer

That topology may change in future issues, but this README describes the current behavior on `main`.

## Document Map

- [README.md](README.md): human/operator guide
- [program.md](program.md): shared agent-facing context
- [roles/supervisor.md](roles/supervisor.md): supervisor-only instructions
- [roles/scientist.md](roles/scientist.md): scientist-only instructions
- [roles/analyst.md](roles/analyst.md): analyst-only instructions
- [roles/engineer.md](roles/engineer.md): engineer-only instructions

## Prerequisites

- Install `uv`.
- Run `uv sync`.
- Configure Kaggle authentication on your machine before starting a run.
- Make sure your Kaggle account has access to the target competition and has accepted any required rules.
- Start Claude Code from within the repository / worktree directories created for the run.

## Starting A Run

1. Open a terminal in the repository root:

```bash
cd <root>/AutoKaggle
claude
```

2. Tell the supervisor:

```text
You are the supervisor, start a new run.
```

3. The supervisor will:
   - propose a run tag
   - create branches and worktrees
   - ensure competition data exists
   - initialize the tracked communication files
   - tell you which `claude` commands to run for the other roles

4. Open the additional terminals exactly as instructed by the supervisor.

5. Once the other role sessions are open, tell the supervisor they are running so it can start the run logic.

## During A Run

The human is expected to:

- approve new capabilities or permissions when an agent asks
- watch supervisor updates
- intervene on strategic questions or external blockers
- say `stop` when you want the run to end

Useful places to inspect:

- [scientist-guidance.md](scientist-guidance.md) when present
- [analyst-hypotheses.md](analyst-hypotheses.md) when present
- [engineer-promotions.md](engineer-promotions.md) when present
- `artifacts/<tag>/` for untracked run outputs

## Repository Layout

Key tracked files:

- [program.md](program.md): shared agent contract
- [experiment.py](experiment.py): scientist-owned experiment file
- [analysis.py](analysis.py): analyst working script
- [promotion.py](promotion.py): engineer submission-preparation script
- [harness/dataset.py](harness/dataset.py): data contract and CV split logic
- [harness/experiment_runner.py](harness/experiment_runner.py): experiment execution and timeout handling
- [harness/analysis_runner.py](harness/analysis_runner.py): analysis execution and findings append flow
- [harness/promotion_runner.py](harness/promotion_runner.py): submission harness entrypoint

Important untracked paths:

- `data/`
- `artifacts/`
- `.claude/settings.local.json`

## Notes

- The committed [`.claude/settings.json`](.claude/settings.json) is project-wide and path-free.
- Machine-specific permissions and directories belong only in untracked local Claude settings.
- Do not push local run state, local Claude state, downloaded Kaggle data, or generated artifacts.
