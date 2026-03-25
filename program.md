# autokaggle

This is an experiment to have an Agent compete in Kaggle's Playground Competition "Predict Customer Churn" (S6E3).

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar5`). The branch `autokaggle/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: First confirm this directory is actually a git repo, then create `autokaggle/<tag>` from the current default branch.
3. **Read the in-scope files**: The repo is small. Read these files for full context:
   - `README.md` — repository context.
   - `prepare.py` — fixed constants, data prep, cross-validation harness. Do not modify.
   - `runner.py` — fixed experiment entrypoint, timeout handling. Do not modify.
   - `train.py` — the file you modify. Preprocessing, features, hyperparameters.
   - If any of `README.md`, `runner.py`, `train.py`, or `pyproject.toml` are missing, stop and tell the human the repo is not ready for autonomous runs yet.
4. **Verify data exists**: Check that `./data/` contains train set, test set and cross-validation ids. If not, tell the human to run `uv run python prepare.py`.
5. **Initialize results.tsv**: Create `results.tsv` with just the header row. The baseline will be recorded after the first run.
6. **Confirm and go**: Confirm setup looks good.

Once you get confirmation, kick off the experimentation.

## Experimentation

Each experiment runs on the local cpu. The runner enforces a **hard time budget of 20 minutes** (wall clock training time, excluding startup/compilation). You launch one experiment as: `uv run python runner.py`.

**What you CAN do:**
- Modify `train.py` — this is the only file you edit. Everything is fair game inside the single-experiment model definition: feature engineering, preprocessing, and hyperparameters. You want to build the best-performing binary classification model.

**What you CANNOT do:**
- Modify `prepare.py`. It is read-only. It contains the data loading and fixed cross-validation splitting.
- Modify `runner.py`. It is read-only. It contains the experiment entrypoint, timeout handling, and result reporting.
- Install new packages or add dependencies. You can only use what's already in `pyproject.toml`.
- Modify the evaluation harness. The `evaluate_model` function in `prepare.py` and the timeout logic in `runner.py` are the ground truth protocol.

**The goal is simple: get the highest mean area under the receiver operating characteristic curve (roc_auc) across cross-validation folds.** The time budget is an upper bound, not a target. If a run finishes in one minute, log it and move on to the next experiment. The only constraints are that the code runs without crashing and finishes within the time budget.

**Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude. A 0.00001 roc_auc improvement that adds 20 lines of hacky code? Probably not worth it. A 0.00001 roc_auc improvement from deleting code? Definitely keep. An improvement of ~0 but much simpler code? Keep.

**The first run**: Your very first run should always be to establish the baseline, so you will run the baseline experiment as is through `runner.py`.

## Output format

Once the runner finishes successfully it prints a summary like this:

```
---
experiment_name:   baseline_hist_gradient_boosting
status:            ok
mean_cv_roc_auc:   0.915923
std_cv_roc_auc:    0.001244
completed_folds:   5/5
training_seconds:  43.4
total_seconds:     44.2
```

If a run times out or crashes, `mean_cv_roc_auc` will be absent from the log. You can extract the key metric from a successful run with:

```bash
grep "^mean_cv_roc_auc:" run.log
```

## Logging results

When an experiment is done, log it to `results.tsv` (tab-separated, NOT comma-separated — commas break in descriptions).

The TSV has a header row and 4 columns:

```
commit  roc_auc status description
```

1. git commit hash (short, 7 chars)
2. roc_auc achieved (e.g. 0.915923) — use 0.000000 for crashes
3. status: `keep`, `discard`, or `crash`
4. short text description of what this experiment tried

Example:

```
commit	roc_auc	status	description
a1b2c3d	0.914900    keep	baseline
b2c3d4e	0.915201	keep	change max_depth to 4
c3d4e5f	0.883325	discard	add categorical feature crosses
d4e5f6g	0.000000	crash	optuna tuning (thread contention)
```

## The experiment loop

The experiment runs on a dedicated branch (e.g. `autokaggle/mar5` or `autokaggle/mar5-cpu0`).

LOOP FOREVER:

1. Look at the git state: record the current branch and starting commit before you edit anything
2. Tune `train.py` with an experimental idea by directly hacking the code.
3. git commit
4. Run the experiment: `uv run python runner.py > run.log 2>&1` (redirect everything — do NOT use tee or let output flood your context)
5. Read out the results: `grep "^mean_cv_roc_auc:" run.log`
6. If the grep output is empty, the run timed out or crashed. Run `tail -n 50 run.log` to read the timeout summary or Python stack trace and attempt a fix. If you can't get things to work after more than a few attempts, give up.
7. Record the results in the tsv (NOTE: do not commit the results.tsv file, leave it untracked by git)
8. If roc_auc improved (higher), you "advance" the branch, keeping the git commit
9. If roc_auc is equal or worse, reset back to the starting commit you recorded before the experiment

The idea is that you are a completely autonomous researcher trying things out. If they work, keep. If they don't, discard. And you're advancing the branch so that you can iterate. If you feel like you're getting stuck in some way, you can rewind but you should probably do this very very sparingly (if ever).

**Timeout**: Each experiment must finish within 20 minutes of training time. If the runner kills it for exceeding the budget, treat it as a failure (discard and revert).

**Crashes**: If a run crashes (OOM, or a bug, or etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log "crash" as the status in the tsv, and move on.

**NEVER STOP**: Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human might be asleep, or gone from a computer and expects you to continue working *indefinitely* until you are manually stopped. You are autonomous. If you run out of ideas, think harder — read papers referenced in the code, re-read the in-scope files for new angles, try combining previous near-misses, try more radical architectural changes. The loop runs until the human interrupts you, period.

As an example use case, a user might leave you running while they sleep. If each experiment takes you ~20 minutes then you can run approx 3/hour, for a total of about 24 over the duration of the average human sleep. The user then wakes up to experimental results, all completed by you while they slept!
