import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANALYSIS_PATH = Path("work/analysis.py")
DEFAULT_TASK_PATH = Path("state/analyst-task.md")
DEFAULT_ARTIFACTS_ROOT = Path("artifacts")
DEFAULT_STDOUT_FILENAME = "analysis-stdout.txt"
DEFAULT_FAILURE_FILENAME = "analysis-run.log"


@dataclass(frozen=True)
class AnalysisTaskMetadata:
    status: str
    task_id: str
    question: str
    reference: str | None


def main() -> None:
    args = _parse_args()
    analysis_path = _normalize_repo_path(args.analysis_path)
    task_file = _normalize_repo_path(args.hypothesis_file)

    try:
        metadata = _read_task_metadata(task_file)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if metadata.status != "active":
        print("status: no_active_hypothesis")
        return

    artifact_dir = _artifact_dir(metadata.task_id)
    stdout_file = artifact_dir / DEFAULT_STDOUT_FILENAME
    errors_file = (
        _normalize_repo_path(args.errors_file)
        if args.errors_file
        else artifact_dir / DEFAULT_FAILURE_FILENAME
    )

    completed = subprocess.run(
        [sys.executable, str(analysis_path)],
        capture_output=True,
        cwd=REPO_ROOT,
        env=_analysis_env(),
        text=True,
    )

    if completed.returncode != 0:
        _write_failure_artifact(
            errors_file=errors_file,
            metadata=metadata,
            analysis_path=analysis_path,
            completed=completed,
        )
        _report_failure(analysis_path=analysis_path, errors_file=errors_file, completed=completed)
        raise SystemExit(completed.returncode)

    _write_stdout_artifact(stdout_file=stdout_file, stdout=completed.stdout)
    print(f"status: success; stdout written to {_display_path(stdout_file)}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-path", type=Path, default=DEFAULT_ANALYSIS_PATH)
    parser.add_argument("--hypothesis-file", type=Path, default=DEFAULT_TASK_PATH)
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


def _read_task_metadata(task_file: Path) -> AnalysisTaskMetadata:
    fields = _parse_key_value_fields(task_file.read_text())
    status = fields.get("status", "none")
    if status != "active":
        return AnalysisTaskMetadata(
            status=status,
            task_id=fields.get("id", "none"),
            question=fields.get("q", "none"),
            reference=fields.get("reference"),
        )

    task_id = fields.get("id")
    if not task_id or task_id == "none":
        raise ValueError("active analyst task is missing id")
    question = fields.get("q")
    if not question or question == "none":
        raise ValueError("active analyst task is missing q")

    return AnalysisTaskMetadata(
        status=status,
        task_id=task_id,
        question=question,
        reference=fields.get("reference"),
    )


def _parse_key_value_fields(task_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in task_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key not in {"status", "id", "at", "q", "decision_use", "reference"}:
            continue
        normalized_value = value.strip()
        if normalized_value and normalized_key not in fields:
            fields[normalized_key] = normalized_value
    return fields


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _write_stdout_artifact(stdout_file: Path, stdout: str) -> None:
    stdout_file.parent.mkdir(parents=True, exist_ok=True)
    stdout_file.write_text(stdout)


def _write_failure_artifact(
    errors_file: Path,
    metadata: AnalysisTaskMetadata,
    analysis_path: Path,
    completed: subprocess.CompletedProcess[str],
) -> None:
    errors_file.parent.mkdir(parents=True, exist_ok=True)
    details = [
        f"at: {_utc_timestamp()}",
        f"id: {metadata.task_id}",
        f"q: {metadata.question}",
    ]
    if metadata.reference:
        details.append(f"reference: {metadata.reference}")
    details.extend(
        [
            f"analysis_path: {_display_path(analysis_path)}",
            f"exit_code: {completed.returncode}",
            "stdout:",
            _format_stream(completed.stdout),
            "",
            "stderr:",
            _format_stream(completed.stderr),
            "",
        ]
    )
    errors_file.write_text("\n".join(details))


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


def _artifact_dir(task_id: str) -> Path:
    return _normalize_repo_path(DEFAULT_ARTIFACTS_ROOT / task_id)


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
