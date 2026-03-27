# AutoKaggle

This is a project to have a full team of agents work together on the shared goal of winning a Kaggle Machine Learning Competition in the Playground Series.

A Kaggle competition is a hosted ML benchmark where you train on a provided dataset and submit test-set predictions to a leaderboard. The Playground Series is the lightweight tabular version: small, fast, recurring competitions that emphasise experimentation over domain knowledge. In practice, they are mostly exercises in validation, feature engineering, model diversity, and ensembling.

The current competition is **Predict Customer Churn** (S6E3). Submissions are evaluated on area under the ROC curve between the predicted probability and the observed target.

Leaderboard scores are calculated with approximately 20% of the test data. The final results will be based on the other 80%, so the final standings may differ. There is a limit of **5 submissions per day**.

---

## The Team

Four roles, each running as an independent Claude Code session:

- **Supervisor** — strategic orchestrator and human interface. Synthesises signals from all other agents, sets direction, commissions analysis, and promotes experiments to the leaderboard. Runs the setup phase before the main loop begins.
- **Scientist** — experiment engine. Iterates on `experiment.py` within the fixed evaluation harness to advance the supervisor's current lane of work.
- **Analyst** — signal quality expert. Inspects model artifacts and data to answer targeted yes/no hypotheses and surfaces patterns the scientist's loop cannot see.
- **Engineer** — submission pipeline. Turns promoted experiment artifacts into Kaggle submissions and tracks CV/LB correlation.

---

## Operating Rules

- The supervisor coordinates strategy. It does not inspect raw dataset files itself. If it needs dataset evidence, it asks the analyst.
- The analyst answers one active, falsifiable hypothesis at a time. Hypotheses should be yes/no questions tied to a concrete decision.
- The analyst presents evidence in code, tables, counts, and metrics. Do not use plots unless the human explicitly asks.
- The scientist follows the supervisor's current lane. CV is the default local scorekeeper, not the sole objective.
- No agent installs packages, modifies dependencies, or changes the environment on its own.
- If an agent needs a new package, new permission, or any capability it does not already have, it asks the human.

---

## Starting a Run

### Step 1 — Start the supervisor

Navigate to the repository root and start a Claude Code session:

```bash
cd <root>/AutoKaggle
claude
```

Tell the supervisor: **"Start a new run."**

The supervisor will:
1. Propose a run tag (confirm or suggest an alternative)
2. Create all branches and worktrees
3. Download competition data if not already present
4. Initialise communication files
5. Tell you exactly what commands to run for the other three agents

### Step 2 — Start the other three agents

Once the supervisor gives you the go-ahead, open three new terminal sessions and run the commands it provides. They will be in the form:

```bash
# Terminal 2
cd <root>/AutoKaggle-<tag>-scientist && claude

# Terminal 3
cd <root>/AutoKaggle-<tag>-analyst && claude

# Terminal 4
cd <root>/AutoKaggle-<tag>-engineer && claude
```

Each agent reads its own role spec, bootstraps its local Claude settings, and begins autonomously. Tell the supervisor when all three are running — it will then start the hook-driven run.

### Step 3 — Let each agent bootstrap local Claude settings

Each agent should ask once, early, for permission to create or update `.claude/settings.local.json` in its current worktree. Use this untracked local file for per-agent permissions, `permissions.additionalDirectories`, and hook registration. Do not invent a top-level `directories` key.

Keep the committed `.claude/settings.json` path-free and shared. Keep any machine-specific full filesystem paths only in local settings derived at runtime from the current repo and branch layout.

For `FileChanged` hooks, use basename matchers such as `analyst-hypotheses.md` or `engineer-promotions.md`, not full filesystem paths in the `matcher` field.

After bootstrapping local settings, each agent should run both `/status` and `/hooks` and confirm that the local settings layer is active and the expected hooks are present.

### Step 4 — Verify hooks before calling the run live

