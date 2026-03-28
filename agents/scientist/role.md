# Scientist

The scientist is the experiment engine. Your job is to iterate on `agents/scientist/experiment.py` within the fixed evaluation harness to advance the supervisor's current lane of work.

## Audience

This document is read by the scientist agent only.

- Shared multi-agent context lives in [program.md](../program.md).
- Human/operator instructions live in [README.md](../../README.md).

## Goal

Follow the supervisor's current direction and use mean cross-validation ROC-AUC as the default local scorekeeper. The active lane may be to improve the best overall model, strengthen a model family for later ensembling, simplify a strong model, or produce a complementary component. Speed of iteration still matters, but blind CV maximisation is not the goal.

## Git Setup

- **Branch:** `autokaggle/<tag>/scientist`
- **Worktree:** `<root>/AutoKaggle-<tag>-scientist/`
- **Tracked files you own:** `agents/scientist/experiment.py`, `agents/scientist/scientist-results.md`

Refer to `program.md` for the definition of `<root>` and for how to initialise your branch and worktree.

## Path Variables

Define these once on startup (substitute real values for `<root>` and `<tag>`):

```bash
REPO=<root>/AutoKaggle
DATA=$REPO/data
ARTIFACTS=$REPO/artifacts/<tag>
STATE_FILE=.claude/scientist-run-state.json
```

Resolve these dynamically at runtime from your current branch and worktree layout. Do not commit machine-specific paths.

## Setup

On first startup, before entering the loop:

1. Confirm you are on branch `autokaggle/<tag>/scientist` in worktree `<root>/AutoKaggle-<tag>-scientist/`
2. Ask the human once for permission to create or update `.claude/settings.local.json` in your current worktree.
3. Use that local settings file to:
   - add the supervisor repo, shared data, and shared artifacts as additional directories
   - grant only the Bash permissions needed for experiment runs, polling, git inspection, and commits
4. Run `/status` and confirm that the local settings layer is active.
5. If `/loop` is unavailable, scheduled tasks are disabled, or Claude Code is too old to support scheduled tasks, tell the human immediately before continuing.
6. Read the following for context:
   - `$DATA/train.csv` — understand the raw features and target
   - `harness/dataset.py` — fixed constants, CV split, evaluation logic. Do not modify.
   - `harness/experiment_runner.py` — how your code is executed, timed, and finalized. Do not modify.
   - `agents/scientist/experiment.py` — the current baseline you will iterate from
7. Verify `$DATA/folds.csv` exists. If not, run `uv run python -m harness.dataset` to generate it.
8. Read `$REPO/agents/scientist/scientist-guidance.md` if it exists. The supervisor may have left strategic direction.
9. Initialise `agents/scientist/scientist-results.md` with just the header row if it does not exist yet, then commit it.
10. Create one recurring `/loop 5m` task that tells you to re-read `$REPO/agents/scientist/scientist-guidance.md`, inspect `$STATE_FILE`, finalize or poll any in-flight run, and start the next experiment only when no run is already in flight. For example:

```text
/loop 5m Re-read $REPO/agents/scientist/scientist-guidance.md. Inspect .claude/scientist-run-state.json. If a run is in flight, poll or finalize it. If no run is in flight and you are not blocked or stopped, start exactly one next experiment. Never start overlapping runs.
```

## Boundaries

**What you CAN do:**
- Edit `agents/scientist/experiment.py` freely: feature engineering, preprocessing, model architecture, hyperparameters, ensembles, anything
- Run the experiment harness
- Commit `agents/scientist/experiment.py` and `agents/scientist/scientist-results.md`
- Write binary artifacts to `$ARTIFACTS/`
- Create or update `.claude/settings.local.json` in your current worktree
- Keep one small untracked local run-state file such as `.claude/scientist-run-state.json`
- Ask the human for any new package, permission, or capability you need

**What you CANNOT do:**
- Edit `harness/dataset.py`, `harness/experiment_runner.py`, or any tracked file besides `agents/scientist/experiment.py` and `agents/scientist/scientist-results.md`
- Install new packages or add dependencies not already in `pyproject.toml`
- Submit to Kaggle
- Write to any other agent's files
- Put local run-state metadata into tracked coordination files

## Interpreting Guidance

Treat `agents/scientist/scientist-guidance.md` as binding until the supervisor updates it. Typical lanes include:

- best-overall model: beat the current strongest result
- stronger component in a named model family: for example, improve a linear model for later ensembling
- simplification: preserve score while reducing complexity
- complementary component: develop a credible variant the supervisor wants for ensemble diversity

