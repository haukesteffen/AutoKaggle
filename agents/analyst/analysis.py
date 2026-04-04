#!/usr/bin/env python3
"""
A-015: Attribute the S-094 over S-093 lift on changed rows.

This script:
- loads existing OOF probability artifacts only
- isolates rows where S-093 and S-094 disagree in argmax prediction
- compares S-052 alignment with beneficial Medium corrections vs High recoveries
- reports whether the changed-row evidence favors a Medium-signal explanation

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

CLASS_TO_IDX = {label: idx for idx, label in enumerate(CLASS_LABELS)}
HIGH = CLASS_TO_IDX["High"]
LOW = CLASS_TO_IDX["Low"]
MEDIUM = CLASS_TO_IDX["Medium"]


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


def support_stats(
    mask: np.ndarray,
    s052_probs: np.ndarray,
    target_class: int,
    old_pred: np.ndarray,
    new_pred: np.ndarray,
) -> dict[str, float]:
    count = int(mask.sum())
    if count == 0:
        return {
            "count": 0,
            "argmax_support": 0,
            "target_gt_old": 0,
            "target_gt_new": 0,
            "mean_target_prob": float("nan"),
            "mean_old_prob": float("nan"),
            "mean_new_prob": float("nan"),
            "mean_margin_vs_old": float("nan"),
            "mean_margin_vs_new": float("nan"),
        }

    rows = np.flatnonzero(mask)
    probs = s052_probs[rows]
    old = old_pred[rows]
    new = new_pred[rows]
    target_probs = probs[:, target_class]
    old_probs = probs[np.arange(count), old]
    new_probs = probs[np.arange(count), new]

    return {
        "count": count,
        "argmax_support": int(np.sum(np.argmax(probs, axis=1) == target_class)),
        "target_gt_old": int(np.sum(target_probs > old_probs)),
        "target_gt_new": int(np.sum(target_probs > new_probs)),
        "mean_target_prob": float(np.mean(target_probs)),
        "mean_old_prob": float(np.mean(old_probs)),
        "mean_new_prob": float(np.mean(new_probs)),
        "mean_margin_vs_old": float(np.mean(target_probs - old_probs)),
        "mean_margin_vs_new": float(np.mean(target_probs - new_probs)),
    }


def fmt_support(label: str, stats: dict[str, float]) -> None:
    print(f"- {label}: count={stats['count']}")
    print(
        f"  argmax_support={stats['argmax_support']} | "
        f"target_prob>old_pred_prob={stats['target_gt_old']} | "
        f"target_prob>new_pred_prob={stats['target_gt_new']}"
    )
    print(
        f"  mean_target_prob={stats['mean_target_prob']:.6f} | "
        f"mean_old_pred_prob={stats['mean_old_prob']:.6f} | "
        f"mean_new_pred_prob={stats['mean_new_prob']:.6f}"
    )
    print(
        f"  mean_margin_vs_old={stats['mean_margin_vs_old']:+.6f} | "
        f"mean_margin_vs_new={stats['mean_margin_vs_new']:+.6f}"
    )


def main() -> None:
    y = load_labels()
    oof = load_oof()
    pred_052 = np.argmax(oof["S-052"], axis=1)
    pred_093 = np.argmax(oof["S-093"], axis=1)
    pred_094 = np.argmax(oof["S-094"], axis=1)

    changed = pred_093 != pred_094
    changed_idx = np.flatnonzero(changed)

    beneficial_medium = changed & (y == MEDIUM) & (pred_093 != MEDIUM) & (pred_094 == MEDIUM)
    harmful_medium = changed & (y == MEDIUM) & (pred_093 == MEDIUM) & (pred_094 != MEDIUM)
    high_recovery = changed & (y == HIGH) & (pred_093 != HIGH) & (pred_094 == HIGH)
    high_loss = changed & (y == HIGH) & (pred_093 == HIGH) & (pred_094 != HIGH)

    medium_stats = support_stats(beneficial_medium, oof["S-052"], MEDIUM, pred_093, pred_094)
    medium_harm_stats = support_stats(harmful_medium, oof["S-052"], MEDIUM, pred_093, pred_094)
    high_stats = support_stats(high_recovery, oof["S-052"], HIGH, pred_093, pred_094)
    high_loss_stats = support_stats(high_loss, oof["S-052"], HIGH, pred_093, pred_094)

    recall_093 = classwise_recalls(y, pred_093)
    recall_094 = classwise_recalls(y, pred_094)
    recall_delta = [b - a for a, b in zip(recall_093, recall_094)]

    delta_cases = Counter()
    for yt, old_pred, new_pred in zip(y[changed], pred_093[changed], pred_094[changed]):
        delta_cases[(CLASS_LABELS[yt], CLASS_LABELS[old_pred], CLASS_LABELS[new_pred])] += 1

    print("=" * 80)
    print("A-015: S-052 attribution on S-094 vs S-093 changed rows")
    print("Method: existing OOF probability artifacts only; no training")
    print(f"Rows: {len(y):,}")
    print(f"Changed rows: {len(changed_idx):,}")
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

    print("\nChanged-Row Outcome Buckets")
    print(f"- Beneficial Medium corrections: {int(beneficial_medium.sum())}")
    print(f"- Harmful Medium flips: {int(harmful_medium.sum())}")
    print(f"- High recoveries: {int(high_recovery.sum())}")
    print(f"- High losses: {int(high_loss.sum())}")

    print("\nS-052 Support for Changed-Row Buckets")
    fmt_support("beneficial Medium corrections", medium_stats)
    fmt_support("harmful Medium flips", medium_harm_stats)
    fmt_support("High recoveries", high_stats)
    fmt_support("High losses", high_loss_stats)

    print("\nLargest Changed-Case Flows")
    for (true_label, old_pred, new_pred), count in delta_cases.most_common(8):
        print(f"- true={true_label}: {old_pred} -> {new_pred}: {count}")

    print("\nDecision Facts")
    print(
        "- S-052 aligns more with beneficial Medium corrections than with High recoveries by argmax: "
        f"{'yes' if medium_stats['argmax_support'] > high_stats['argmax_support'] else 'no'}"
    )
    print(
        "- S-052 target-class probability beats the old prediction more often on beneficial Medium corrections than on High recoveries: "
        f"{'yes' if medium_stats['target_gt_old'] > high_stats['target_gt_old'] else 'no'}"
    )
    print(
        "- S-052 mean target-class margin vs old prediction is larger for beneficial Medium corrections than for High recoveries: "
        f"{'yes' if medium_stats['mean_margin_vs_old'] > high_stats['mean_margin_vs_old'] else 'no'}"
    )
    print(
        "- S-052 gives any direct argmax support to High recoveries: "
        f"{'yes' if high_stats['argmax_support'] > 0 else 'no'}"
    )
    print(
        "- Changed-row evidence favors a Medium-signal explanation over a High-signal explanation: "
        f"{'yes' if (medium_stats['argmax_support'] > high_stats['argmax_support']) and (medium_stats['target_gt_old'] > high_stats['target_gt_old']) and (medium_stats['mean_margin_vs_old'] > high_stats['mean_margin_vs_old']) else 'no'}"
    )


if __name__ == "__main__":
    main()