After all three role sessions are running and have bootstrapped local settings, the supervisor sends one sentinel update to each hook-driven inbox file:

- `analyst-hypotheses.md` gets a `startup-check` hypothesis
- `engineer-promotions.md` gets a `startup-check` row

The receiving agent must acknowledge that sentinel before normal work starts. Do not consider the run live until those smoke tests pass.

---

## Directory Layout

`<root>` is the parent directory where the repository lives (e.g. `~/dev`). All worktrees share the same `.git` object store.

```
<root>/
  AutoKaggle/                        # main repo and supervisor's directory
    harness/                         # shared harness code
    roles/                           # role specifications
    experiment.py                    # scientist's editable file
    promotion.py                     # engineer's editable file
    data/                            # competition data (untracked, shared)
    artifacts/<tag>/                 # run artifacts (untracked, shared)
      run.log
      experiments/<hash>/
        oof-preds.npy
        model.pkl
        test-preds.npy

  AutoKaggle-<tag>-scientist/        # scientist worktree
  AutoKaggle-<tag>-analyst/          # analyst worktree
  AutoKaggle-<tag>-engineer/         # engineer worktree
```

The supervisor has no separate worktree — it works from `AutoKaggle/` directly, on branch `autokaggle/<tag>/supervisor`.

---

## Communication Files

All inter-agent coordination flows through files committed on each agent's branch, read by others through paths resolved dynamically at runtime from the repo and worktree layout.

| File | Owned by | Read by | Lives in |
|------|----------|---------|----------|
| `scientist-guidance.md` | Supervisor | Scientist | `AutoKaggle/` |
| `analyst-hypotheses.md` | Supervisor | Analyst | `AutoKaggle/` |
| `engineer-promotions.md` | Supervisor | Engineer | `AutoKaggle/` |
| `scientist-results.md` | Scientist | Supervisor, Analyst | `AutoKaggle-<tag>-scientist/` |
| `analyst-findings.md` | Analyst | Supervisor | `AutoKaggle-<tag>-analyst/` |
| `engineer-submissions.md` | Engineer | Supervisor | `AutoKaggle-<tag>-engineer/` |

Binary artifacts (`oof-preds.npy`, `model.pkl`, `test-preds.npy`) are never committed. They live in `AutoKaggle/artifacts/<tag>/experiments/<hash>/` and are accessed by all agents via absolute path.

---

## Strategy

### Validation

5-fold cross-validation with a fixed random seed, defined in `harness/dataset.py`. Fold assignments must not change mid-run — this would invalidate cross-experiment comparisons.

CV score is the default local optimisation metric, but it is not the sole objective. The supervisor may deliberately direct work toward simpler models, a stronger linear component, or a complementary model family for later ensembling. The engineer tracks whether CV gains translate to LB gains. If they stop correlating, the supervisor treats this as a priority signal over chasing further CV improvement.

### Experimentation

The scientist runs a tight loop: one idea, one commit, one 20-minute run, keep or discard. Direction comes from the supervisor's guidance. The analyst informs strategy indirectly — findings go to the supervisor, which distils them into guidance for the scientist. Analyst work should resolve concrete yes/no questions and report evidence in tables and metrics, not plots.

### Promotion

The supervisor promotes selectively — clear score jumps or meaningfully different approaches. There are only 5 Kaggle submissions per day. Late in a competition it may be worth using submissions to extract LB signal even on smaller improvements.

### Ending a Run

A run ends when the human says `stop`. This overrides every autonomy instruction in the role specs.

When `stop` is given, each agent should:

1. Stop taking new work immediately.
2. Disable its hooks in `.claude/settings.local.json`.
3. Cancel any active polling or keepalive loop it started.
4. Finish only the current atomic checkpoint.
5. Commit its owned status files if needed.
6. Report a final status note, then go idle or exit.

There is no automatic stopping condition besides an explicit human stop.