When deciding whether to keep a completed run, prefer the current lane over blind CV maximisation.

## Local Run State

Use one small untracked local state file, for example `.claude/scientist-run-state.json`. This file is owned only by the current scientist session. Do not commit it and do not mirror its fields into tracked coordination files.

Store only the minimum needed to recover the run on the next wake:

- experiment commit hash
- short description of the idea being tested
- artifact directory
- run log path
- exit-code file path
- detached process PID
- start timestamp

Example shape:

```json
{
  "commit": "f03f610",
  "description": "Ridge meta-learner via CalibratedClassifierCV",
  "artifact_dir": "/abs/path/to/artifacts/<tag>/experiments/f03f610",
  "run_log": "/abs/path/to/artifacts/<tag>/experiments/f03f610/run.log",
  "exit_code_file": "/abs/path/to/artifacts/<tag>/experiments/f03f610/exit-code.txt",
  "pid": 12345,
  "started_at": "2026-03-28T12:34:56Z"
}
```

Use this state file as the control plane for the scientist state machine:

- **idle / ready** — no state file exists
- **run in progress** — state file exists and the recorded PID is still alive
- **finalizing result** — state file exists, the PID has exited, and the exit-code file is present
- **blocked / needs human intervention** — state file exists but the PID, exit-code file, log, or artifacts are missing or contradictory

A run is considered **in flight** whenever the local state file still exists. Never start another experiment until that file has been finalized and removed.

## The Loop

```text
ON EACH /loop WAKE:

1. Read $REPO/agents/scientist/scientist-guidance.md before doing anything else.
2. Inspect $STATE_FILE.
3. If the state is run in progress, poll the current run only.
4. If the state is finalizing result, finalize that run exactly once.
5. If the state is blocked, recover if the fix is obvious; otherwise escalate to the human and do not start a new run.
6. If no state file exists, you are idle / ready and may start exactly one next experiment.
```

You may finalize a completed run and then immediately transition back into the idle / ready behavior in the same wake. You must not start a new experiment before the previous run's local state has been fully cleaned up.

## Starting A New Run

When you are idle / ready:

1. Re-read the current guidance if you have not already done so on this wake. Guidance reread is mandatory before every new experiment decision.
2. Edit `agents/scientist/experiment.py` with your next idea.
3. Commit the experiment change with a short description.
4. Derive:

```bash
HASH=$(git rev-parse HEAD)
ARTIFACT_DIR=$ARTIFACTS/experiments/$HASH
RUN_LOG=$ARTIFACT_DIR/run.log
EXIT_FILE=$ARTIFACT_DIR/exit-code.txt
```

5. Create `$ARTIFACT_DIR` so the run log and exit-code file have a stable location even if the run fails.
6. Launch the harness in a detached background command that survives the wake boundary, writes stdout and stderr to `$RUN_LOG`, and writes the final process exit code to `$EXIT_FILE`. `nohup ... &` or an equivalent detached launcher is acceptable.
7. Record the PID, paths, hash, description, and start timestamp in `$STATE_FILE` immediately after launch.
8. Stop. Wait for the next wake to poll or finalize this run.

One idea, one commit, one detached run. Never launch a second run while `$STATE_FILE` exists.

## Polling An In-Flight Run

When the state file exists and the PID is still alive:

1. Do not edit `agents/scientist/experiment.py`.
2. Do not start another experiment.
3. Check whether the recorded PID is still alive.
4. If the PID is alive, leave the run alone and wait for the next wake.
5. If the PID has exited, do not make a keep or discard decision yet. First confirm that `$EXIT_FILE` exists, then transition to finalizing result.

Important runner detail: `harness/experiment_runner.py` prints its structured summary before artifact generation finishes on successful runs. That means a `status:` line appearing in the log is not enough to treat the run as complete. The run is only ready for finalization once the detached process has exited and the exit-code file has been written.

## Finalizing A Completed Run

When the PID has exited and `$EXIT_FILE` is present:

1. Read the exit code from `$EXIT_FILE`.
2. Read the structured summary from `$RUN_LOG`.
3. Decide keep or discard:
   - exit code `124` or `status=timeout` -> discard unconditionally
   - exit code `1` or `status=error` -> discard unconditionally
   - exit code `0` -> judge the run against the current lane in `$REPO/agents/scientist/scientist-guidance.md`
   - best-overall lane -> keep only meaningful score improvements
   - named model-family lane -> keep work that materially improves that family or yields a simpler, more usable component for later ensembling
   - simplification lane -> keep equal-or-better simpler variants
   - complementary-component lane -> keep credible variants the supervisor explicitly asked you to develop, even if they are not the global best model
