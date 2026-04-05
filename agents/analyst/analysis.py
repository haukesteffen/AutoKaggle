#!/usr/bin/env python3
"""
A-018: Test whether S-104 materially improves Medium-class behavior versus S-102
while staying within 0.00003 balanced accuracy of S-094.

This script:
- loads existing OOF probability artifacts only
- compares balanced accuracy and classwise recall for S-094, S-102, and S-104
- measures changed-row flows focused on harmful true-Medium regressions and
  true-Medium Medium->High drift

No model training is performed.
"""

import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from sklearn.metrics import balanced_accuracy_score, confusion_matrix

from harness.dataset import CLASS_LABELS, load_train_with_folds, split_xy


ARTIFACT_ROOT = REPO_ROOT / "artifacts"
MODEL_PATHS = {
    "S-094": ARTIFACT_ROOT / "S-094" / "oof-preds.npy",
    "S-102": ARTIFACT_ROOT / "S-102" / "oof-preds.npy",
    "S-104": ARTIFACT_ROOT / "S-104" / "oof-preds.npy",
}

CLASS_TO_IDX = {label: idx for idx, label in enumerate(CLASS_LABELS)}
MEDIUM = CLASS_TO_IDX["Medium"]
HIGH = CLASS_TO_IDX["High"]


def load_train_labels() -> np.ndarray:
    train_df = load_train_with_folds()
    _, y = split_xy(train_df)
    return y.to_numpy() if hasattr(y, "to_numpy") else np.asarray(y)


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


