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

- **Supervisor** — strategic orchestrator and human interface. Synthesises signals from across the run, consumes strategist recommendations, sets direction, commissions analysis, decides what to submit, and maintains leaderboard history. Runs the setup phase before the main loop begins.

Episodic roles:

- **Strategist** — long-horizon planning role. Produces `agents/strategist/strategy-whitepaper.md`, maintains `agents/strategist/strategy-lifecycle-guide.md` and `agents/strategist/strategy-idea-cookbook.md`, and reads the supervisor-owned `agents/strategist/strategy-request.md`. The strategist recommends; the supervisor decides.
- **Analyst** — signal quality expert. Invoked by the supervisor only when there is a concrete yes/no hypothesis to test. Inspects model artifacts and data, appends a durable findings entry, updates concise durable knowledge when warranted, then exits or idles until the next request.
- **Scientist** — experiment engine. Invoked by the supervisor only when there is one concrete experiment task to execute. Implements one experiment, retries invalid launches locally, records one terminal result, updates concise durable knowledge when warranted, then exits.

---

## Operating Rules

- The supervisor coordinates strategy and owns submission timing, submission notes, and leaderboard bookkeeping.
- The supervisor does not inspect raw dataset files itself. If it needs dataset evidence, it asks the analyst.
- The supervisor should treat unverified empirical claims as hypotheses. If a claim is decision-relevant and not already supported by experiment results, leaderboard history, or analyst output, route it to the analyst before acting on it.
- The supervisor owns `agents/strategist/strategy-request.md`. The request is factual. The whitepaper is interpretive.
- The strategist recommends the high-level plan. The supervisor translates that plan into operational guidance for the scientist and the rest of the team.
- The strategist normally reads the strategy request, durable analyst knowledge, durable scientist knowledge, and leaderboard history. It does not need to reread raw findings and result histories on every refresh.
- Early thin coverage is a strategy problem even if current CV is improving.
- When time is abundant, no major cookbook area should remain completely untested.
- The analyst is on-demand. It is invoked only for concrete decision-relevant hypotheses and does not require a standing terminal or polling loop.
- The analyst answers one active, falsifiable hypothesis at a time. Hypotheses should be yes/no questions tied to a concrete decision.
- The analyst presents evidence in code, tables, counts, and metrics. Findings should stay neutral and factual. Do not use plots unless the human explicitly asks.
- The scientist is on-demand. It is invoked only for one concrete experiment task and does not require a standing terminal or polling loop.
- The scientist reads one active task at a time, executes one experiment cycle, and records only terminal evaluated runs in `agents/scientist/scientist-results.md`.
- Invalid scientist launches are repaired inside the same invocation and do not count as completed experiment results.
- The scientist follows the supervisor's current lane. CV is the default local scorekeeper, not the sole objective.
- The supervisor is the only agent that commits tracked changes.
- The supervisor commits only at quiescent points, after all active strategist, analyst, and scientist work has finished.
- `agents/scientist/scientist-task.md` and `agents/analyst/analyst-hypothesis.md` are tracked live-control files, but they should normally be cleared back to `status: none` before the supervisor commits a checkpoint.
- No agent installs packages, modifies dependencies, or changes the environment on its own.
- If an agent needs a new package, new permission, or any capability it does not already have, it asks the human.

---

## Shared Runtime Assumptions

- The human starts the supervisor first. The supervisor creates or updates the long-lived `run` branch, ensures the initial tracked communication files exist, and then manages all later commits.
- The strategist, analyst, and scientist are on-demand, not permanently polling. They are invoked in the current repo only when needed.
- Per-agent Claude settings belong in untracked `.claude/settings.local.json` files inside the current repo.
- The committed [`.claude/settings.json`](../.claude/settings.json) is shared and must stay path-free.
- Coordination in this repository is polling-based. Do not rely on file hooks or sentinel writes as part of the documented control flow.

---

## Directory Layout

`<root>` is the parent directory where the repository lives (for example `~/dev`).

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
        strategy-lifecycle-guide.md
        strategy-request.md          # supervisor-owned factual strategist input
        strategy-whitepaper.md
        strategy-idea-cookbook.md
      analyst/
        role.md
        analysis.py
        analyst-hypothesis.md        # supervisor-owned active request
        analyst-findings.md          # append-only durable findings history
        analyst-knowledge.md         # concise durable analyst memory
      scientist/
        role.md
        experiment.py
        scientist-task.md            # supervisor-owned active task
        scientist-results.md         # append-only terminal run history
        scientist-knowledge.md       # concise durable scientist memory
    harness/                         # shared harness code
    data/                            # competition data (untracked, shared)
    artifacts/                       # untracked runtime artifacts
      experiments/<hash>/
        run.log
        exit-code.txt
        oof-preds.npy
        model.pkl
        test-preds.npy