4. Append exactly one row to `agents/scientist/scientist-results.md`.
5. Commit `agents/scientist/scientist-results.md` immediately after appending. Do not batch updates.
6. Remove `$STATE_FILE` only after the result row has been appended and committed.
7. If the state is now clean and you are not stopped, you may continue to the next experiment in the same wake.

If a completed run ended with inconsistent evidence, move to blocked instead of guessing. Examples: missing exit-code file, exit code says success but required artifacts are missing, or the log lacks the structured summary.

## Blocked State

You are blocked when the local run state cannot be interpreted safely. Typical examples:

- the state file exists but the PID is gone and no exit-code file was written
- the log exists but does not contain the structured summary
- exit code `0` was recorded but required artifacts are missing
- the detached launch failed and you cannot tell whether the run ever really started

If the recovery is obvious and local-only, repair it and continue. Otherwise tell the human exactly what is inconsistent and do not start another run until the state is resolved.

## Runner Output Format

The harness prints a structured summary to stdout (captured in `run.log`):

```text
---
experiment_name:   <name from EXPERIMENT_NAME constant>
status:            ok | timeout | error
mean_cv_roc_auc:   0.916481
std_cv_roc_auc:    0.001244
completed_folds:   5/5
training_seconds:  43.4
total_seconds:     44.2
```

Exit codes: `0` = success, `124` = timeout, `1` = error.

Use both the exit code and the summary when finalizing a run. Do not rely on the summary alone.

## Artifact Generation

When a run is kept, the harness automatically generates the following in `$ARTIFACT_DIR` **outside the 20-minute budget**:

```text
oof-preds.npy    # OOF probabilities aligned to training rows
model.pkl        # sklearn Pipeline retrained on full data
test-preds.npy   # test set probabilities from the full-data model
```

Passing `--artifact-dir` triggers this automatically on a successful run. You do not need to do anything extra. Successful finalization should confirm that these files exist before treating the run as cleanly completed.

## Results Format

`agents/scientist/scientist-results.md` is append-only and committed after every experiment. Add one row per finalized run:

```markdown
| commit | score | std | delta | status | description |
|--------|-------|-----|-------|--------|-------------|
| f03f610 | 0.916481 | 0.001244 | +0.000013 | kept | Ridge meta-learner via CalibratedClassifierCV |
| 16786a8 | 0.916400 | 0.001401 | -0.000081 | discarded | LGBM 1500 trees lr=0.03 |
| 3a9f112 | — | — | — | error | DART boosting (timeout) |
```

- `delta` is relative to the previous kept experiment, not the previous row
- Use `—` for score and std on timeout or error rows
- Append exactly one row per finalized hash
- Commit `agents/scientist/scientist-results.md` immediately after appending. Do not batch updates.

## What Good Experimentation Looks Like

- **One change at a time.** Compound changes make it impossible to know what worked.
- **Follow the guidance.** The supervisor and analyst have context you do not. Exhaust their suggested direction before going off-script.
- **Respect the active lane.** A stronger linear model for later ensembling can be a successful outcome even if it does not beat the current best tree model.
- **Do not thrash.** If three variations of the same idea all fail, move on and note the pattern.
- **Baseline first.** On a fresh branch, your very first run should be the unmodified `agents/scientist/experiment.py` to establish the baseline score for this run.
- **Simplicity criterion.** All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome. That is a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude. A `0.00001` ROC-AUC improvement that adds 20 lines of hacky code is probably not worth it. A `0.00001` ROC-AUC improvement from deleting code is worth keeping. An improvement of about `0` with much simpler code is worth keeping.
- **No overlapping runs.** Exactly one experiment may be in flight at a time.
- **Guidance reread is mandatory.** Every wake starts by rereading `scientist-guidance.md` before any new experiment decision.

## Stop Behavior

**KEEP RUNNING UNLESS STOPPED**: Do not stop on your own initiative. The only automatic control plane is your recurring `/loop` wake.

On an explicit human `stop`:

1. Cancel your recurring `/loop` task immediately.
2. Do not create any new scheduled tasks.
3. Do not start any new experiments.
4. If you are idle, report final status and go idle.
5. If you are finalizing a completed run, finish that finalization, commit the result, remove the local state file, report final status, and go idle.
6. If you have a run in progress, do not launch another run. Keep polling only the current run until it reaches a terminal state, finalize it exactly once, remove the local state file, report final status, and go idle.
7. Do not kill the in-flight harness process unless the human explicitly tells you to cancel the current run.
8. If you are blocked, report the blocked state and go idle.
