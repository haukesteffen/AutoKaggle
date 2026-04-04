#!/usr/bin/env python3
"""
A-017: Test whether harmful true-Medium changes in S-102 are concentrated in one fold.

This script:
- loads existing OOF probability artifacts only
- identifies true-Medium rows that regress from Medium under S-094 to another class under S-102
- joins those rows to the fixed fold assignments from the harness
- reports whether any one fold accounts for a clear majority of those regressions

No model training is performed.
"""

import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from harness.dataset import CLASS_LABELS, FOLD_COLUMN, load_train_with_folds, split_xy


ARTIFACT_ROOT = REPO_ROOT / "artifacts"
MODEL_PATHS = {
    "S-094": ARTIFACT_ROOT / "S-094" / "oof-preds.npy",
    "S-102": ARTIFACT_ROOT / "S-102" / "oof-preds.npy",
}

CLASS_TO_IDX = {label: idx for idx, label in enumerate(CLASS_LABELS)}
MEDIUM = CLASS_TO_IDX["Medium"]


def load_train_arrays() -> tuple[np.ndarray, np.ndarray]:
    train_df = load_train_with_folds()
    _, y = split_xy(train_df)
    labels = y.to_numpy() if hasattr(y, "to_numpy") else np.asarray(y)
    folds = train_df[FOLD_COLUMN].to_numpy()
    return labels, folds


def load_oof() -> dict[str, np.ndarray]:
    arrays: dict[str, np.ndarray] = {}
    expected_shape = None
    for name, path in MODEL_PATHS.items():
        arr = np.load(path)
        if arr.ndim != 2 or arr.shape[1] != len(CLASS_LABELS):
            raise ValueError(f"{name} OOF shape invalid: {arr.shape}")
        if expected_shape is None:
            expected_shape = arr.shape
        elif arr.shape != expected_shape:
            raise ValueError(f"OOF shape mismatch for {name}: {arr.shape} vs {expected_shape}")
        arrays[name] = arr
    return arrays


def main() -> None:
    y, folds = load_train_arrays()
    oof = load_oof()
    pred_094 = np.argmax(oof["S-094"], axis=1)
    pred_102 = np.argmax(oof["S-102"], axis=1)

    harmful_medium = (y == MEDIUM) & (pred_094 == MEDIUM) & (pred_102 != MEDIUM)
    harmful_idx = np.flatnonzero(harmful_medium)
    harmful_folds = folds[harmful_medium]
    fold_counts = Counter(int(fold) for fold in harmful_folds)
    target_counts = Counter(CLASS_LABELS[int(pred)] for pred in pred_102[harmful_medium])

    total = int(harmful_medium.sum())
    majority_fold, majority_count = max(fold_counts.items(), key=lambda item: item[1])
    majority_share = majority_count / total if total else float("nan")

    print("=" * 80)
    print("A-017: Fold concentration of harmful true-Medium S-102 regressions")
    print("Method: existing OOF probability artifacts plus fixed fold assignments; no training")
    print(f"Rows: {len(y):,}")
    print(f"Classes: {CLASS_LABELS}")
    print("=" * 80)

    print("\nArtifacts")
    for name, path in MODEL_PATHS.items():
        print(f"- {name}: {path.relative_to(REPO_ROOT)}")
    print("- Folds: harness.dataset.load_train_with_folds()")

    print("\nTarget Regression Slice")
    print(
        "- Harmful true-Medium regressions: "
        f"{total} rows where truth=Medium, S-094=Medium, S-102!=Medium"
    )
    print(
        "- S-102 destination classes within this slice: "
        + ", ".join(f"{label}={count}" for label, count in sorted(target_counts.items()))
    )

    print("\nFold Distribution")
    for fold in sorted(fold_counts):
        count = fold_counts[fold]
        print(f"- Fold {fold}: {count} ({count / total:.2%})")

    print("\nLargest Within-Slice Flows")
    per_fold_dest = Counter((int(fold), CLASS_LABELS[int(pred)]) for fold, pred in zip(harmful_folds, pred_102[harmful_medium]))
    for (fold, dest), count in per_fold_dest.most_common(8):
        print(f"- Fold {fold}: Medium -> {dest}: {count}")

    print("\nDecision Facts")
    print(f"- Largest fold by count: fold {majority_fold} with {majority_count} rows ({majority_share:.2%})")
    print(
        "- Any one fold accounts for a strict majority (>50%) of harmful true-Medium regressions: "
        f"{'yes' if majority_share > 0.5 else 'no'}"
    )
    print(
        "- Distribution is spread across multiple folds rather than dominated by one: "
        f"{'yes' if majority_share <= 0.5 else 'no'}"
    )


if __name__ == "__main__":
    main()
