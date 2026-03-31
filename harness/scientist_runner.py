import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from harness.experiment_runner import INVALID_EXIT_CODE
from harness.scientist_contract import (
    DEFAULT_EXPERIMENT_PATH,
    ensure_results_file,
    normalize_repo_path,
    parse_task_metadata,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ERRORS_FILENAME = "scientist-errors.md"


@dataclass(frozen=True)
class TaskMetadata:
    status: str
    task_id: str
    goal: str
    keep_if: str
    reference: str | None


@dataclass(frozen=True)
class ExperimentSummary:
    status: str | None
    experiment_name: str | None
    mean_score: float | None
    std_score: float | None


def main() -> None:
    args = _parse_args()
    task_file = normalize_repo_path(args.task_file)
    results_file = normalize_repo_path(args.results_file)
    errors_file = (
        normalize_repo_path(args.errors_file)
        if args.errors_file
        else results_file.with_name(DEFAULT_ERRORS_FILENAME)
    )

    task = _extract_task_metadata(task_file.read_text())
    if task.status != "active":
        print("status: no_active_task")
        return
    completed = subprocess.run(
        _experiment_command(),
        capture_output=True,
        cwd=REPO_ROOT,
        env=_runner_env(),
        text=True,
    )
    summary = _parse_summary(completed.stdout)

    if completed.returncode == INVALID_EXIT_CODE or summary.status == "invalid":
        _append_invalid_entry(errors_file=errors_file, task=task, completed=completed)
        _report_invalid(errors_file=errors_file, completed=completed)
        raise SystemExit(INVALID_EXIT_CODE)

    _append_results_row(results_file=results_file, task=task, completed=completed, summary=summary)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-file", type=Path, required=True)
    parser.add_argument("--results-file", type=Path, required=True)
    parser.add_argument("--experiment-path", type=Path, default=DEFAULT_EXPERIMENT_PATH)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--errors-file", type=Path)
    return parser.parse_args()


def _runner_env() -> dict[str, str]:
    env = os.environ.copy()
    repo_root = str(REPO_ROOT)
    current_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = repo_root if not current_pythonpath else f"{repo_root}{os.pathsep}{current_pythonpath}"
    return env


def _extract_task_metadata(task_text: str) -> TaskMetadata:
    parsed = parse_task_metadata(task_text)
    return TaskMetadata(
        status=parsed.status,
        task_id=parsed.task_id,
        goal=parsed.goal,
        keep_if=parsed.keep_if,
        reference=parsed.reference,
    )
def _experiment_command() -> list[str]:
    return [
        sys.executable,
        "-m",
        "harness.experiment_runner",
    ]


def _parse_summary(stdout: str) -> ExperimentSummary:
    values: dict[str, str] = {}
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---" or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        values[key.strip()] = value.strip()
    return ExperimentSummary(
        status=values.get("status"),
        experiment_name=values.get("experiment_name"),
        mean_score=_maybe_float(values.get("mean_cv_roc_auc")),
        std_score=_maybe_float(values.get("std_cv_roc_auc")),
    )


def _maybe_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _append_invalid_entry(
    errors_file: Path,
    task: TaskMetadata,
    completed: subprocess.CompletedProcess[str],
) -> None:
    errors_file.parent.mkdir(parents=True, exist_ok=True)
    with errors_file.open("a") as f:
        if f.tell() > 0:
            f.write("\n\n")
        f.write(f"## {task.task_id}\n")
        f.write(f"at: {_utc_timestamp()}\n")
        f.write(f"goal: {task.goal}\n")
        if task.reference:
            f.write(f"reference: {task.reference}\n")
        f.write(f"exit_code: `{completed.returncode}`\n")
        f.write("stdout:\n")
        f.write(f"{_format_stream(completed.stdout)}\n\n")
        f.write("stderr:\n")
        f.write(f"{_format_stream(completed.stderr)}\n")


def _report_invalid(errors_file: Path, completed: subprocess.CompletedProcess[str]) -> None:
    print(f"error: invalid experiment; details written to {_display_path(errors_file)}", file=sys.stderr)
    if completed.stdout.strip():
        print("\n[experiment stdout]", file=sys.stderr)
        print(completed.stdout.rstrip(), file=sys.stderr)
    if completed.stderr.strip():
        print("\n[experiment stderr]", file=sys.stderr)
        print(completed.stderr.rstrip(), file=sys.stderr)


def _append_results_row(
    results_file: Path,
    task: TaskMetadata,
    completed: subprocess.CompletedProcess[str],
    summary: ExperimentSummary,
) -> None:
    ensure_results_file(results_file)
    outcome = _terminal_outcome(task=task, completed=completed, summary=summary, results_file=results_file)
    desc = _table_cell(task.goal)
    with results_file.open("a") as f:
        f.write(
            f"| {task.task_id} | {outcome['status']} | {outcome['score']} | {outcome['std']} | {outcome['delta_best']} | {desc} |\n"
        )


def _terminal_outcome(
    task: TaskMetadata,
    completed: subprocess.CompletedProcess[str],
    summary: ExperimentSummary,
    results_file: Path,
) -> dict[str, str]:
    if completed.returncode == 124 or summary.status == "timeout":
        return {
            "status": "timeout",
            "score": "-",
            "std": "-",
            "delta_best": "-",
        }

    if completed.returncode != 0 or summary.status == "error":
        return {
            "status": "error",
            "score": "-",
            "std": "-",
            "delta_best": "-",
        }

    if summary.mean_score is None or summary.std_score is None:
        return {
            "status": "error",
            "score": "-",
            "std": "-",
            "delta_best": "-",
        }

    best_kept = _best_kept_score(results_file)
    delta_best = summary.mean_score - best_kept if best_kept is not None else 0.0
    kept = _evaluate_keep_if(task.keep_if, summary.mean_score)
    return {
        "status": "kept" if kept else "discarded",
        "score": f"{summary.mean_score:.6f}",
        "std": f"{summary.std_score:.6f}",
        "delta_best": f"{delta_best:+.6f}",
    }


def _best_kept_score(results_file: Path) -> float | None:
    best: float | None = None
    if not results_file.exists():
        return None
    for line in results_file.read_text().splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("| task_id ") or stripped.startswith("|---------"):
            continue
        columns = [column.strip() for column in stripped.strip("|").split("|")]
        if len(columns) != 6:
            continue
        status = columns[1]
        score = _maybe_float(columns[2])
        if status != "kept" or score is None:
            continue
        if best is None or score > best:
            best = score
    return best


def _evaluate_keep_if(expression: str, score: float) -> bool:
    match = re.fullmatch(
        r"mean_cv_roc_auc\s*(>=|>|<=|<)\s*([+-]?(?:inf|infinity|[0-9]*\.?[0-9]+))",
        expression.strip(),
        flags=re.IGNORECASE,
    )
    if match is None:
        raise ValueError(f"unsupported keep_if expression: {expression}")
    operator, raw_threshold = match.groups()
    threshold = float(raw_threshold)
    if operator == ">":
        return score > threshold
    if operator == ">=":
        return score >= threshold
    if operator == "<":
        return score < threshold
    return score <= threshold


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _format_stream(stream: str) -> str:
    if not stream.strip():
        return "*(no output)*"
    return stream.rstrip()


def _table_cell(value: str) -> str:
    return " ".join(value.replace("|", "/").split())


if __name__ == "__main__":
    main()
