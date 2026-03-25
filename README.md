# autokaggle

AutoKaggle is an experiment in adapting Karpathy's `autoresearch` loop to a Kaggle Playground competition.

## Prerequisites

- Install `uv`. This repo uses `uv` for dependency management and command execution.
- Run `uv sync` to create the project environment and install the managed dependencies, including `kaggle`.
- Configure Kaggle authentication on your machine before running data prep.
- Make sure your Kaggle account has access to the target competition and has accepted any required rules, or the download step will fail.
