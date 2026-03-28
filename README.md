# AutoKaggle

## Audience

This document is the human/operator entry point.

- Read this file if you are starting, monitoring, or stopping a run.
- Agents should use [agents/program.md](agents/program.md) for shared context.
- Each agent should use its own role spec under `agents/<role>/role.md`.

## What This Repo Is

AutoKaggle is an experiment in running a small team of Claude Code agents against a Kaggle Playground competition.

The repository has two layers:

- fixed harness code under [harness/](harness)
- agent-facing prompts, inboxes, and working files under [agents/](agents)

The current documented operating model on `main` uses four long-lived roles plus one on-demand planning role:

- supervisor
- scientist
- analyst
- engineer
- strategist (episodic / temporary, not a permanently running session)

That topology may change in future issues, but this README describes the current behavior on `main`.

## Document Map

- [README.md](README.md): human/operator guide
- [agents/program.md](agents/program.md): shared agent-facing context
- [agents/supervisor/role.md](agents/supervisor/role.md): supervisor-only instructions
- [agents/strategist/role.md](agents/strategist/role.md): strategist-only instructions
- [agents/scientist/role.md](agents/scientist/role.md): scientist-only instructions
- [agents/analyst/role.md](agents/analyst/role.md): analyst-only instructions
- [agents/engineer/role.md](agents/engineer/role.md): engineer-only instructions

## Prerequisites

- Install `uv`.
- Run `uv sync`.
- Configure Kaggle authentication on your machine before starting a run.
- Make sure your Kaggle account has access to the target competition and has accepted any required rules.
- Start Claude Code from within the repository or worktree directories created for the run.

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
   - initialize the tracked communication files under `agents/`
   - tell you which `claude` commands to run for the other roles

4. Open the additional terminals exactly as instructed by the supervisor.

5. The supervisor may also ask you to open a temporary strategist session in the main repo:

```bash
cd <root>/AutoKaggle
claude
```

That strategist session is on-demand. It is not a permanent terminal like the supervisor, scientist, analyst, and engineer sessions.

6. Once the other role sessions are open, tell the supervisor they are running so it can start the run logic.

## During A Run

The human is expected to:

- approve new capabilities or permissions when an agent asks
- watch supervisor updates
- intervene on strategic questions or external blockers
- say `stop` when you want the run to end

Useful places to inspect:

- [agents/strategist/strategy-whitepaper.md](agents/strategist/strategy-whitepaper.md) when present
- [agents/strategist/strategy-idea-cookbook.md](agents/strategist/strategy-idea-cookbook.md)
- [agents/scientist/scientist-guidance.md](agents/scientist/scientist-guidance.md) when present
- [agents/analyst/analyst-hypotheses.md](agents/analyst/analyst-hypotheses.md) when present
- [agents/engineer/engineer-promotions.md](agents/engineer/engineer-promotions.md) when present
- `artifacts/<tag>/` for untracked run outputs

## Repository Layout

Key tracked files:

- [agents/program.md](agents/program.md): shared agent contract
- [agents/strategist/strategy-whitepaper.md](agents/strategist/strategy-whitepaper.md): strategist-owned current plan
- [agents/strategist/strategy-idea-cookbook.md](agents/strategist/strategy-idea-cookbook.md): strategist-owned reusable playbook
- [agents/scientist/experiment.py](agents/scientist/experiment.py): scientist-owned experiment file
- [agents/analyst/analysis.py](agents/analyst/analysis.py): analyst working script
- [agents/engineer/promotion.py](agents/engineer/promotion.py): engineer submission-preparation script
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
