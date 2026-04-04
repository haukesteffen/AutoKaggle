#!/usr/bin/env python3
"""
A-014: Test whether adding S-052 to the S-093 stacker creates a durable recovery pattern.

This script:
- loads existing OOF probability artifacts only
- compares S-093 vs S-094 balanced accuracy and classwise recall
- isolates rows whose argmax prediction changes
- checks whether changed-case recoveries, especially for High, align with S-052

No model training is performed.
"""

import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from sklearn.metrics import balanced_accuracy_score

from harness.dataset import CLASS_LABELS, load_train_with_folds, split_xy


ARTIFACT_ROOT = REPO_ROOT / "artifacts"
MODEL_PATHS = {
    "S-052": ARTIFACT_ROOT / "S-052" / "oof-preds.npy",
    "S-093": ARTIFACT_ROOT / "S-093" / "oof-preds.npy",
    "S-094": ARTIFACT_ROOT / "S-094" / "oof-preds.npy",
}


def load_labels() -> np.ndarray:
    train_df = load_train_with_folds()
    _, y = split_xy(train_df)
    if hasattr(y, "to_numpy"):
        return y.to_numpy()
    return np.asarray(y)


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


def ba(y: np.ndarray, pred: np.ndarray) -> float:
    return balanced_accuracy_score(y, pred)


def classwise_recalls(y: np.ndarray, pred: np.ndarray) -> list[float]:
    return [float(np.mean(pred[y == cls] == cls)) for cls in range(len(CLASS_LABELS))]


def fmt_recall_triplet(values: list[float]) -> str:
    return ", ".join(f"{label}={value:.6f}" for label, value in zip(CLASS_LABELS, values))


def main() -> None:
    y = load_labels()
    oof = load_oof()
    pred_052 = np.argmax(oof["S-052"], axis=1)
    pred_093 = np.argmax(oof["S-093"], axis=1)
    pred_094 = np.argmax(oof["S-094"], axis=1)

    changed = pred_093 != pred_094
    changed_idx = np.flatnonzero(changed)
    recall_093 = classwise_recalls(y, pred_093)
    recall_094 = classwise_recalls(y, pred_094)
    recall_delta = [b - a for a, b in zip(recall_093, recall_094)]

    recovered = (pred_093 != y) & (pred_094 == y)
    lost = (pred_093 == y) & (pred_094 != y)

    recovered_high = (y == 0) & recovered
    lost_high = (y == 0) & lost

    s052_matches_094 = pred_052[changed] == pred_094[changed]
    s052_matches_093 = pred_052[changed] == pred_093[changed]

    delta_cases = Counter()
    for yt, old_pred, new_pred in zip(y[changed], pred_093[changed], pred_094[changed]):
        delta_cases[(CLASS_LABELS[yt], CLASS_LABELS[old_pred], CLASS_LABELS[new_pred])] += 1

    print("=" * 80)
    print("A-014: S-094 vs S-093 changed-case attribution")
    print("Method: existing OOF probability artifacts only; no training")
    print(f"Rows: {len(y):,}")
    print(f"Classes: {CLASS_LABELS}")
    print("=" * 80)

    print("\nArtifacts")
    for name, path in MODEL_PATHS.items():
        print(f"- {name}: {path.relative_to(REPO_ROOT)}")

    print("\nBalanced Accuracy")
    print(f"- S-093: {ba(y, pred_093):.6f}")
    print(f"- S-094: {ba(y, pred_094):.6f}")
    print(f"- Delta (S-094 - S-093): {ba(y, pred_094) - ba(y, pred_093):+.6f}")

    print("\nClasswise Recall")
    print(f"- S-093: {fmt_recall_triplet(recall_093)}")
    print(f"- S-094: {fmt_recall_triplet(recall_094)}")
    print(f"- Delta: {fmt_recall_triplet(recall_delta)}")

    print("\nChanged Argmax Rows")
    print(f"- Changed rows: {len(changed_idx)} / {len(y)} ({len(changed_idx) / len(y):.6%})")
    print(f"- Wrong -> right: {int(recovered.sum())}")
    print(f"- Right -> wrong: {int(lost.sum())}")
    print(f"- Wrong -> wrong: {int((changed & ~recovered & ~lost).sum())}")
    print(
        "- True-label mix among changed rows: "
        + ", ".join(
            f"{label}={int(np.sum(y[changed] == cls))}"
            for cls, label in enumerate(CLASS_LABELS)
        )
    )

    print("\nChanged Rows by True Class")
    for cls, label in enumerate(CLASS_LABELS):
        class_recovered = int(np.sum((y == cls) & recovered))
        class_lost = int(np.sum((y == cls) & lost))
        print(f"- {label}: recovered={class_recovered}, lost={class_lost}, net={class_recovered - class_lost:+d}")

    print("\nHigh-Class Attribution")
    print(f"- High recovered by S-094: {int(recovered_high.sum())}")
    print(f"- High lost by S-094: {int(lost_high.sum())}")
    print(
        f"- Recovered Highs where S-052 also predicted High: {int(np.sum(pred_052[recovered_high] == 0))}"
    )
    print(
        f"- Lost Highs where S-052 predicted non-High: {int(np.sum(pred_052[lost_high] != 0))}"
    )
    print(
        "- S-052 predictions on recovered Highs: "
        + ", ".join(
            f"{label}={count}"
            for label, count in zip(CLASS_LABELS, np.bincount(pred_052[recovered_high], minlength=3))
        )
    )
    print(
        "- S-052 predictions on lost Highs: "
        + ", ".join(
            f"{label}={count}"
            for label, count in zip(CLASS_LABELS, np.bincount(pred_052[lost_high], minlength=3))
        )
    )

    print("\nS-052 Alignment on Changed Rows")
    print(f"- S-052 matches S-094 on changed rows: {int(np.sum(s052_matches_094))}")
    print(f"- S-052 matches S-093 on changed rows: {int(np.sum(s052_matches_093))}")
    for cls, label in enumerate(CLASS_LABELS):
        mask = changed & (y == cls)
        print(
            f"- True {label}: S-052 matches S-094={int(np.sum(pred_052[mask] == pred_094[mask]))}, "
            f"S-052 matches S-093={int(np.sum(pred_052[mask] == pred_093[mask]))}"
        )

    print("\nLargest Changed-Case Flows")
    for (true_label, old_pred, new_pred), count in delta_cases.most_common(8):
        print(f"- true={true_label}: {old_pred} -> {new_pred}: {count}")

    print("\nDecision Facts")
    print(f"- High recall changed: {'yes' if recall_delta[0] != 0.0 else 'no'}")
    print(f"- Net High recoveries > 0: {'yes' if int(recovered_high.sum()) > int(lost_high.sum()) else 'no'}")
    print(
        "- Recovered Highs mostly supported by S-052: "
        f"{'yes' if int(np.sum(pred_052[recovered_high] == 0)) > int(recovered_high.sum()) / 2 else 'no'}"
    )
    print(
        "- BA lift driven mainly by Medium recall: "
        f"{'yes' if recall_delta[2] > 0 and recall_delta[0] == 0 and abs(recall_delta[2]) > abs(recall_delta[1]) else 'no'}"
    )


if __name__ == "__main__":
    main()
