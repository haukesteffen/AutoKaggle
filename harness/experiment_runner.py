import argparse
import importlib.util
import multiprocessing as mp
import os
import queue
import subprocess
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(os.cpu_count() or 1))

from harness.dataset import N_SPLITS, TIME_BUDGET_SECONDS, EvaluationResult, evaluate_model

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT_PATH = Path("agents/scientist/experiment.py")


def main() -> None:
    args = _parse_args()
    experiment_path = _normalize_repo_path(args.experiment_path)
    editable_path = _normalize_repo_path(args.editable_path or args.experiment_path)

    try:
        _enforce_edit_boundary(editable_path)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    total_start = time.perf_counter()
    deadline = time.monotonic() + TIME_BUDGET_SECONDS

    ctx = mp.get_context("spawn")
    messages: mp.Queue = ctx.Queue()
    process = ctx.Process(target=_run_evaluation, args=(messages, experiment_path))
    process.start()

    experiment_name = "unnamed"
    completed_folds = 0
    result: EvaluationResult | None = None
    oof_preds = None

    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            _terminate_process(process)
            total_seconds = time.perf_counter() - total_start
            _print_timeout_summary(
                experiment_name=experiment_name,
                completed_folds=completed_folds,
                training_seconds=None,
                total_seconds=total_seconds,
            )
            raise SystemExit(124)

        try:
            message = messages.get(timeout=min(0.5, remaining))
        except queue.Empty:
            if process.is_alive():
                continue
            break

        message_type = message["type"]
        if message_type == "start":
            experiment_name = message["experiment_name"]
            continue
        if message_type == "progress":
            completed_folds = message["completed_folds"]
            continue
        if message_type == "result":
            experiment_name = message["experiment_name"]
            result = message["result"]
            oof_preds = message["oof_preds"]
            break
        if message_type == "error":
            experiment_name = message["experiment_name"]
            total_seconds = time.perf_counter() - total_start
            _print_error_summary(experiment_name, completed_folds, total_seconds)
            print(message["traceback"], file=sys.stderr, end="")
            raise SystemExit(1)

        raise RuntimeError(f"unexpected worker message type: {message_type}")

    process.join(timeout=1)
    total_seconds = time.perf_counter() - total_start

    if result is None:
        if process.is_alive():
            _terminate_process(process)
        _print_error_summary(experiment_name, completed_folds, total_seconds)
        print("worker exited without returning an evaluation result", file=sys.stderr)
        raise SystemExit(1)

    if result.timed_out or result.completed_folds < N_SPLITS or result.mean_score is None or result.std_score is None:
        _print_timeout_summary(
            experiment_name=experiment_name,
            completed_folds=result.completed_folds,
            training_seconds=result.training_seconds,
            total_seconds=total_seconds,
        )
        raise SystemExit(124)

    _print_success_summary(
        experiment_name=experiment_name,
        result=result,
        total_seconds=total_seconds,
    )
    if args.artifact_dir is not None:
        if oof_preds is None:
            print("artifact generation failed: worker did not return out-of-fold predictions", file=sys.stderr)
            raise SystemExit(1)
        try:
            _generate_artifacts(args.artifact_dir, oof_preds, experiment_path)
        except BaseException as exc:
            print(f"artifact generation failed: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc


def _run_evaluation(messages: mp.Queue, experiment_path: Path) -> None:
    experiment_name = "unnamed"
    try:
        experiment = _load_module_from_path(experiment_path, "autokaggle_experiment_worker")

        experiment_name = getattr(experiment, "EXPERIMENT_NAME", experiment_name)
        messages.put({"type": "start", "experiment_name": experiment_name})

        result, oof_preds = evaluate_model(
            model_builder=experiment.build_model,
            feature_builder=experiment.build_features,
            deadline=time.monotonic() + TIME_BUDGET_SECONDS,
            on_fold_complete=lambda completed: messages.put(
                {"type": "progress", "completed_folds": completed}
            ),
        )
        messages.put(
            {
                "type": "result",
                "experiment_name": experiment_name,
                "result": result,
                "oof_preds": oof_preds,
            }
        )
    except BaseException:
        messages.put(
            {
                "type": "error",
                "experiment_name": experiment_name,
                "traceback": traceback.format_exc(),
            }
        )


def _enforce_edit_boundary(editable_path: Path) -> None:
    if os.environ.get("AUTOKAGGLE_STRICT_EDIT_GUARD") != "1":
        return

    allowed_path = _to_repo_relative_path(editable_path)
    changed_paths: set[str] = set()
    commands = (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
    )
    for command in commands:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
        changed_paths.update(Path(line.strip()).as_posix() for line in completed.stdout.splitlines() if line.strip())

    disallowed = sorted(path for path in changed_paths if path != allowed_path)
    if disallowed:
        joined = ", ".join(disallowed)
        raise RuntimeError(
            f"tracked edits outside {allowed_path} are not allowed during experiment runs: {joined}"
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--experiment-path", type=Path, default=DEFAULT_EXPERIMENT_PATH)
    parser.add_argument("--editable-path", type=Path)
    return parser.parse_args()


def _terminate_process(process: mp.Process) -> None:
    if process.is_alive():
        process.terminate()
        process.join(timeout=1)
    if process.is_alive():
        process.kill()
        process.join(timeout=1)


def _generate_artifacts(artifact_dir: Path, oof_preds, experiment_path: Path) -> None:
    import pickle

    import numpy as np
    import pandas as pd

    experiment = _load_module_from_path(experiment_path, "autokaggle_experiment_artifacts")
    from harness.dataset import ID_COLUMN, TEST_PATH, load_train_with_folds, predict_positive_scores, split_xy

    artifact_dir.mkdir(parents=True, exist_ok=True)
    np.save(artifact_dir / "oof-preds.npy", oof_preds)

    train_df = load_train_with_folds()
    raw_X, y = split_xy(train_df)
    X_full = experiment.build_features(raw_X.copy())
    if not hasattr(X_full, "columns") or len(X_full) != len(raw_X):
        raise TypeError("build_features must return a pandas DataFrame with the original row count")

    model = experiment.build_model(X_full.head(0).copy())
    model.fit(X_full, y)

    with (artifact_dir / "model.pkl").open("wb") as f:
        pickle.dump(model, f)

    test_df = pd.read_csv(TEST_PATH).drop(columns=[ID_COLUMN])
    X_test = experiment.build_features(test_df.copy())
    if not hasattr(X_test, "columns") or len(X_test) != len(test_df):
        raise TypeError("build_features must return a pandas DataFrame with the original row count")
    if X_full.columns.tolist() != X_test.columns.tolist():
        raise ValueError("build_features must return the same columns for train and test splits")

    test_preds = predict_positive_scores(model, X_test)
    np.save(artifact_dir / "test-preds.npy", test_preds)

    print(f"artifacts written to {artifact_dir}")


def _normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def _to_repo_relative_path(path: Path) -> str:
    resolved = _normalize_repo_path(path)
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _load_module_from_path(module_path: Path, module_name: str):
    _ensure_repo_root_on_syspath()
    resolved_path = _normalize_repo_path(module_path)
    spec = importlib.util.spec_from_file_location(module_name, resolved_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {resolved_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _ensure_repo_root_on_syspath() -> None:
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


def _print_success_summary(experiment_name: str, result: EvaluationResult, total_seconds: float) -> None:
    print("---")
    print(f"experiment_name:   {experiment_name}")
    print("status:            ok")
    print(f"mean_cv_roc_auc:   {result.mean_score:.6f}")
    print(f"std_cv_roc_auc:    {result.std_score:.6f}")
    print(f"completed_folds:   {result.completed_folds}/{N_SPLITS}")
    print(f"training_seconds:  {result.training_seconds:.1f}")
    print(f"total_seconds:     {total_seconds:.1f}")


def _print_timeout_summary(
    experiment_name: str,
    completed_folds: int,
    training_seconds: float | None,
    total_seconds: float,
) -> None:
    print("---")
    print(f"experiment_name:   {experiment_name}")
    print("status:            timeout")
    print(f"completed_folds:   {completed_folds}/{N_SPLITS}")
    if training_seconds is not None:
        print(f"training_seconds:  {training_seconds:.1f}")
    print(f"total_seconds:     {total_seconds:.1f}")


def _print_error_summary(experiment_name: str, completed_folds: int, total_seconds: float) -> None:
    print("---")
    print(f"experiment_name:   {experiment_name}")
    print("status:            error")
    print(f"completed_folds:   {completed_folds}/{N_SPLITS}")
    print(f"total_seconds:     {total_seconds:.1f}")


if __name__ == "__main__":
    main()
