import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    args = _parse_args()

    hypothesis_text = args.hypothesis_file.read_text()
    title = _extract_title(hypothesis_text)

    completed = subprocess.run(
        [sys.executable, "analysis.py"],
        capture_output=True,
        text=True,
    )

    args.findings_file.parent.mkdir(parents=True, exist_ok=True)
    with args.findings_file.open("a") as f:
        if f.tell() > 0:
            f.write("\n\n")
        f.write(f"## {title}\n")
        f.write(f"*{_utc_timestamp()}*\n\n")
        f.write("**Hypothesis:**\n")
        f.write(f"{hypothesis_text.rstrip()}\n\n")
        f.write("**Verdict:** *(fill in: Supported / Rejected / Inconclusive)*\n\n")
        f.write("**Evidence:**\n")
        f.write(f"{_format_evidence(completed.stdout, completed.stderr, completed.returncode)}\n\n")
        f.write("**Implications:**\n")
        f.write("*(fill in)*\n\n")
        f.write("**Suggested next hypotheses:** *(optional)*\n")
        f.write("*(fill in or delete)*\n")

    if completed.returncode != 0:
        print(
            f"warning: analysis.py exited with code {completed.returncode}; stderr was appended to the findings entry",
            file=sys.stderr,
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hypothesis-file", type=Path, required=True)
    parser.add_argument("--findings-file", type=Path, required=True)
    return parser.parse_args()


def _extract_title(hypothesis_text: str) -> str:
    for line in hypothesis_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("**Question:**"):
            return stripped.removeprefix("**Question:**").strip() or "Analysis"
    return "Analysis"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _format_evidence(stdout: str, stderr: str, returncode: int) -> str:
    sections: list[str] = []
    if stdout.strip():
        sections.append(stdout.rstrip())
    if returncode != 0 and stderr.strip():
        sections.append(f"[stderr]\n{stderr.rstrip()}")
    if not sections:
        return "*(no output)*"
    return "\n\n".join(sections)


if __name__ == "__main__":
    main()
