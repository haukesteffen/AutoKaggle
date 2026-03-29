import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_PATH = Path("agents/analyst/analysis.py")
DEFAULT_ERRORS_FILENAME = "analysis-errors.md"


@dataclass(frozen=True)
class HypothesisMetadata:
    title: str
    question: str
    reference: str | None


def main() -> None:
    args = _parse_args()
    analysis_path = _normalize_repo_path(args.analysis_path)
    hypothesis_file = _normalize_repo_path(args.hypothesis_file)
    findings_file = _normalize_repo_path(args.findings_file)
    errors_file = (
        _normalize_repo_path(args.errors_file)
        if args.errors_file
        else findings_file.with_name(DEFAULT_ERRORS_FILENAME)
    )

    hypothesis_text = hypothesis_file.read_text()
    metadata = _extract_hypothesis_metadata(hypothesis_text)

    completed = subprocess.run(
        [sys.executable, str(analysis_path)],
        capture_output=True,
        cwd=REPO_ROOT,
        env=_analysis_env(),
        text=True,
    )

    if completed.returncode != 0:
        _append_failure_entry(
            errors_file=errors_file,
            metadata=metadata,
            analysis_path=analysis_path,
            completed=completed,
        )
        _report_failure(analysis_path=analysis_path, errors_file=errors_file, completed=completed)
        raise SystemExit(completed.returncode)

    _append_findings_entry(
        findings_file=findings_file,
        metadata=metadata,
        stdout=completed.stdout,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-path", type=Path, default=DEFAULT_ANALYSIS_PATH)
    parser.add_argument("--hypothesis-file", type=Path, required=True)
    parser.add_argument("--findings-file", type=Path, required=True)
    parser.add_argument("--errors-file", type=Path)
    return parser.parse_args()


def _normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def _analysis_env() -> dict[str, str]:
    env = os.environ.copy()
    repo_root = str(REPO_ROOT)
    current_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = repo_root if not current_pythonpath else f"{repo_root}{os.pathsep}{current_pythonpath}"
    return env


def _extract_hypothesis_metadata(hypothesis_text: str) -> HypothesisMetadata:
    fields = _parse_key_value_fields(hypothesis_text)
    question = fields.get("q") or _extract_legacy_question(hypothesis_text) or "Analysis"
    return HypothesisMetadata(
        title=fields.get("id") or question,
        question=question,
        reference=fields.get("reference"),
    )


def _extract_title(hypothesis_text: str) -> str:
    return _extract_hypothesis_metadata(hypothesis_text).title


def _parse_key_value_fields(hypothesis_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in hypothesis_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key not in {"status", "id", "at", "q", "reference"}:
            continue
        normalized_value = value.strip()
        if normalized_value and normalized_key not in fields:
            fields[normalized_key] = normalized_value
    return fields


def _extract_legacy_question(hypothesis_text: str) -> str | None:
    lines = hypothesis_text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        for prefix in ("**Hypothesis:**", "**Question:**"):
            if not stripped.startswith(prefix):
                continue
            title = stripped.removeprefix(prefix).strip()
            if title:
                return title
            fallback_title = _next_nonempty_line(lines[index + 1 :])
            if fallback_title:
                return fallback_title
    return None


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _append_findings_entry(findings_file: Path, metadata: HypothesisMetadata, stdout: str) -> None:
    findings_file.parent.mkdir(parents=True, exist_ok=True)
    with findings_file.open("a") as f:
        if f.tell() > 0:
            f.write("\n\n")
        f.write(f"## {metadata.title}\n")
        f.write(f"at: {_utc_timestamp()}\n")
        f.write(f"q: {metadata.question}\n")
        f.write("verdict: *(fill in: supported | rejected | inconclusive)*\n")
        f.write("conf: *(fill in: high | medium | low)*\n")
        if metadata.reference:
            f.write(f"reference: {metadata.reference}\n")
        f.write("evidence:\n")
        f.write(f"{_format_stream(stdout)}\n\n")
        f.write("follow_up:\n")
        f.write("- *(fill in yes/no hypothesis)*\n")
        f.write("- *(fill in yes/no hypothesis)*\n")
        f.write("- *(fill in yes/no hypothesis)*\n")


def _append_failure_entry(
    errors_file: Path,
    metadata: HypothesisMetadata,
    analysis_path: Path,
    completed: subprocess.CompletedProcess[str],
) -> None:
    errors_file.parent.mkdir(parents=True, exist_ok=True)
    with errors_file.open("a") as f:
        if f.tell() > 0:
            f.write("\n\n")
        f.write(f"## {metadata.title}\n")
        f.write(f"at: {_utc_timestamp()}\n")
        f.write(f"q: {metadata.question}\n")
        if metadata.reference:
            f.write(f"reference: {metadata.reference}\n")
        f.write(f"analysis_path: `{_display_path(analysis_path)}`\n")
        f.write(f"exit_code: `{completed.returncode}`\n")
        f.write("stdout:\n")
        f.write(f"{_format_stream(completed.stdout)}\n\n")
        f.write("stderr:\n")
        f.write(f"{_format_stream(completed.stderr)}\n")


def _report_failure(
    analysis_path: Path, errors_file: Path, completed: subprocess.CompletedProcess[str]
) -> None:
    print(
        f"error: {_display_path(analysis_path)} exited with code {completed.returncode}; details written to {_display_path(errors_file)}",
        file=sys.stderr,
    )
    if completed.stdout.strip():
        print("\n[analysis stdout]", file=sys.stderr)
        print(completed.stdout.rstrip(), file=sys.stderr)
    if completed.stderr.strip():
        print("\n[analysis stderr]", file=sys.stderr)
        print(completed.stderr.rstrip(), file=sys.stderr)


def _next_nonempty_line(lines: list[str]) -> str | None:
    for line in lines:
        stripped = line.strip()
        if stripped:
            return stripped
    return None


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


if __name__ == "__main__":
    main()
