from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT_PATH = Path("agents/supervisor/run-state.md")
DEFAULT_RESULTS_PATH = Path("agents/scientist/scientist-results.md")
DEFAULT_FINDINGS_PATH = Path("agents/analyst/analyst-findings.md")
DEFAULT_KNOWLEDGE_PATH = Path("agents/analyst/analyst-knowledge.md")
DEFAULT_WHITEPAPER_PATH = Path("agents/strategist/strategy-whitepaper.md")
DEFAULT_LEADERBOARD_PATH = Path("agents/supervisor/leaderboard-history.md")
DEFAULT_STRATEGY_REQUEST_PATH = Path("agents/strategist/strategy-request.md")
DEFAULT_SCIENTIST_TASK_PATH = Path("agents/scientist/scientist-task.md")
DEFAULT_ANALYST_HYPOTHESIS_PATH = Path("agents/analyst/analyst-hypothesis.md")

SECTION_HEADING = re.compile(r"^##\s+(.+?)\s*$")


@dataclass(frozen=True)
class ScientistResultRow:
    task_id: str
    score: float | None
    std: float | None
    delta_best: float | None
    desc: str


@dataclass(frozen=True)
class LeaderboardRow:
    task_id: str
    submitted_at: str
    cv_score: float | None
    status: str
    lb_score: float | None
    lb_rank: int | None
    rationale: str


@dataclass(frozen=True)
class KnowledgeEntry:
    entry_id: str
    title: str
    summary: str


@dataclass(frozen=True)
class FindingEntry:
    entry_id: str
    question: str
    verdict: str
    confidence: str


@dataclass(frozen=True)
class StrategySummary:
    current_date: str
    deadline_assumption: str
    days_remaining: str
    primary: str
    secondary: str
    background: str
    hold: str
    guidance: list[str]


def main() -> None:
    args = _parse_args()
    output_path = _normalize_repo_path(args.output_path)

    strategy = parse_strategy_whitepaper(_read_text(DEFAULT_WHITEPAPER_PATH))
    results = parse_scientist_results(_read_text(DEFAULT_RESULTS_PATH))
    knowledge = parse_knowledge_entries(_read_text(DEFAULT_KNOWLEDGE_PATH))
    findings = parse_findings_entries(_read_text(DEFAULT_FINDINGS_PATH))
    leaderboard = parse_leaderboard_rows(_read_text(DEFAULT_LEADERBOARD_PATH))

    status_map = {
        "strategy_request": read_status_fields(DEFAULT_STRATEGY_REQUEST_PATH),
        "scientist_task": read_status_fields(DEFAULT_SCIENTIST_TASK_PATH),
        "analyst_hypothesis": read_status_fields(DEFAULT_ANALYST_HYPOTHESIS_PATH),
    }

    rendered = render_run_state(
        strategy=strategy,
        results=results,
        knowledge=knowledge,
        findings=findings,
        leaderboard=leaderboard,
        status_map=status_map,
        max_recent_results=args.max_recent_results,
        max_recent_knowledge=args.max_recent_knowledge,
        max_recent_findings=args.max_recent_findings,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered)
    print(f"wrote {output_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-recent-results", type=int, default=5)
    parser.add_argument("--max-recent-knowledge", type=int, default=4)
    parser.add_argument("--max-recent-findings", type=int, default=3)
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


def parse_scientist_results(text: str) -> list[ScientistResultRow]:
    rows: list[ScientistResultRow] = []
    for line in text.splitlines():
        if not line.strip().startswith("|") or _is_separator_row(line):
            continue
        cols = _split_markdown_row(line)
        if cols[:5] == ["id", "score", "std", "delta_best", "desc"]:
            continue
        if len(cols) < 5:
            continue
        rows.append(
            ScientistResultRow(
                task_id=cols[0],
                score=_safe_float(cols[1]),
                std=_safe_float(cols[2]),
                delta_best=_safe_float(cols[3]),
                desc=cols[4],
            )
        )
    return rows


def parse_leaderboard_rows(text: str) -> list[LeaderboardRow]:
    rows: list[LeaderboardRow] = []
    for line in text.splitlines():
        if not line.strip().startswith("|") or _is_separator_row(line):
            continue
        cols = _split_markdown_row(line)
        if cols[:7] == ["task_id", "submitted_at", "cv_score", "status", "lb_score", "lb_rank", "rationale"]:
            continue
        if len(cols) < 7:
            continue
        rows.append(
            LeaderboardRow(
                task_id=cols[0],
                submitted_at=cols[1],
                cv_score=_safe_float(cols[2]),
                status=cols[3],
                lb_score=_safe_float(cols[4]),
                lb_rank=_safe_int(cols[5]),
                rationale=cols[6],
            )
        )
    return rows


