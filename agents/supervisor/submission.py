import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from harness.dataset import (
    CLASS_LABELS,
    ID_COLUMN,
    TARGET_COLUMN,
    TEST_PATH,
    class_probabilities_to_indices,
    decode_target_labels,
)


def main() -> None:
    args = _parse_args()
    output_path = create_submission_csv(args.artifact_dir, args.output)
    print(f"wrote {output_path}")


def create_submission_csv(artifact_dir: Path, output: Path) -> Path:
    artifact_dir = _normalize_repo_path(artifact_dir)
    output = _normalize_repo_path(output)

    test_ids = pd.read_csv(_normalize_repo_path(TEST_PATH), usecols=[ID_COLUMN])[ID_COLUMN]
    preds = np.load(artifact_dir / "test-preds.npy", allow_pickle=False)
    if preds.ndim != 2 or preds.shape[1] != len(CLASS_LABELS):
        raise ValueError(f"test predictions must be a 2D matrix with {len(CLASS_LABELS)} class columns")
    if len(preds) != len(test_ids):
        raise ValueError("test prediction count does not match the test set row count")

    predicted_labels = decode_target_labels(class_probabilities_to_indices(preds))
    submission = pd.DataFrame({ID_COLUMN: test_ids, TARGET_COLUMN: predicted_labels})
    output.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(output, index=False)
    return output


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("agents/supervisor/submission.csv"))
    return parser.parse_args()


def _normalize_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    main()
