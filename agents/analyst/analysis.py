#!/usr/bin/env python3
"""
A-016: Test whether S-102 preserves the practical behavior of S-094.

This script:
- loads existing OOF probability artifacts only
- compares S-094 and S-102 on balanced accuracy and classwise recall
- isolates rows whose argmax prediction changes
- measures whether changed-row differences are mostly Medium reallocations rather
  than new High regressions

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
    "S-094": ARTIFACT_ROOT / "S-094" / "oof-preds.npy",
    "S-102": ARTIFACT_ROOT / "S-102" / "oof-preds.npy",
}

CLASS_TO_IDX = {label: idx for idx, label in enumerate(CLASS_LABELS)}
HIGH = CLASS_TO_IDX["High"]
LOW = CLASS_TO_IDX["Low"]
MEDIUM = CLASS_TO_IDX["Medium"]
BA_TOL = 1e-5


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
    pred_094 = np.argmax(oof["S-094"], axis=1)
    pred_102 = np.argmax(oof["S-102"], axis=1)

    changed = pred_094 != pred_102
    changed_idx = np.flatnonzero(changed)

    recall_094 = classwise_recalls(y, pred_094)
    recall_102 = classwise_recalls(y, pred_102)
    recall_delta = [b - a for a, b in zip(recall_094, recall_102)]

    improved = (pred_094 != y) & (pred_102 == y)
    regressed = (pred_094 == y) & (pred_102 != y)
    changed_wrong = changed & ~improved & ~regressed

    high_recovered = improved & (y == HIGH)
    high_regressed = regressed & (y == HIGH)
    medium_recovered = improved & (y == MEDIUM)
    medium_regressed = regressed & (y == MEDIUM)
    low_recovered = improved & (y == LOW)
    low_regressed = regressed & (y == LOW)

    changed_true_medium = changed & (y == MEDIUM)
    changed_true_high = changed & (y == HIGH)
    changed_true_low = changed & (y == LOW)

    delta_cases = Counter()
    for yt, old_pred, new_pred in zip(y[changed], pred_094[changed], pred_102[changed]):
        delta_cases[(CLASS_LABELS[yt], CLASS_LABELS[old_pred], CLASS_LABELS[new_pred])] += 1

    ba_094 = ba(y, pred_094)
    ba_102 = ba(y, pred_102)
    ba_delta = ba_102 - ba_094

    print("=" * 80)
    print("A-016: S-102 preservation check versus S-094")
    print("Method: existing OOF probability artifacts only; no training")
    print(f"Rows: {len(y):,}")
    print(f"Classes: {CLASS_LABELS}")
    print("=" * 80)

    print("\nArtifacts")
    for name, path in MODEL_PATHS.items():
        print(f"- {name}: {path.relative_to(REPO_ROOT)}")

    print("\nBalanced Accuracy")
    print(f"- S-094: {ba_094:.6f}")
    print(f"- S-102: {ba_102:.6f}")
    print(f"- Delta (S-102 - S-094): {ba_delta:+.6f}")
    print(f"- Within 0.00001 tolerance: {'yes' if abs(ba_delta) <= BA_TOL else 'no'}")

    print("\nClasswise Recall")
    print(f"- S-094: {fmt_recall_triplet(recall_094)}")
    print(f"- S-102: {fmt_recall_triplet(recall_102)}")
    print(f"- Delta: {fmt_recall_triplet(recall_delta)}")
    print(f"- High recall unchanged: {'yes' if recall_delta[HIGH] == 0.0 else 'no'}")

    print("\nChanged Argmax Rows")
    print(f"- Changed rows: {len(changed_idx)} / {len(y)} ({len(changed_idx) / len(y):.6%})")
    print(f"- Wrong -> right: {int(improved.sum())}")
    print(f"- Right -> wrong: {int(regressed.sum())}")
    print(f"- Wrong -> wrong: {int(changed_wrong.sum())}")
    print(
        "- True-label mix among changed rows: "
        + ", ".join(
            f"{label}={int(np.sum(y[changed] == cls))}"
            for cls, label in enumerate(CLASS_LABELS)
        )
    )

    print("\nChanged Rows by True Class")
    print(
        f"- High: total={int(changed_true_high.sum())}, improved={int(high_recovered.sum())}, "
        f"regressed={int(high_regressed.sum())}, net={int(high_recovered.sum()) - int(high_regressed.sum()):+d}"
    )
    print(
        f"- Low: total={int(changed_true_low.sum())}, improved={int(low_recovered.sum())}, "
        f"regressed={int(low_regressed.sum())}, net={int(low_recovered.sum()) - int(low_regressed.sum()):+d}"
    )
    print(
        f"- Medium: total={int(changed_true_medium.sum())}, improved={int(medium_recovered.sum())}, "
        f"regressed={int(medium_regressed.sum())}, net={int(medium_recovered.sum()) - int(medium_regressed.sum()):+d}"
    )

    print("\nLargest Changed-Case Flows")
    for (true_label, old_pred, new_pred), count in delta_cases.most_common(8):
        print(f"- true={true_label}: {old_pred} -> {new_pred}: {count}")

    print("\nDecision Facts")
    print(
        "- Balanced accuracy preserved within threshold: "
        f"{'yes' if abs(ba_delta) <= BA_TOL else 'no'}"
    )
    print(f"- High recall preserved exactly: {'yes' if recall_delta[HIGH] == 0.0 else 'no'}")
    print(
        "- Changed rows are mainly true Medium rows: "
        f"{'yes' if int(changed_true_medium.sum()) > int(changed_true_high.sum()) + int(changed_true_low.sum()) else 'no'}"
    )
    print(
        "- New High regressions exceed zero: "
        f"{'yes' if int(high_regressed.sum()) > 0 else 'no'}"
    )
    print(
        "- Net changed-row effect is larger in Medium than in High: "
        f"{'yes' if abs(int(medium_recovered.sum()) - int(medium_regressed.sum())) > abs(int(high_recovered.sum()) - int(high_regressed.sum())) else 'no'}"
    )
    print(
        "- Practical behavior preserved under the hypothesis criteria: "
        f"{'yes' if abs(ba_delta) <= BA_TOL and recall_delta[HIGH] == 0.0 and int(changed_true_medium.sum()) > int(changed_true_high.sum()) + int(changed_true_low.sum()) and int(high_regressed.sum()) == 0 else 'no'}"
    )


if __name__ == "__main__":
    main()
