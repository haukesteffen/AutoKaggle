import argparse
import subprocess
from pathlib import Path

from harness.dataset import COMPETITION

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUBMISSION_FILE = Path("agents/supervisor/submission.csv")


def main() -> None:
    args = _parse_args()
    submission_file = _normalize_repo_path(args.submission_file)

    subprocess.run(
        [
            "uv",
            "run",
            "kaggle",
            "competitions",
            "submit",
            "-c",
            COMPETITION,
            "-f",
            str(submission_file),
            "-m",
            args.hash,
        ],
        check=True,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--submission-file", type=Path, default=DEFAULT_SUBMISSION_FILE)
    return parser.parse_args()


def _normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    main()
