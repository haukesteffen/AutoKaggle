# AutoKaggle

## Audience

This document is shared operational context for all agents.

- Human/operator instructions live in [README.md](../README.md).
- Role-specific instructions live under `agents/<role>/role.md`.
- Agents should treat this file as the shared contract that sits between the human-facing README and the single-role specs.

This is a project to have a full team of agents work together on the shared goal of winning a Kaggle Machine Learning Competition in the Playground Series.

A Kaggle competition is a hosted ML benchmark where you train on a provided dataset and submit test-set predictions to a leaderboard. The Playground Series is the lightweight tabular version: small, fast, recurring competitions that emphasise experimentation over domain knowledge. In practice, they are mostly exercises in validation, feature engineering, model diversity, and ensembling.

The current competition is **Predict Customer Churn** (S6E3). Submissions are evaluated on area under the ROC curve between the predicted probability and the observed target.

Leaderboard scores are calculated with approximately 20% of the test data. The final results will be based on the other 80%, so the final standings may differ. There is a limit of **5 submissions per day**.

---

## The Team

Persistent roles:

- **Supervisor** — strategic orchestrator and human interface. Synthesises signals from all other agents, consumes strategist recommendations, sets direction, commissions analysis, decides what to submit, and maintains leaderboard history. Runs the setup phase before the main loop begins.
- **Scientist** — experiment engine. Re-enters on `/loop` wakes, iterates on `agents/scientist/experiment.py`, and advances the supervisor's current lane of work within the fixed evaluation harness.
- **Analyst** — signal quality expert. Inspects model artifacts and data to answer targeted yes/no hypotheses and surfaces patterns the scientist's loop cannot see.

Episodic role:

- **Strategist** — long-horizon planning role. Produces `agents/strategist/strategy-whitepaper.md` and maintains `agents/strategist/strategy-idea-cookbook.md`. The strategist recommends; the supervisor decides.

---

## Operating Rules

- The supervisor coordinates strategy and owns submission timing, submission notes, and leaderboard bookkeeping.
- The supervisor does not inspect raw dataset files itself. If it needs dataset evidence, it asks the analyst.
- The strategist recommends the high-level plan. The supervisor translates that plan into operational guidance for the scientist and the rest of the team.
- The analyst answers one active, falsifiable hypothesis at a time. Hypotheses should be yes/no questions tied to a concrete decision.
- The analyst presents evidence in code, tables, counts, and metrics. Do not use plots unless the human explicitly asks.
- The scientist follows the supervisor's current lane. CV is the default local scorekeeper, not the sole objective.
- No agent installs packages, modifies dependencies, or changes the environment on its own.
- If an agent needs a new package, new permission, or any capability it does not already have, it asks the human.

---

## Shared Runtime Assumptions

- The human starts the supervisor first. The supervisor provisions the run tag, branches, worktrees, and initial tracked communication files before the rest of the team begins normal work.
- The strategist is on-demand, not permanently polling. It is consulted at startup and whenever strategic replanning is needed.
- Per-agent Claude settings belong in untracked `.claude/settings.local.json` files inside the current repo or worktree.
- The committed [`.claude/settings.json`](../.claude/settings.json) is shared and must stay path-free.
- Coordination in this repository is polling-based. Do not rely on file hooks or sentinel writes as part of the documented control flow.
- `/loop` scheduled tasks are session-scoped, fire only while Claude is open and idle, and expire after 3 days. If `/loop` is unavailable or scheduled tasks are disabled, the affected agent must tell the human immediately.

---

## Directory Layout

`<root>` is the parent directory where the repository lives (for example `~/dev`). All worktrees share the same `.git` object store.

