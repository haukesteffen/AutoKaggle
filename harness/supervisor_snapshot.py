from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT_PATH = Path("state/run-state.md")
DEFAULT_MEMORY_PATH = Path("state/memory.md")
DEFAULT_SCIENTIST_TASK_PATH = Path("state/scientist-task.md")
DEFAULT_ANALYST_TASK_PATH = Path("state/analyst-task.md")
DEFAULT_EXPERIMENTS_PATH = Path("history/experiments.md")
DEFAULT_ANALYSES_PATH = Path("history/analyses.md")
DEFAULT_SUBMISSIONS_PATH = Path("history/submissions.md")


@dataclass(frozen=True)
class ExperimentRow:
    task_id: str
    at: str
    lane: str
    cv: float | None
    delta_best: float | None
    status: str
    summary: str


@dataclass(frozen=True)
class AnalysisRow:
    entry_id: str
    at: str
    question: str
    verdict: str
    confidence: str
    summary: str


@dataclass(frozen=True)
class SubmissionRow:
    task_id: str
    submitted_at: str
    cv_score: float | None
    lb_score: float | None
    lb_rank: int | None
    status: str
    summary: str


def main() -> None:
    args = _parse_args()
    output_path = _normalize_repo_path(args.output_path)

    seed = _parse_run_state_seed(_read_text(DEFAULT_OUTPUT_PATH))
    memory_text = _read_text(DEFAULT_MEMORY_PATH)
    scientist_task = _parse_key_value_lines(_read_text(DEFAULT_SCIENTIST_TASK_PATH).splitlines())
    analyst_task = _parse_key_value_lines(_read_text(DEFAULT_ANALYST_TASK_PATH).splitlines())

    rendered = render_run_state(
        seed=seed,
        scientist_task=scientist_task,
        analyst_task=analyst_task,
        experiments=_load_experiments(),
        analyses=_load_analyses(),
        submissions=_load_submissions(),
        memory_text=memory_text,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)
    print(f"wrote {output_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def _normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def _read_text(path: Path) -> str:
    resolved = _normalize_repo_path(path)
    if not resolved.exists():
        return ""
    return resolved.read_text()


def _safe_float(value: str) -> float | None:
    stripped = value.strip()
    if not stripped or stripped == "-" or stripped.lower() == "pending":
        return None
    return float(stripped)


def _safe_int(value: str) -> int | None:
    stripped = value.strip()
    if not stripped or stripped == "-" or stripped.lower() == "pending":
        return None
    return int(stripped)


def _split_markdown_row(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def _is_separator_row(line: str) -> bool:
    stripped = line.strip().replace("|", "").replace("-", "").replace(":", "")
    return not stripped


def _normalize_header(token: str) -> str:
    return re.sub(r"\s+", "_", token.strip().lower().replace("`", ""))


def _parse_key_value_lines(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or ":" not in stripped or stripped.startswith("#"):
            continue
        key, value = stripped.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key in fields:
            continue
        fields[normalized_key] = value.strip()
    return fields


def _parse_run_state_seed(text: str) -> dict[str, object]:
    top_lines: list[str] = []
    for line in text.splitlines():
        if line.strip() == "## Current Focus":
            break
        top_lines.append(line)

    fields = _parse_key_value_lines(top_lines)
    focus: dict[str, str] = {}
    in_focus = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Current Focus":
            in_focus = True
            continue
        if in_focus and stripped.startswith("## "):
            break
        if not in_focus or not stripped.startswith("- "):
            continue
        body = stripped[2:].strip()
        if ":" not in body:
            continue
        key, value = body.split(":", 1)
        focus[key.strip()] = value.strip()
    fields["current_focus"] = focus
    return fields


def _parse_table_rows(text: str, required_headers: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header_map: dict[str, int] | None = None
    normalized_required = [_normalize_header(header) for header in required_headers]

    for line in text.splitlines():
        if not line.strip().startswith("|") or _is_separator_row(line):
            continue
        cols = _split_markdown_row(line)
        normalized_cols = [_normalize_header(col) for col in cols]
        if normalized_cols == normalized_required:
            header_map = {header: normalized_cols.index(header) for header in normalized_required}
            continue
        if header_map is None or len(cols) <= max(header_map.values()):
            continue
        rows.append({header: cols[index] for header, index in header_map.items()})
    return rows


def _load_experiments() -> list[ExperimentRow]:
    rows: list[ExperimentRow] = []
    for row in _parse_table_rows(
        _read_text(DEFAULT_EXPERIMENTS_PATH),
        ["task_id", "finished_at", "lane", "metric", "delta_best", "status", "artifact_dir", "summary"],
    ):
        rows.append(
            ExperimentRow(
                task_id=row.get("task_id", ""),
                at=row.get("finished_at", ""),
                lane=row.get("lane", ""),
                cv=_safe_float(row.get("metric", "")),
                delta_best=_safe_float(row.get("delta_best", "")),
                status=row.get("status", ""),
                summary=row.get("summary", ""),
            )
        )
    return rows


def _load_analyses() -> list[AnalysisRow]:
    rows: list[AnalysisRow] = []
    for row in _parse_table_rows(
        _read_text(DEFAULT_ANALYSES_PATH),
        ["analysis_id", "at", "q", "verdict", "confidence", "artifact_dir", "summary"],
    ):
        rows.append(
            AnalysisRow(
                entry_id=row.get("analysis_id", ""),
                at=row.get("at", ""),
                question=row.get("q", ""),
                verdict=row.get("verdict", ""),
                confidence=row.get("confidence", ""),
                summary=row.get("summary", ""),
            )
        )
    return rows


def _load_submissions() -> list[SubmissionRow]:
    rows: list[SubmissionRow] = []
    for row in _parse_table_rows(
        _read_text(DEFAULT_SUBMISSIONS_PATH),
        ["task_id", "submitted_at", "cv_score", "lb_score", "lb_rank", "status", "summary"],
    ):
        rows.append(
            SubmissionRow(
                task_id=row.get("task_id", ""),
                submitted_at=row.get("submitted_at", ""),
                cv_score=_safe_float(row.get("cv_score", "")),
                lb_score=_safe_float(row.get("lb_score", "")),
                lb_rank=_safe_int(row.get("lb_rank", "")),
                status=row.get("status", ""),
                summary=row.get("summary", ""),
            )
        )
    return rows


def _format_scientist_task(fields: dict[str, str], seed_value: str) -> str:
    status = fields.get("status", "").strip().lower()
    if not status:
        return seed_value or "none"
    if status != "active":
        return "none"
    task_id = fields.get("id", "").strip() or "unknown"
    detail = _first_non_empty(fields, ["batch_goal", "success_criterion", "reference"])
    return f"{task_id} | {detail}" if detail else task_id


def _format_analyst_task(fields: dict[str, str], seed_value: str) -> str:
    status = fields.get("status", "").strip().lower()
    if not status:
        return seed_value or "none"
    if status != "active":
        return "none"
    task_id = fields.get("id", "").strip() or "unknown"
    detail = _first_non_empty(fields, ["q", "decision_use", "reference"])
    return f"{task_id} | {detail}" if detail else task_id


def _first_non_empty(fields: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        value = fields.get(key, "").strip()
        if value and value.lower() != "none":
            return value
    return ""


def _memory_stage_hint(text: str) -> str:
    lowered = text.lower()
    if "late promotion gate" in lowered or "promotion gate" in lowered:
        return "promotion_gate"
    if "exploration phase" in lowered:
        return "exploration"
    return ""


def _memory_lane_hint(text: str) -> str:
    lowered = text.lower()
    if "s-094" in lowered and "stabilization" in lowered:
        return "S-094-successor / Medium-stabilization"
    if "de-risking" in lowered:
        return "conservative de-risking"
    return ""


def _best_experiment(rows: list[ExperimentRow]) -> ExperimentRow | None:
    scored = [row for row in rows if row.cv is not None]
    if not scored:
        return None
    return max(scored, key=lambda row: row.cv or float("-inf"))


def _best_submission(rows: list[SubmissionRow]) -> SubmissionRow | None:
    scored = [row for row in rows if row.lb_score is not None]
    if scored:
        return max(scored, key=lambda row: row.lb_score or float("-inf"))
    scored = [row for row in rows if row.cv_score is not None]
    if not scored:
        return None
    return max(scored, key=lambda row: row.cv_score or float("-inf"))


def _render_experiment_candidate(row: ExperimentRow | None, seed_value: str) -> str:
    if row is None:
        return seed_value or "none"
    score = f"{row.cv:.6f}" if row.cv is not None else "unknown"
    summary = row.summary or "no summary"
    return f"{row.task_id} | {score} | {summary}"


def _render_submission_candidate(row: SubmissionRow | None, seed_value: str) -> str:
    if row is None:
        return seed_value or "none"
    if row.lb_score is not None:
        score = f"{row.lb_score:.5f} LB"
    elif row.cv_score is not None:
        score = f"{row.cv_score:.6f} CV"
    else:
        score = "unknown"
    rank = f"rank {row.lb_rank}" if row.lb_rank is not None else "rank unknown"
    submitted_at = row.submitted_at or "unknown"
    return f"{row.task_id} | {submitted_at} | {score} | {rank}"


def _derive_focus_defaults(seed_focus: dict[str, str], analyses: list[AnalysisRow]) -> dict[str, str]:
    focus = dict(seed_focus)
    if not focus.get("next_decision") and analyses:
        latest = analyses[-1]
        decision_bits = [latest.verdict or "review", latest.question or latest.entry_id]
        focus["next_decision"] = " ".join(bit for bit in decision_bits if bit)
    if not focus.get("next_batch") and analyses:
        latest = analyses[-1]
        focus["next_batch"] = latest.summary or latest.question or latest.entry_id
    return focus


def render_run_state(
    *,
    seed: dict[str, object],
    scientist_task: dict[str, str],
    analyst_task: dict[str, str],
    experiments: list[ExperimentRow],
    analyses: list[AnalysisRow],
    submissions: list[SubmissionRow],
    memory_text: str,
) -> str:
    generated_as_of = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    seed_focus = cast(dict[str, str], seed.get("current_focus", {}))
    focus = _derive_focus_defaults(seed_focus, analyses)

    best_experiment = _best_experiment(experiments)
    best_submission = _best_submission(submissions)

    stage = str(seed.get("stage", "")).strip() or _memory_stage_hint(memory_text) or "unknown"
    lane = (
        str(seed.get("lane", "")).strip()
        or _memory_lane_hint(memory_text)
        or (best_experiment.lane if best_experiment else "")
        or "unknown"
    )
    active_scientist_task = _format_scientist_task(
        scientist_task, str(seed.get("active_scientist_task", "")).strip()
    )
    active_analyst_task = _format_analyst_task(
        analyst_task, str(seed.get("active_analyst_task", "")).strip()
    )

    best_offline_candidate = _render_experiment_candidate(
        best_experiment,
        focus.get("best_offline_candidate", ""),
    )
    best_submitted_candidate = _render_submission_candidate(
        best_submission,
        focus.get("best_submitted_candidate", ""),
    )
    next_decision = (
        focus.get("next_decision", "")
        or "keep the current lane until a stronger offline candidate appears."
    )
    next_batch = (
        focus.get("next_batch", "")
        or "one bounded scientist run on the current lane; use analyst only after a new candidate exists."
    )

    lines = [
        "# Run State",
        "",
        f"as_of: {generated_as_of}",
        f"stage: {stage}",
        f"lane: {lane}",
        f"active_scientist_task: {active_scientist_task or 'none'}",
        f"active_analyst_task: {active_analyst_task or 'none'}",
        "",
        "## Current Focus",
        "",
        f"- best_offline_candidate: {best_offline_candidate}",
        f"- best_submitted_candidate: {best_submitted_candidate}",
        f"- next_decision: {next_decision}",
        f"- next_batch: {next_batch}",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
