from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile


COMPETITION_SLUG = "playground-series-s6e3"
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"


def download_competition_data(force: bool = True) -> list[Path]:
    """Download the Kaggle competition archive, extract it, and delete the zip."""
    if shutil.which("uv") is None:
        raise RuntimeError(
            "uv was not found on PATH. Install it before running prepare.py."
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DATA_DIR / f"{COMPETITION_SLUG}.zip"

    cmd = [
        "uv",
        "run",
        "kaggle",
        "competitions",
        "download",
        "-c",
        COMPETITION_SLUG,
        "-p",
        str(DATA_DIR),
    ]
    if force:
        cmd.append("--force")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Kaggle download failed. Check uv, Kaggle authentication, and competition access."
        ) from exc

    if not archive_path.exists():
        raise FileNotFoundError(
            f"Expected archive was not downloaded: {archive_path}"
        )

    with ZipFile(archive_path) as zf:
        zf.extractall(DATA_DIR)
        extracted_paths = [DATA_DIR / name for name in zf.namelist()]

    archive_path.unlink()
    return extracted_paths


def main() -> None:
    extracted_paths = download_competition_data()
    print(f"downloaded_files: {len(extracted_paths)}")
    for path in extracted_paths:
        print(path.relative_to(PROJECT_ROOT))


if __name__ == "__main__":
    main()
