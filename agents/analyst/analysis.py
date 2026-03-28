import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd

from harness.dataset import TARGET_COLUMN, TEST_PATH, TRAIN_PATH


def main() -> None:
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    print(f"train_rows: {len(train_df)}")
    print(f"test_rows: {len(test_df)}")
    print(f"feature_count: {len(train_df.columns) - 2}")
    print("target_distribution:")
    print(train_df[TARGET_COLUMN].value_counts(normalize=True).sort_index())

    missing_rate = train_df.isna().mean().sort_values(ascending=False)
    top_missing = missing_rate[missing_rate > 0].head(10)
    if top_missing.empty:
        print("top_missing_columns: none")
    else:
        print("top_missing_columns:")
        print(top_missing)


if __name__ == "__main__":
    main()
