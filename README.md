# autokaggle

AutoKaggle is an experiment in adapting Karpathy's `autoresearch` loop to a Kaggle Playground competition.

The repository is split into a fixed harness plus an editable experiment file:

- `prepare.py` owns data prep plus the fixed cross-validation contract.
- `runner.py` owns the experiment entrypoint, timeout handling, and result reporting.
- `train.py` is the single editable file for feature engineering, preprocessing, and model choice across the installed families (`scikit-learn`, `xgboost`, `lightgbm`, and `catboost`).

## Prerequisites

- Install `uv`. This repo uses `uv` for dependency management and command execution.
- Run `uv sync` to create the project environment and install the managed dependencies, including `kaggle`.
- Configure Kaggle authentication on your machine before running data prep.
- Make sure your Kaggle account has access to the target competition and has accepted any required rules, or the download step will fail.

## Commands

- Prepare the local data once with `uv run python prepare.py`.
- Run one cross-validation experiment with `uv run python runner.py`.
