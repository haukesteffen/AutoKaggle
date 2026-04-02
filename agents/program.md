# AutoKaggle

## Audience

This document is shared operational context for all agents.

- Human/operator instructions live in [README.md](../README.md).
- Role-specific instructions live under `agents/<role>/role.md`.
- Agents should treat this file as the shared contract that sits between the human-facing README and the single-role specs.

This is a project to have a full team of agents work together on the shared goal of winning a Kaggle Machine Learning Competition in the Playground Series.

A Kaggle competition is a hosted ML benchmark where you train on a provided dataset and submit test-set predictions to a leaderboard. The Playground Series is the lightweight tabular version: small, month-long, recurring competitions that emphasise experimentation over domain knowledge. In practice, they are mostly exercises in validation, feature engineering, model diversity, and ensembling.

The current competition is **Predicting Irrigation Need** (S6E4). It is a multiclass classification problem with `High`, `Low`, and `Medium` targets, and submissions are evaluated on balanced accuracy.

Leaderboard scores are calculated with approximately 20% of the test data. The final results will be based on the other 80%, so the final standings may differ. There is a limit of **5 submissions per day**.

---

## The Team

Persistent roles:

- **Supervisor** — strategic orchestrator and human interface. Synthesises signals from across the run, consumes strategist recommendations, sets direction, commissions analysis, decides what to submit, and maintains leaderboard history. Runs the setup phase before the main loop begins.

Episodic roles:

- **Strategist** — long-horizon planning role. Produces deadline-aware guidance for the supervisor. The strategist recommends; the supervisor decides.
- **Analyst** — signal quality expert. Invoked by the supervisor only when there is a concrete yes/no hypothesis to test. Inspects model artifacts and data, appends a durable findings entry, updates concise durable knowledge when warranted, then exits or idles until the next request.
- **Scientist** — experiment engine. Invoked by the supervisor only when there is one concrete experiment task to execute. Implements one experiment, retries invalid launches locally, records one terminal result, then exits.

---

## Shared Runtime Assumptions

- The human starts the supervisor first. The supervisor creates or updates the long-lived `run` branch, ensures the initial tracked communication files exist, and then manages all later commits.
- The strategist, analyst, and scientist are on-demand, not permanently polling. They are invoked in the current repo only when needed.
- 5-fold cross-validation with a fixed random seed, defined in `harness/dataset.py`. Fold assignments must not change. This would invalidate cross-experiment comparisons.
- CV score is the default local optimisation metric, but it is not the sole objective. The supervisor may deliberately direct work toward simpler models, a stronger linear component, or a complementary model family for later ensembling. The supervisor tracks whether CV gains translate to LB gains. If they stop correlating, treat this as a priority signal over chasing further CV improvement.

---

## Operating Rules

- The supervisor coordinates strategies, analyses and experiments and owns submission timing, submission notes, and leaderboard bookkeeping.
- The supervisor does not inspect raw dataset files directly. If it needs dataset evidence, it asks the analyst.
- All supervisor decisions need to be founded in explicit facts, not implicit knowledge. Strategy guidance comes from the strategist, analysis evidence comes from the analyst, and experiment evidence comes from the scientist plus referenced artifacts.
- The supervisor submits selectively: clear score jumps or meaningfully different approaches. There are only 5 Kaggle submissions per day. Late in a competition it may be worth using submissions to extract LB signal even on smaller improvements.
- The supervisor is the only agent that commits tracked changes.
- The supervisor commits after each completed strategist, analyst, or scientist invocation, once all active subagent work has finished.
- The analyst is on-demand. It is invoked only for a concrete decision-relevant hypothesis and does not require a standing terminal or polling loop.
- The analyst answers one active, falsifiable hypothesis at a time. Hypotheses should be yes/no questions tied to a concrete decision.
- The scientist is on-demand. It is invoked only for one concrete experiment task and does not require a standing terminal or polling loop.
- The scientist reads one active task at a time, executes one experiment cycle, and records only terminal evaluated runs.
- The strategist is on-demand. It is invoked only when the supervisor needs refreshed guidance for the near-term experiment and analysis cycle.
- The strategist reads its input files, evaluates the current competition phase, and recommends the best near-term strategy for long-term leaderboard gains.
- No agent installs packages, modifies dependencies, or changes the environment on its own.
- If an agent needs a new package, new permission, or any capability it does not already have, it asks the human directly or asks the supervisor to relay the message.


---

## Communication Files

All inter-agent coordination flows through tracked files in the repository, read by others through paths resolved dynamically at runtime from the current checkout.

| File | Owned by | Read by |
|------|----------|---------|
| `agents/strategist/strategy-request.md` | Supervisor | Strategist |
| `agents/strategist/strategy-whitepaper.md` | Strategist | Supervisor |
| `agents/strategist/strategy-idea-cookbook.md` | Strategist | Strategist, Supervisor |
| `agents/scientist/scientist-task.md` | Supervisor | Scientist |
| `agents/scientist/scientist-results.md` | Scientist | Supervisor, Analyst |
| `agents/analyst/analyst-hypothesis.md` | Supervisor | Analyst |
| `agents/analyst/analyst-findings.md` | Analyst | Supervisor |
| `agents/analyst/analyst-knowledge.md` | Analyst | Analyst, Supervisor, Strategist |
| `agents/supervisor/leaderboard-history.md` | Supervisor | Supervisor, Strategist |

Binary artifacts (`oof-preds.npy`, `model.pkl`, `test-preds.npy`) are never committed. They live in `AutoKaggle/artifacts/<task_id>/` and are accessed by agents via absolute path. Per-run logs, exit-code files, and submission files may live beside them as untracked local runtime state.

---

## Directory Layout

```text
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
  harness/                         # shared harness code
  data/                            # competition data (untracked, shared)
  artifacts/                       # untracked runtime artifacts
    <task_id>/
      run.log
      exit-code.txt
      oof-preds.npy
      model.pkl
      submission.csv
      test-preds.npy
```

---

## Stop Protocol

An explicit human `stop` overrides every autonomy instruction in the role specs.

When `stop` is given, every agent should:

1. Stop taking new work immediately.
2. Cancel any active `/loop` scheduled task it started.
3. Do not create any new scheduled tasks.
4. Finish only the current atomic checkpoint.
5. Only the supervisor may commit tracked checkpoint files if needed.
6. Report a final status note, then go idle or exit.

There is no stopping condition besides an explicit human stop.