```text
<root>/
  AutoKaggle/                        # main repo and supervisor's directory
    agents/
      program.md                     # shared agent contract
      supervisor/
        role.md
        leaderboard-history.md       # supervisor-owned submission ledger
        submission.py                # supervisor-owned submission prep helper
      strategist/
        role.md
        strategy-whitepaper.md
        strategy-idea-cookbook.md
      scientist/
        role.md
        experiment.py
        scientist-guidance.md        # shared inbox written by supervisor
      analyst/
        role.md
        analysis.py
        analyst-hypotheses.md        # shared inbox written by supervisor
    harness/                         # shared harness code
    data/                            # competition data (untracked, shared)
    artifacts/<tag>/                 # run artifacts (untracked, shared)
      experiments/<hash>/
        run.log
        exit-code.txt
        oof-preds.npy
        model.pkl
        test-preds.npy

  AutoKaggle-<tag>-scientist/        # scientist worktree
  AutoKaggle-<tag>-analyst/          # analyst worktree
```

The supervisor has no separate worktree. It works from `AutoKaggle/` directly, on branch `autokaggle/<tag>/supervisor`.

---

## Communication Files

All inter-agent coordination flows through files committed on each agent's branch, read by others through paths resolved dynamically at runtime from the repo and worktree layout.

| File | Owned by | Read by | Lives in |
|------|----------|---------|----------|
| `agents/strategist/strategy-whitepaper.md` | Strategist | Supervisor | `AutoKaggle/` |
| `agents/strategist/strategy-idea-cookbook.md` | Strategist | Strategist, Supervisor | `AutoKaggle/` |
| `agents/scientist/scientist-guidance.md` | Supervisor | Scientist | `AutoKaggle/` |
| `agents/analyst/analyst-hypotheses.md` | Supervisor | Analyst | `AutoKaggle/` |
| `agents/supervisor/leaderboard-history.md` | Supervisor | Supervisor, Strategist | `AutoKaggle/` |
| `agents/scientist/scientist-results.md` | Scientist | Supervisor, Analyst | `AutoKaggle-<tag>-scientist/` |
| `agents/analyst/analyst-findings.md` | Analyst | Supervisor | `AutoKaggle-<tag>-analyst/` |

Binary artifacts (`oof-preds.npy`, `model.pkl`, `test-preds.npy`) are never committed. They live in `AutoKaggle/artifacts/<tag>/experiments/<hash>/` and are accessed by all agents via absolute path. Per-run logs and exit-code files may live beside them as untracked local runtime state.

---

## Strategy

### Validation

5-fold cross-validation with a fixed random seed, defined in `harness/dataset.py`. Fold assignments must not change mid-run. This would invalidate cross-experiment comparisons.

CV score is the default local optimisation metric, but it is not the sole objective. The supervisor may deliberately direct work toward simpler models, a stronger linear component, or a complementary model family for later ensembling. The supervisor tracks whether CV gains translate to LB gains in `agents/supervisor/leaderboard-history.md`. If they stop correlating, treat this as a priority signal over chasing further CV improvement.

The strategist decides the current phase using the current date, the competition deadline assumption, and the evidence accumulated so far. The whitepaper should explicitly state the current date, the deadline assumption, and the number of calendar days remaining using absolute dates.

### Experimentation

The scientist runs a `/loop`-driven state machine: start one experiment, let it run, poll it on later wakes, then keep or discard exactly one completed run before starting the next. Direction comes from the supervisor's guidance. The analyst informs strategy indirectly. Findings go to the supervisor, which distils them into guidance for the scientist. Analyst work should resolve concrete yes/no questions and report evidence in tables and metrics, not plots.

### Promotion

The supervisor submits selectively: clear score jumps or meaningfully different approaches. There are only 5 Kaggle submissions per day. Late in a competition it may be worth using submissions to extract LB signal even on smaller improvements.

### Stop Protocol

An explicit human `stop` overrides every autonomy instruction in the role specs.

When `stop` is given, every agent should:

1. Stop taking new work immediately.
2. Cancel any active `/loop` scheduled task it started.
3. Do not create any new scheduled tasks.
4. Finish only the current atomic checkpoint.
5. Commit its owned status files if needed.
6. Report a final status note, then go idle or exit.

There is no automatic stopping condition besides an explicit human stop.
