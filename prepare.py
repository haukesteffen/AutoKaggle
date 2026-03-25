import csv
import subprocess
from pathlib import Path
from zipfile import ZipFile

from sklearn.model_selection import KFold


DATA_DIR = Path("data")
TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH = DATA_DIR / "test.csv"
FOLDS_PATH = DATA_DIR / "folds.csv"
COMPETITION = "playground-series-s6e3"
ID_COLUMN = "id"
TARGET_COLUMN = "Churn"
POSITIVE_LABEL = "Yes"
NEGATIVE_LABEL = "No"
FOLD_ROW_INDEX_COLUMN = "row_idx"
FOLD_COLUMN = "fold"
N_SPLITS = 5
RANDOM_STATE = 42


def main():
    DATA_DIR.mkdir(exist_ok=True)

    if not TRAIN_PATH.exists() or not TEST_PATH.exists():
        zip_path = DATA_DIR / f"{COMPETITION}.zip"
        subprocess.run(
            [
                "uv",
                "run",
                "kaggle",
                "competitions",
                "download",
                "-c",
                COMPETITION,
                "-p",
                str(DATA_DIR),
                "--force",
            ],
            check=True,
        )
        with ZipFile(zip_path) as zf:
            zf.extractall(DATA_DIR)
        zip_path.unlink()

    with TRAIN_PATH.open(newline="") as f:
        train_rows = list(csv.DictReader(f))
    folds = [-1] * len(train_rows)

    splitter = KFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    for fold, (_, valid_idx) in enumerate(splitter.split(train_rows)):
        for i in valid_idx:
            folds[i] = fold

    with FOLDS_PATH.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([FOLD_ROW_INDEX_COLUMN, FOLD_COLUMN])
        for i, fold in enumerate(folds):
            writer.writerow([i, fold])


if __name__ == "__main__":
    main()
