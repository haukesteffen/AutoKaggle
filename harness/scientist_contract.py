from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT_PATH = Path("agents/scientist/experiment.py")
DEFAULT_RESULTS_PATH = Path("agents/scientist/scientist-results.md")
DEFAULT_TASK_PATH = Path("agents/scientist/scientist-task.md")
DEFAULT_ARTIFACTS_ROOT = Path("artifacts")
TASK_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
RESULTS_HEADER = """# Scientist Results

| task_id | status | score | std | delta_best | desc |
|---------|--------|-------|-----|------------|------|
"""


@dataclass(frozen=True)
class TaskMetadata:
    status: str
    task_id: str
    goal: str
    keep_if: str
    reference: str | None


@dataclass(frozen=True)
class ResultRow:
    task_id: str
    status: str
    score: float | None
    std: float | None
    delta_best: float | None
    desc: str


def normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def parse_task_metadata(task_text: str) -> TaskMetadata:
    fields = _parse_key_value_fields(task_text)
    task_id = fields.get("id") or "S-unknown"
    _validate_task_id(task_id)
    return TaskMetadata(
        status=fields.get("status", "none"),
        task_id=task_id,
        goal=fields.get("goal") or "Unspecified experiment goal",
        keep_if=fields.get("keep_if") or "mean_cv_roc_auc > -inf",
        reference=fields.get("reference"),
    )


def read_task_metadata(task_path: Path = DEFAULT_TASK_PATH) -> TaskMetadata:
    return parse_task_metadata(normalize_repo_path(task_path).read_text())


def default_artifact_dir(task_id: str) -> Path:
    _validate_task_id(task_id)
    return DEFAULT_ARTIFACTS_ROOT / task_id


def ensure_results_file(results_path: Path = DEFAULT_RESULTS_PATH) -> Path:
    resolved = normalize_repo_path(results_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    if not resolved.exists() or not resolved.read_text().strip():
        resolved.write_text(RESULTS_HEADER)
    return resolved


def read_result_row(task_id: str, results_path: Path = DEFAULT_RESULTS_PATH) -> ResultRow:
    _validate_task_id(task_id)
    resolved = normalize_repo_path(results_path)
    if not resolved.exists():
        raise ValueError(f"results file does not exist: {resolved}")

    matches: list[ResultRow] = []
    for line in resolved.read_text().splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or stripped.startswith("| task_id ") or stripped.startswith("|---------"):
            continue
        columns = [column.strip() for column in stripped.strip("|").split("|")]
        if len(columns) != 6:
            continue
        if columns[0] != task_id:
            continue
        matches.append(
            ResultRow(
                task_id=columns[0],
                status=columns[1],
                score=_maybe_float(columns[2]),
                std=_maybe_float(columns[3]),
                delta_best=_maybe_float(columns[4]),
                desc=columns[5],
            )
        )

    if not matches:
        raise ValueError(f"task_id {task_id!r} not found in {resolved}")
    if len(matches) > 1:
        raise ValueError(f"task_id {task_id!r} appears multiple times in {resolved}")
    return matches[0]


def _validate_task_id(task_id: str) -> None:
    if TASK_ID_PATTERN.fullmatch(task_id) is None:
        raise ValueError(f"invalid task id: {task_id!r}")


def _parse_key_value_fields(task_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in task_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key not in {"status", "id", "at", "goal", "keep_if", "reference"}:
            continue
        normalized_value = value.strip()
        if normalized_value and normalized_key not in fields:
            fields[normalized_key] = normalized_value
    return fields


def _maybe_float(value: str | None) -> float | None:
    if value is None or value == "-":
        return None
    try:
        return float(value)
    except ValueError:
        return None
