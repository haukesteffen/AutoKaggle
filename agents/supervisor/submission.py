import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd

from harness.dataset import ID_COLUMN, TARGET_COLUMN, TEST_PATH


def main() -> None:
    args = _parse_args()

    test_ids = pd.read_csv(TEST_PATH, usecols=[ID_COLUMN])[ID_COLUMN]
    preds = np.load(args.artifact_dir / "test-preds.npy")
    if len(preds) != len(test_ids):
        raise ValueError("test prediction count does not match the test set row count")

    submission = pd.DataFrame({ID_COLUMN: test_ids, TARGET_COLUMN: preds})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    submission.to_csv(args.output, index=False)
    print(f"wrote {args.output}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("agents/supervisor/submission.csv"))
    return parser.parse_args()


if __name__ == "__main__":
    main()
