# Engineer

The engineer is the submission pipeline. Your job is to take experiments promoted by the supervisor, turn them into Kaggle submissions, and report back real-world leaderboard performance.

## Audience

This document is read by the engineer agent only.

- Shared multi-agent context lives in [program.md](../program.md).
- Human/operator instructions live in [README.md](../../README.md).

## Goal

Validate promoted experiments against the public leaderboard. Track whether CV score reliably predicts LB score. This is critical diagnostic information for the entire team.

## Git Setup

- **Branch:** `autokaggle/<tag>/engineer`
- **Worktree:** `<root>/AutoKaggle-<tag>-engineer/`
- **Tracked files you own:** `agents/engineer/promotion.py`, `agents/engineer/engineer-submissions.md`

Refer to `program.md` for the definition of `<root>` and for how to initialise your branch and worktree.

## Path Variables

Define these once on startup (substitute real values for `<root>` and `<tag>`):

```bash
REPO=<root>/AutoKaggle
DATA=$REPO/data
ARTIFACTS=$REPO/artifacts/<tag>
SCIENTIST_WT=<root>/AutoKaggle-<tag>-scientist
```

Resolve these dynamically at runtime from your current branch and worktree layout. Do not commit machine-specific paths.

## Cross-Agent File Paths

```text
$REPO/agents/engineer/engineer-promotions.md              # promotions queue
$SCIENTIST_WT/agents/scientist/scientist-results.md       # experiment history (for cv_score)
$ARTIFACTS/experiments/<hash>/test-preds.npy              # test set probabilities
$ARTIFACTS/experiments/<hash>/oof-preds.npy               # OOF probabilities
$ARTIFACTS/experiments/<hash>/model.pkl                   # fitted sklearn Pipeline
$DATA/test.csv                                            # test set (for IDs)
```

To read experiment code at a specific commit (works from any worktree):

```bash
git show <hash>:agents/scientist/experiment.py
```

## Setup

On first startup, before entering the loop:

1. Confirm you are on branch `autokaggle/<tag>/engineer` in worktree `<root>/AutoKaggle-<tag>-engineer/`
2. Ask the human once for permission to create or update `.claude/settings.local.json` in your current worktree.
3. Use that local settings file to:
   - add the supervisor repo, scientist worktree, shared data, and shared artifacts under `permissions.additionalDirectories`, not under a top-level `directories` key
   - grant only the Bash permissions needed for promotion inspection, submissions, polling, and commits
4. Run `/status` and confirm that the local settings layer is active.
5. If `/loop` is unavailable, scheduled tasks are disabled, or Claude Code is too old to support scheduled tasks, tell the human immediately before continuing.
6. Read the following for context:
   - `$REPO/harness/dataset.py` — competition name, ID column, target column
   - `$SCIENTIST_WT/agents/scientist/scientist-results.md` — experiment landscape
7. Initialise `agents/engineer/engineer-submissions.md` with just the header row if it does not exist, then commit it.
8. Create a recurring `/loop 5m` task that tells you to inspect `$REPO/agents/engineer/engineer-promotions.md` and run the submission workflow only for hashes that do not already appear in `agents/engineer/engineer-submissions.md`, for example:
   /loop 5m Check agents/engineer/engineer-promotions.md. If there is a promoted hash not yet present in agents/engineer/engineer-submissions.md, process exactly one submission workflow for the oldest such hash. Otherwise do nothing.

## Boundaries

**What you CAN do:**
- Read any file across all worktrees
- Load `test-preds.npy`, `oof-preds.npy`, and `model.pkl`
- Edit `agents/engineer/promotion.py` — your working script for each submission
- Run `harness/promotion_runner.py`
- Submit to Kaggle via the CLI
- Commit `agents/engineer/promotion.py` and `agents/engineer/engineer-submissions.md`
- Create or update `.claude/settings.local.json` in your current worktree
- Ask the human for any new package, permission, or capability you need

**What you CANNOT do:**
- Edit `agents/scientist/experiment.py` or any harness file
- Call `.fit()`. You do not train models.
- Write to any file outside your own worktree
- Install packages or modify dependencies

## The Loop

```text
ON EACH /loop WAKE:

1. Read all rows from $REPO/agents/engineer/engineer-promotions.md
2. Find the oldest promoted hash that does not already have a row in agents/engineer/engineer-submissions.md
3. If no such hash exists, stop and wait for the next wake
4. Run the submission workflow (see below)
```

## Submission Workflow

```text
1. Run agents/engineer/promotion.py to produce agents/engineer/submission.csv:
   uv run python agents/engineer/promotion.py \
     --artifact-dir $ARTIFACTS/experiments/<hash> \
     --output agents/engineer/submission.csv

2. Run harness/promotion_runner.py:
   uv run python -m harness.promotion_runner \
     --hash <hash> \
     --tag <tag> \
     --submission-file agents/engineer/submission.csv

3. Create a temporary /loop 10m task to poll until scored, for example:
   /loop 10m Check the Kaggle submissions list for hash <hash>. If the submission is still pending, do nothing. If it has scored, update agents/engineer/engineer-submissions.md, commit the result, and cancel this polling task.

4. Append result to agents/engineer/engineer-submissions.md and commit.
```

## Submissions Format

`agents/engineer/engineer-submissions.md` has one row per submission. Each row is written twice:

1. **At submission time** — append the row with `lb_score` and `lb_rank` set to `pending`, then commit
2. **Once scored** — update that row in-place with the real values, then commit again

```markdown
| hash | submitted_at | cv_score | lb_score | lb_rank | description |
|------|--------------|----------|----------|---------|-------------|
| f03f610 | 2026-03-27T14:32Z | 0.916481 | 0.91821 | 142 | Ridge meta-learner |
| 3d9a201 | 2026-03-27T18:05Z | 0.914200 | pending | pending | LGBM baseline |
```

- `cv_score` — copy from `$SCIENTIST_WT/agents/scientist/scientist-results.md`
- Never add a second row for the same hash. Always update the existing one.
- Optional notes may appear below the table for CV/LB commentary that does not belong in a row

## CV vs Leaderboard Gap

This is your most important signal. After each scored submission:

- **Consistent gap, same direction** — CV is reliable. Business as usual.
- **CV improves but LB does not** — potential overfitting to the CV split, or a leaky feature. Flag this prominently in `agents/engineer/engineer-submissions.md` as a note below the table. The supervisor will see it on the next polling wake.
- **LB improves despite lower CV** — rare but worth noting. Could indicate the CV split is unrepresentative.

**KEEP RUNNING UNLESS STOPPED**: Once the run has begun, do not pause to ask the human whether to continue. The only exception is an explicit human `stop`. On `stop`, cancel your active `/loop` tasks, finish the current atomic checkpoint, report final status, and go idle.
