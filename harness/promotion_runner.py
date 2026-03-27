import argparse
import subprocess

from harness.dataset import COMPETITION


def main() -> None:
    args = _parse_args()

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
            "submission.csv",
            "-m",
            args.hash,
        ],
        check=True,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hash", required=True)
    parser.add_argument("--tag", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