def _parse_headed_blocks(text: str) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                blocks.append((current_heading, current_lines))
            current_heading = line[3:].strip()
            current_lines = []
            continue
        if current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        blocks.append((current_heading, current_lines))
    return blocks


def _first_summary_line(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("source:", "at:", "q:", "verdict:", "conf:", "reference:", "evidence:", "follow_up:")):
            continue
        if stripped.startswith("- "):
            return stripped[2:].strip()
        return stripped
    return ""


def parse_knowledge_entries(text: str) -> list[KnowledgeEntry]:
    entries: list[KnowledgeEntry] = []
    for heading, lines in _parse_headed_blocks(text):
        entry_id, title = _split_heading_identifier(heading)
        entries.append(
            KnowledgeEntry(
                entry_id=entry_id,
                title=title,
                summary=_first_summary_line(lines),
            )
        )
    return entries


def parse_findings_entries(text: str) -> list[FindingEntry]:
    entries: list[FindingEntry] = []
    for heading, lines in _parse_headed_blocks(text):
        fields = _parse_key_value_lines(lines)
        entries.append(
            FindingEntry(
                entry_id=heading.strip(),
                question=fields.get("q", ""),
                verdict=fields.get("verdict", ""),
                confidence=fields.get("conf", ""),
            )
        )
    return entries


def _split_heading_identifier(heading: str) -> tuple[str, str]:
    if "—" in heading:
        entry_id, title = heading.split("—", 1)
        return entry_id.strip(), title.strip()
    return heading.strip(), heading.strip()


