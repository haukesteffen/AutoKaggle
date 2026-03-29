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

The current documented operating model on `main` uses one long-lived role plus three on-demand roles:

- supervisor
- strategist (episodic / temporary, not a permanently running session)
- analyst (episodic / temporary, invoked only for concrete yes/no investigations)
- scientist (episodic / temporary, invoked only for one concrete experiment task)

## Document Map

- [README.md](README.md): human/operator guide
- [agents/program.md](agents/program.md): shared agent-facing context
- [agents/supervisor/role.md](agents/supervisor/role.md): supervisor-only instructions
- [agents/strategist/role.md](agents/strategist/role.md): strategist-only instructions
- [agents/scientist/role.md](agents/scientist/role.md): scientist-only instructions
- [agents/analyst/role.md](agents/analyst/role.md): analyst-only instructions
- [agents/supervisor/leaderboard-history.md](agents/supervisor/leaderboard-history.md): tracked submission ledger

## Prerequisites

- Install `uv`.
- Run `uv sync`.
- Configure Kaggle authentication on your machine before starting a run.
- Make sure your Kaggle account has access to the target competition and has accepted any required rules.
- Start Claude Code from within the repository root.

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
   - create or update the long-lived `run` branch
   - prepare the run state
   - ensure competition data exists
   - initialize the tracked communication files under `agents/`
   - begin the supervisor loop and invoke strategist, analyst, and scientist work only when needed

4. The supervisor may ask you to open a temporary strategist, analyst, or scientist session in the main repo if direct episodic invocation is unavailable:

```bash
cd <root>/AutoKaggle
claude
```

Those sessions are on-demand. They are not permanent terminals.

## During A Run

The human is expected to:

- approve new capabilities or permissions when an agent asks
- watch supervisor updates
- intervene on strategic questions or external blockers
- say `stop` when you want the run to end

Useful places to inspect:

- [agents/strategist/strategy-whitepaper.md](agents/strategist/strategy-whitepaper.md) when present
- [agents/strategist/strategy-idea-cookbook.md](agents/strategist/strategy-idea-cookbook.md)
- [agents/scientist/scientist-task.md](agents/scientist/scientist-task.md) when present
- [agents/scientist/scientist-results.md](agents/scientist/scientist-results.md) when present
- [agents/scientist/scientist-knowledge.md](agents/scientist/scientist-knowledge.md) when present
- [agents/analyst/analyst-hypothesis.md](agents/analyst/analyst-hypothesis.md) when present
- [agents/analyst/analyst-findings.md](agents/analyst/analyst-findings.md) when present
- [agents/analyst/analyst-knowledge.md](agents/analyst/analyst-knowledge.md) when present
- [agents/supervisor/leaderboard-history.md](agents/supervisor/leaderboard-history.md) when present
- `artifacts/` for untracked run outputs

## Repository Layout

Key tracked files:

- [agents/program.md](agents/program.md): shared agent contract
- [agents/strategist/strategy-whitepaper.md](agents/strategist/strategy-whitepaper.md): strategist-owned current plan
- [agents/strategist/strategy-idea-cookbook.md](agents/strategist/strategy-idea-cookbook.md): strategist-owned reusable playbook
- [agents/scientist/scientist-task.md](agents/scientist/scientist-task.md): supervisor-owned active scientist task
- [agents/scientist/scientist-results.md](agents/scientist/scientist-results.md): append-only scientist result history
- [agents/scientist/scientist-knowledge.md](agents/scientist/scientist-knowledge.md): concise scientist-owned durable memory
- [agents/analyst/analyst-hypothesis.md](agents/analyst/analyst-hypothesis.md): supervisor-owned active analyst question
- [agents/analyst/analyst-findings.md](agents/analyst/analyst-findings.md): append-only analyst findings history
- [agents/analyst/analyst-knowledge.md](agents/analyst/analyst-knowledge.md): concise analyst-owned durable memory
- [agents/supervisor/leaderboard-history.md](agents/supervisor/leaderboard-history.md): supervisor-owned submission ledger and CV/LB notes
- [agents/supervisor/submission.py](agents/supervisor/submission.py): supervisor submission-preparation script
- [agents/scientist/experiment.py](agents/scientist/experiment.py): scientist-owned experiment file
- [agents/analyst/analysis.py](agents/analyst/analysis.py): analyst working script
- [harness/dataset.py](harness/dataset.py): data contract and CV split logic
- [harness/experiment_runner.py](harness/experiment_runner.py): experiment execution and timeout handling
- [harness/scientist_runner.py](harness/scientist_runner.py): scientist execution and result append flow
- [harness/analysis_runner.py](harness/analysis_runner.py): analysis execution and findings append flow
- [harness/promotion_runner.py](harness/promotion_runner.py): submission harness entrypoint

Important untracked paths:

- `data/`
- `artifacts/`
- `.claude/settings.local.json`
- `agents/analyst/analysis-errors.md`
- `agents/scientist/scientist-errors.md`

## Submission Harness

Supervisor submissions should go through [harness/promotion_runner.py](harness/promotion_runner.py), not raw Kaggle CLI calls. The harness:

- validates the artifact directory against the target hash
- generates `submission.csv` if needed
- submits to Kaggle
- polls until the submission is scored, errors, or times out
- prints deterministic JSON for leaderboard-history updates

Example invocation:

```bash
uv run python -m harness.promotion_runner \
  --hash <hash> \
  --artifact-dir artifacts/experiments/<hash> \
  --cv-score <cv_score>
```

## Notes

- The committed [`.claude/settings.json`](.claude/settings.json) is project-wide and path-free.
- Machine-specific permissions and directories belong only in untracked local Claude settings.
- The supervisor is the only agent that commits tracked changes.
- Do not push local run state, local Claude state, downloaded Kaggle data, or generated artifacts.
