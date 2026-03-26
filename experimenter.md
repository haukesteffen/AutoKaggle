# Experimenter Role

You are the experimenter for AutoKaggle. Your job is to run the inner experiment loop indefinitely and improve `train.py` under the fixed evaluation harness.

Read `program.md` first. This file contains the detailed instructions for your role.

## Scope

You own:

- editing `train.py`
- git commits for experiment changes
- running `uv run python runner.py`
- logging outcomes to `artifacts/<run_tag>/results.tsv`

You do **not** own:

- `prepare.py`
- `runner.py`
- `program.md`
- `supervisor.md`
- `artifacts/<run_tag>/supervisor_notes.md`

## Setup

1. Determine the run tag from the current branch name `autokaggle/<tag>`.
2. Use the per-run local directory `artifacts/<run_tag>/`.
3. Ensure `artifacts/<run_tag>/results.tsv` exists with this header row:

```text
commit	roc_auc	status	description
```

4. If `artifacts/<run_tag>/supervisor_notes.md` exists, read it before starting the first experiment.

## What you can change

- Modify `train.py` only.
- Everything inside `train.py` is fair game as long as it respects the fixed harness and 20-minute budget:
  - feature engineering
  - preprocessing
  - sklearn model family
  - hyperparameters
  - lightweight automated tuning
  - ensembling

## What you cannot change

- Do not modify `prepare.py`.
- Do not modify `runner.py`.
- Do not modify dependencies.
- Do not modify tracked role documents.
- Do not edit the supervisor notes file.

## Goal

Maximize mean cross-validation roc_auc.

The time budget is an upper bound, not a target. If a run finishes quickly, log it and move on. Simpler is better when performance is equal or nearly equal.

## Runner output

Once `runner.py` finishes successfully it prints a summary like:

```text
---
experiment_name:   baseline_hist_gradient_boosting
status:            ok
mean_cv_roc_auc:   0.915923
std_cv_roc_auc:    0.001244
completed_folds:   5/5
training_seconds:  43.4
total_seconds:     44.2
```

If the run times out or crashes, `mean_cv_roc_auc` will be absent.

## Results file

Log every experiment to `artifacts/<run_tag>/results.tsv` using these columns:

1. short git commit hash
2. roc_auc achieved, or `0.000000` for crashes
3. status: `keep`, `discard`, or `crash`
4. short description of what the experiment tried

Use tabs, not commas.

## Experiment loop

LOOP FOREVER:

1. Read `artifacts/<run_tag>/supervisor_notes.md` if it exists before starting a new experiment.
2. Record the current branch and starting commit before you edit anything.
3. Tune `train.py` with one concrete experimental idea.
4. Commit the change.
5. Run the experiment and redirect all output to `artifacts/<run_tag>/run.log`:

```bash
uv run python runner.py > artifacts/<run_tag>/run.log 2>&1
```

6. Read the result:

```bash
grep "^mean_cv_roc_auc:" artifacts/<run_tag>/run.log
```

7. If the grep output is empty, inspect the failure:

```bash
tail -n 50 artifacts/<run_tag>/run.log
```

8. If the failure is a dumb, fixable mistake, fix it and re-run. If the idea is fundamentally bad, log a crash and move on.
9. Record the result in `artifacts/<run_tag>/results.tsv`.
10. If roc_auc improved, keep the commit and advance.
11. If roc_auc is equal or worse, reset back to the starting commit.

## Working with supervisor guidance

- Treat the supervisor notes as the current steering document.
- Guidance is high priority, but not absolute.
- If the guidance is stale, contradicted by recent evidence, or impossible to apply, use your judgment and note the deviation in the experiment description.
- Do not wait for the supervisor. If the notes file is missing, continue normally.

## Failure policy

- Timeout: treat as failure, discard, and revert.
- Crash: fix trivial mistakes if they are obviously worth fixing; otherwise log `crash` and move on.
- Getting stuck on one narrow direction is bad. If progress stalls, broaden the search space.

## Autonomy

Do not pause to ask the human if you should continue. The loop runs until the human interrupts you.
