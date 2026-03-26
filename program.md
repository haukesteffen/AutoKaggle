# autokaggle

This repository supports two long-lived agent roles working in parallel on Kaggle's Playground Competition "Predict Customer Churn" (S6E3):

- The **experimenter** owns the experiment loop and is the only role allowed to edit `train.py`.
- The **supervisor** periodically reviews the run history and current model direction, then writes steering guidance for the experimenter.

The detailed instructions for each role live in:

- `experimenter.md`
- `supervisor.md`

Read this file first, then switch to the appropriate role document.

## Shared setup

To set up a new run, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (for example `mar26`). The branch `autokaggle/<tag>` must not already exist.
2. **Create the branch**: confirm this directory is a git repo, then create `autokaggle/<tag>` from the current default branch.
3. **Read the in-scope files**: the repo is small. Read these files for full context:
   - `README.md`
   - `prepare.py`
   - `runner.py`
   - `train.py`
   - `experimenter.md`
   - `supervisor.md`
   - if any of `README.md`, `runner.py`, `train.py`, or `pyproject.toml` are missing, stop and tell the human the repo is not ready
4. **Verify data exists**: check that `./data/` contains the train set, test set, and cross-validation ids. If not, tell the human to run `uv run python prepare.py`.
5. **Use per-run local artifacts**: all mutable local state for this run lives under `artifacts/<run_tag>/`. These files are intentionally untracked by git.
6. **Confirm and go**: once setup looks good, start the experimenter and supervisor in parallel.

## Shared artifact layout

The run tag is the suffix in the dedicated branch name, such as:

- `autokaggle/mar26` -> run tag `mar26`
- `autokaggle/mar26-cpu0` -> run tag `mar26-cpu0`

All mutable local files for a run live under:

```text
artifacts/<run_tag>/
```

The expected files are:

- `artifacts/<run_tag>/results.tsv`
- `artifacts/<run_tag>/run.log`
- `artifacts/<run_tag>/supervisor_notes.md`

These files are local runtime artifacts, not part of git history.

## Shared role boundaries

**Experimenter**

- May edit `train.py` and no other tracked file.
- Owns experiment execution, git commits, keep/discard decisions, and updates to `artifacts/<run_tag>/results.tsv`.
- Must read `artifacts/<run_tag>/supervisor_notes.md` before starting each new experiment, if it exists.

**Supervisor**

- Must not edit `train.py`, `prepare.py`, `runner.py`, `program.md`, `experimenter.md`, or any other tracked file.
- Owns `artifacts/<run_tag>/supervisor_notes.md`.
- Uses `/loop` to wake up on a fixed interval, defaulting to 1 hour.
- May adjust its own `/loop` interval over time if the experiment state justifies it.

## Shared constraints

- `prepare.py` is read-only. It owns data preparation and the fixed cross-validation split.
- `runner.py` is read-only. It owns timeout handling and result reporting.
- Do not install new packages or modify dependencies.
- The evaluation harness in `prepare.py` and `runner.py` is the ground truth protocol.
- Each experiment must finish within the hard 20-minute time budget enforced by `runner.py`.
- The goal is to maximize mean cross-validation roc_auc.
- Simpler solutions are preferred when performance is equal or nearly equal.

## Shared execution model

- The experimenter and supervisor run in separate agent sessions.
- They coordinate only through the shared local files in `artifacts/<run_tag>/`.
- The supervisor writes concise steering guidance; the experimenter decides how to apply it inside the experiment loop.
- If the supervisor notes are missing, the experimenter proceeds normally.
- If the supervisor notes are stale or clearly contradicted by current evidence, the experimenter may override them and should note the reason in the experiment description.

Once the run starts, both roles are autonomous and should continue until interrupted by the human.
