#!/usr/bin/env python3
"""
A-013: Test whether S-052 remains a plausible diversity source after S-093.

This script:
- loads existing OOF probability artifacts only
- loads train labels from the fixed dataset contract
- compares S-052 vs S-093 correlation against the S-014/S-082 tree baseline
- checks whether a simple S-093 + S-052 average materially regresses vs S-093

No model training is performed.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
from scipy.stats import pearsonr
from sklearn.metrics import balanced_accuracy_score

from harness.dataset import CLASS_LABELS, load_train_with_folds, split_xy


ARTIFACT_ROOT = REPO_ROOT / "artifacts"
MODEL_PATHS = {
    "S-014": ARTIFACT_ROOT / "S-014" / "oof-preds.npy",
    "S-052": ARTIFACT_ROOT / "S-052" / "oof-preds.npy",
    "S-082": ARTIFACT_ROOT / "S-082" / "oof-preds.npy",
    "S-093": ARTIFACT_ROOT / "S-093" / "oof-preds.npy",
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


def pairwise_correlations(a: np.ndarray, b: np.ndarray) -> list[float]:
    return [pearsonr(a[:, i], b[:, i])[0] for i in range(a.shape[1])]


def argmax_agreement(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.argmax(a, axis=1) == np.argmax(b, axis=1)))


def ba(y: np.ndarray, proba: np.ndarray) -> float:
    return balanced_accuracy_score(y, np.argmax(proba, axis=1))


def fmt_corrs(corrs: list[float]) -> str:
    parts = [f"{label}={corr:.6f}" for label, corr in zip(CLASS_LABELS, corrs)]
    return ", ".join(parts)


def main() -> None:
    y = load_labels()
    oof = load_oof()

    avg_093_052 = (oof["S-093"] + oof["S-052"]) / 2.0
    corrs_014_082 = pairwise_correlations(oof["S-014"], oof["S-082"])
    corrs_093_052 = pairwise_correlations(oof["S-093"], oof["S-052"])

    ba_014 = ba(y, oof["S-014"])
    ba_052 = ba(y, oof["S-052"])
    ba_082 = ba(y, oof["S-082"])
    ba_093 = ba(y, oof["S-093"])
    ba_avg = ba(y, avg_093_052)

    print("=" * 80)
    print("A-013: S-052 diversity check after S-093")
    print("Method: existing OOF probability artifacts only; no training")
    print(f"Rows: {len(y):,}")
    print(f"Classes: {CLASS_LABELS}")
    print("=" * 80)

    print("\nArtifacts")
    for name, path in MODEL_PATHS.items():
        print(f"- {name}: {path.relative_to(REPO_ROOT)}")

    print("\nBalanced Accuracy")
    print(f"- S-014: {ba_014:.6f}")
    print(f"- S-052: {ba_052:.6f}")
    print(f"- S-082: {ba_082:.6f}")
    print(f"- S-093: {ba_093:.6f}")
    print(f"- Simple average S-093 + S-052: {ba_avg:.6f}")
    print(f"- Delta (avg - S-093): {ba_avg - ba_093:+.6f}")

    print("\nPairwise Probability Correlations")
    print(f"- S-014 vs S-082: {fmt_corrs(corrs_014_082)}")
    print(f"- S-093 vs S-052: {fmt_corrs(corrs_093_052)}")

    print("\nPairwise Argmax Agreement")
    print(f"- S-014 vs S-082: {argmax_agreement(oof['S-014'], oof['S-082']):.6f}")
    print(f"- S-093 vs S-052: {argmax_agreement(oof['S-093'], oof['S-052']):.6f}")

    print("\nCorrelation Delta vs S-014/S-082 Baseline")
    for label, tree_corr, stack_lr_corr in zip(CLASS_LABELS, corrs_014_082, corrs_093_052):
        print(f"- {label}: {tree_corr - stack_lr_corr:+.6f}")

    min_tree_corr = min(corrs_014_082)
    min_stack_lr_corr = min(corrs_093_052)

    print("\nDecision Facts")
    print(f"- Minimum classwise correlation for S-014 vs S-082: {min_tree_corr:.6f}")
    print(f"- Minimum classwise correlation for S-093 vs S-052: {min_stack_lr_corr:.6f}")
    print(f"- S-093 vs S-052 less correlated than S-014 vs S-082: {'yes' if min_stack_lr_corr < min_tree_corr else 'no'}")
    print(f"- Simple average S-093 + S-052 regresses vs S-093: {'yes' if ba_avg < ba_093 else 'no'}")


if __name__ == "__main__":
    main()