def _parse_key_value_lines(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key in fields:
            continue
        fields[normalized_key] = value.strip()
    return fields


def parse_strategy_whitepaper(text: str) -> StrategySummary:
    sections = _parse_markdown_sections(text)
    emphasis = _parse_emphasis_section(sections.get("Emphasis", ""))
    guidance = [
        line.strip()
        for line in sections.get("Guidance For The Supervisor", "").splitlines()
        if re.match(r"^\d+\.\s", line.strip())
    ]
    return StrategySummary(
        current_date=_single_line(sections.get("Current Date", "")),
        deadline_assumption=_single_line(sections.get("Deadline Assumption", "")),
        days_remaining=_single_line(sections.get("Days Remaining", "")),
        primary=emphasis.get("primary", ""),
        secondary=emphasis.get("secondary", ""),
        background=emphasis.get("background", ""),
        hold=emphasis.get("hold", ""),
        guidance=guidance[:3],
    )


def _parse_markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None

    for line in text.splitlines():
        match = SECTION_HEADING.match(line)
        if match:
            current_heading = match.group(1)
            sections[current_heading] = []
            continue
        if current_heading is not None:
            sections[current_heading].append(line)

    return {heading: "\n".join(lines).strip() for heading, lines in sections.items()}


def _parse_emphasis_section(text: str) -> dict[str, str]:
    emphasis: dict[str, str] = {}
    for line in text.splitlines():
        normalized = line.replace("**", "").strip()
        for label in ("Primary", "Secondary", "Background", "Hold"):
            prefix = f"{label}:"
            if normalized.startswith(prefix):
                emphasis[label.lower()] = normalized[len(prefix) :].strip()
    return emphasis


def _single_line(text: str) -> str:
    return " ".join(part.strip() for part in text.splitlines() if part.strip())


def read_status_fields(path: Path) -> dict[str, str]:
    text = _read_text(path)
    return _parse_key_value_lines(text.splitlines())


def render_run_state(
    *,
    strategy: StrategySummary,
    results: list[ScientistResultRow],
    knowledge: list[KnowledgeEntry],
    findings: list[FindingEntry],
    leaderboard: list[LeaderboardRow],
    status_map: dict[str, dict[str, str]],
    max_recent_results: int,
    max_recent_knowledge: int,
    max_recent_findings: int,
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    scored_results = [row for row in results if row.score is not None]
    non_scored_results = [row for row in results if row.score is None]
    best_result = max(scored_results, key=lambda row: row.score or float("-inf")) if scored_results else None
    best_lb = max(
        (row for row in leaderboard if row.lb_score is not None),
        key=lambda row: row.lb_score or float("-inf"),
        default=None,
    )

    recent_results = results[-max_recent_results:]
    recent_knowledge = knowledge[-max_recent_knowledge:]
    recent_findings = findings[-max_recent_findings:]

    lines = [
        "# Supervisor Run State",
        f"generated_at: {generated_at}",
        "generated_by: harness.supervisor_snapshot",
        "",
        "Compact restart context for Codex supervisor sessions. Read this before any full histories.",
        "",
        "## Default Read Set",
        "- `AGENTS.md`",
        "- `agents/program.md`",
        "- `agents/supervisor/role.md`",
        "- this file",
    ]

    if status_map["strategy_request"].get("status") == "active":
        lines.append("- `agents/strategist/strategy-request.md`")
    if status_map["scientist_task"].get("status") == "active":
        lines.append("- `agents/scientist/scientist-task.md`")
    if status_map["analyst_hypothesis"].get("status") == "active":
        lines.append("- `agents/analyst/analyst-hypothesis.md`")

    lines.extend(
        [
            "",
            "## Current Strategy",
            f"- current_date: {strategy.current_date or 'unknown'}",
            f"- deadline_assumption: {strategy.deadline_assumption or 'unknown'}",
            f"- days_remaining: {strategy.days_remaining or 'unknown'}",
            f"- primary: {strategy.primary or 'unknown'}",
            f"- secondary: {strategy.secondary or 'unknown'}",
            f"- background: {strategy.background or 'unknown'}",
            f"- hold: {strategy.hold or 'unknown'}",
        ]
    )

    if strategy.guidance:
        lines.append("- guidance:")
        for item in strategy.guidance:
            lines.append(f"  {item}")

    lines.extend(
        [
            "",
            "## Control Files",
            f"- strategy_request: {status_map['strategy_request'].get('status', 'missing')}",
            f"- scientist_task: {status_map['scientist_task'].get('status', 'missing')}",
            f"- analyst_hypothesis: {status_map['analyst_hypothesis'].get('status', 'missing')}",
        ]
    )

    if status_map["scientist_task"].get("status") == "active":
        lines.append(
            f"- active_scientist_task: {status_map['scientist_task'].get('id', 'unknown')} | {status_map['scientist_task'].get('goal', 'no goal')}"
        )
    if status_map["analyst_hypothesis"].get("status") == "active":
        lines.append(
            f"- active_analyst_hypothesis: {status_map['analyst_hypothesis'].get('id', 'unknown')} | {status_map['analyst_hypothesis'].get('q', 'no question')}"
        )

    lines.extend(
        [
            "",
            "## Experiment Summary",
            f"- total_results: {len(results)}",
            f"- scored_results: {len(scored_results)}",
            f"- terminal_non_scored_results: {len(non_scored_results)}",
        ]
    )

    if best_result is not None:
        lines.append(f"- best_cv: {best_result.score:.6f} ({best_result.task_id}) | {best_result.desc}")
    else:
        lines.append("- best_cv: none")

    lines.append("- recent_results:")
    for row in recent_results:
        score = f"{row.score:.6f}" if row.score is not None else "-"
        lines.append(f"  - {row.task_id} | {score} | {row.desc}")

    lines.extend(
        [
            "",
            "## Analysis Summary",
            f"- knowledge_entries: {len(knowledge)}",
            f"- findings_entries: {len(findings)}",
            "- recent_knowledge:",
        ]
    )
    for entry in recent_knowledge:
        lines.append(f"  - {entry.entry_id} | {entry.title} | {entry.summary or 'no summary'}")

    lines.append("- recent_findings:")
    for entry in recent_findings:
        lines.append(
            f"  - {entry.entry_id} | verdict={entry.verdict or 'unknown'} | conf={entry.confidence or 'unknown'} | q={entry.question or 'unknown'}"
        )

    lines.extend(
        [
            "",
            "## Leaderboard",
            f"- submissions_total: {len(leaderboard)}",
        ]
    )

    if best_lb is not None:
        lines.append(
            f"- best_lb: {best_lb.lb_score:.5f} ({best_lb.task_id}) | rank {best_lb.lb_rank if best_lb.lb_rank is not None else 'unknown'}"
        )
    else:
        lines.append("- best_lb: none")

    if leaderboard:
        latest_submission = leaderboard[-1]
        lb_score = f"{latest_submission.lb_score:.5f}" if latest_submission.lb_score is not None else latest_submission.status
        lines.append(
            f"- latest_submission: {latest_submission.task_id} | {latest_submission.submitted_at} | {lb_score} | {latest_submission.rationale}"
        )

    lines.extend(
        [
            "",
            "## Reset Policy",
            "- After any durable state change, run `uv run python -m harness.supervisor_snapshot`.",
            "- Prefer a fresh Codex supervisor session after a completed checkpoint instead of carrying a large chat thread forward.",
        ]
    )

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