```

---

## Communication Files

All inter-agent coordination flows through tracked files in the repository, read by others through paths resolved dynamically at runtime from the current checkout.

| File | Owned by | Read by | Lives in |
|------|----------|---------|----------|
| `agents/strategist/strategy-request.md` | Supervisor | Strategist | `AutoKaggle/` |
| `agents/strategist/strategy-whitepaper.md` | Strategist | Supervisor | `AutoKaggle/` |
| `agents/strategist/strategy-idea-cookbook.md` | Strategist | Strategist, Supervisor | `AutoKaggle/` |
| `agents/scientist/scientist-task.md` | Supervisor | Scientist | `AutoKaggle/` |
| `agents/analyst/analyst-hypothesis.md` | Supervisor | Analyst | `AutoKaggle/` |
| `agents/analyst/analyst-findings.md` | Analyst | Supervisor | `AutoKaggle/` |
| `agents/analyst/analyst-knowledge.md` | Analyst | Analyst, Supervisor, Strategist | `AutoKaggle/` |
| `agents/supervisor/leaderboard-history.md` | Supervisor | Supervisor, Strategist | `AutoKaggle/` |
| `agents/scientist/scientist-results.md` | Scientist | Supervisor, Analyst | `AutoKaggle/` |
| `agents/scientist/scientist-knowledge.md` | Scientist | Scientist, Supervisor, Strategist | `AutoKaggle/` |

Binary artifacts (`oof-preds.npy`, `model.pkl`, `test-preds.npy`) are never committed. They live in `AutoKaggle/artifacts/experiments/<hash>/` and are accessed by all agents via absolute path. Per-run logs and exit-code files may live beside them as untracked local runtime state.

---

## Strategy

### Validation

5-fold cross-validation with a fixed random seed, defined in `harness/dataset.py`. Fold assignments must not change mid-run. This would invalidate cross-experiment comparisons.

CV score is the default local optimisation metric, but it is not the sole objective. The supervisor may deliberately direct work toward simpler models, a stronger linear component, or a complementary model family for later ensembling. The supervisor tracks whether CV gains translate to LB gains in `agents/supervisor/leaderboard-history.md`. If they stop correlating, treat this as a priority signal over chasing further CV improvement.

The supervisor refreshes `agents/strategist/strategy-request.md` from factual run state and durable knowledge. The strategist then computes the current date, the deadline assumption, the number of calendar days remaining, and the current emphasis across the full cycle. The whitepaper should explicitly state the current date, the deadline assumption, and the number of calendar days remaining using absolute dates.

### Experimentation

The scientist is invoked only when the supervisor has one concrete experiment task to execute. Each scientist invocation should implement one experiment, retry invalid launches locally, and end only after the run reaches a terminal outcome that has been recorded in `agents/scientist/scientist-results.md`. Durable reusable scientist facts go in `agents/scientist/scientist-knowledge.md`. The analyst is invoked only when the supervisor has a concrete yes/no question to resolve. Findings go to the supervisor through `agents/analyst/analyst-findings.md`, which remains append-only and reviewable across invocations. Durable reusable analyst facts go in `agents/analyst/analyst-knowledge.md`. Analyst work should resolve concrete hypotheses and report neutral evidence in tables and metrics, not plots.

### Promotion

The supervisor submits selectively: clear score jumps or meaningfully different approaches. There are only 5 Kaggle submissions per day. Late in a competition it may be worth using submissions to extract LB signal even on smaller improvements.

### Stop Protocol

An explicit human `stop` overrides every autonomy instruction in the role specs.

When `stop` is given, every agent should:

1. Stop taking new work immediately.
2. Cancel any active `/loop` scheduled task it started.
3. Do not create any new scheduled tasks.
4. Finish only the current atomic checkpoint.
5. Only the supervisor may commit tracked checkpoint files if needed.
6. Report a final status note, then go idle or exit.

There is no automatic stopping condition besides an explicit human stop.