def class_recalls(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    cm = confusion_matrix(y_true, y_pred, labels=np.arange(len(CLASS_LABELS)))
    recalls = cm.diagonal() / cm.sum(axis=1)
    return {label: float(recalls[idx]) for idx, label in enumerate(CLASS_LABELS)}


def summarize_vs_benchmark(
    y_true: np.ndarray, benchmark_pred: np.ndarray, candidate_pred: np.ndarray
) -> dict[str, int]:
    changed = benchmark_pred != candidate_pred
    true_medium_changed = changed & (y_true == MEDIUM)
    harmful_medium = true_medium_changed & (benchmark_pred == MEDIUM) & (candidate_pred != MEDIUM)
    medium_to_high = true_medium_changed & (benchmark_pred == MEDIUM) & (candidate_pred == HIGH)
    beneficial_medium = true_medium_changed & (benchmark_pred != MEDIUM) & (candidate_pred == MEDIUM)
    high_regressions = changed & (y_true == HIGH) & (benchmark_pred == HIGH) & (candidate_pred != HIGH)
    return {
        "changed_rows": int(changed.sum()),
        "true_medium_changed": int(true_medium_changed.sum()),
        "harmful_true_medium": int(harmful_medium.sum()),
        "true_medium_medium_to_high": int(medium_to_high.sum()),
        "beneficial_true_medium": int(beneficial_medium.sum()),
        "new_true_high_regressions": int(high_regressions.sum()),
    }


def flow_counter(y_true: np.ndarray, pred_a: np.ndarray, pred_b: np.ndarray) -> Counter[tuple[str, str, str]]:
    changed_idx = np.flatnonzero(pred_a != pred_b)
    return Counter(
        (
            CLASS_LABELS[int(y_true[i])],
            CLASS_LABELS[int(pred_a[i])],
            CLASS_LABELS[int(pred_b[i])],
        )
        for i in changed_idx
    )


def main() -> None:
    y = load_train_labels()
    oof = load_oof()
    preds = {name: np.argmax(arr, axis=1) for name, arr in oof.items()}

    scores = {name: float(balanced_accuracy_score(y, pred)) for name, pred in preds.items()}
    recalls = {name: class_recalls(y, pred) for name, pred in preds.items()}
    vs_094 = {
        "S-102": summarize_vs_benchmark(y, preds["S-094"], preds["S-102"]),
        "S-104": summarize_vs_benchmark(y, preds["S-094"], preds["S-104"]),
    }
    flows_104_vs_094 = flow_counter(y, preds["S-094"], preds["S-104"])

    print("=" * 80)
    print("A-018: S-104 practical Medium-behavior check versus S-102")
    print("Method: existing OOF probability artifacts only; no training")
    print(f"Rows: {len(y):,}")
    print(f"Classes: {CLASS_LABELS}")
    print("=" * 80)

    print("\nArtifacts")
    for name, path in MODEL_PATHS.items():
        print(f"- {name}: {path.relative_to(REPO_ROOT)}")

    print("\nBalanced Accuracy")
    for name in ("S-094", "S-102", "S-104"):
        print(f"- {name}: {scores[name]:.6f}")
    print(f"- S-104 minus S-094: {scores['S-104'] - scores['S-094']:+.6f}")
    print(f"- Within 0.00003 of S-094: {'yes' if (scores['S-094'] - scores['S-104']) <= 0.00003 else 'no'}")

    print("\nClasswise Recall")
    for label in CLASS_LABELS:
        print(
            f"- {label}: "
            f"S-094={recalls['S-094'][label]:.6f}, "
            f"S-102={recalls['S-102'][label]:.6f}, "
            f"S-104={recalls['S-104'][label]:.6f}"
        )

    print("\nChanged-Row Comparison Against S-094 Benchmark")
    for name in ("S-102", "S-104"):
        stats = vs_094[name]
        print(
            f"- {name} vs S-094: changed_rows={stats['changed_rows']}, "
            f"true_Medium_changed={stats['true_medium_changed']}, "
            f"harmful_true_Medium={stats['harmful_true_medium']}, "
            f"true_Medium_Medium_to_High={stats['true_medium_medium_to_high']}, "
            f"beneficial_true_Medium={stats['beneficial_true_medium']}, "
            f"new_true_High_regressions={stats['new_true_high_regressions']}"
        )

    print("\nS-104 Delta Relative to S-102")
    print(
        "- Harmful true-Medium regressions reduced versus S-102 "
        f"({vs_094['S-102']['harmful_true_medium']} -> {vs_094['S-104']['harmful_true_medium']}): "
        f"{'yes' if vs_094['S-104']['harmful_true_medium'] < vs_094['S-102']['harmful_true_medium'] else 'no'}"
    )
    print(
        "- True-Medium Medium->High drift reduced versus S-102 "
        f"({vs_094['S-102']['true_medium_medium_to_high']} -> {vs_094['S-104']['true_medium_medium_to_high']}): "
        f"{'yes' if vs_094['S-104']['true_medium_medium_to_high'] < vs_094['S-102']['true_medium_medium_to_high'] else 'no'}"
    )
    print(
        "- Medium recall improves over S-102: "
        f"{'yes' if recalls['S-104']['Medium'] > recalls['S-102']['Medium'] else 'no'} "
        f"({recalls['S-102']['Medium']:.6f} -> {recalls['S-104']['Medium']:.6f})"
    )

    print("\nLargest S-094 -> S-104 Changed Flows")
    for (truth, pred_a, pred_b), count in flows_104_vs_094.most_common(8):
        print(f"- true={truth}: {pred_a} -> {pred_b}: {count}")

    print("\nDecision Facts")
    print(
        "- S-104 reduces harmful true-Medium regressions versus S-102: "
        f"{'yes' if vs_094['S-104']['harmful_true_medium'] < vs_094['S-102']['harmful_true_medium'] else 'no'}"
    )
    print(
        "- S-104 reduces true-Medium Medium->High drift versus S-102: "
        f"{'yes' if vs_094['S-104']['true_medium_medium_to_high'] < vs_094['S-102']['true_medium_medium_to_high'] else 'no'}"
    )
    print(
        "- S-104 stays within 0.00003 balanced accuracy of S-094: "
        f"{'yes' if (scores['S-094'] - scores['S-104']) <= 0.00003 else 'no'}"
    )


if __name__ == "__main__":
    main()
