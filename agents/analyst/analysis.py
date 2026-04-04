#!/usr/bin/env python3
"""
A-012: Assess whether S-073 MLP OOF probabilities add complementary signal
relative to S-014 XGBoost and S-082 LightGBM, and whether a simple 3-way
average avoids meaningful regression versus the current S-083 weighted blend.

This script:
- loads existing OOF probability artifacts only
- loads train labels from the fixed dataset contract
- computes pairwise class-probability correlations and argmax agreement
- compares balanced accuracy for each model and simple ensembles

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
    "S-073": ARTIFACT_ROOT / "S-073" / "oof-preds.npy",
    "S-082": ARTIFACT_ROOT / "S-082" / "oof-preds.npy",
    "S-083": ARTIFACT_ROOT / "S-083" / "oof-preds.npy",
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

    n_rows = len(y)
    print("=" * 80)
    print("A-012: S-073 complementarity vs S-014 XGBoost and S-082 LightGBM")
    print("Method: existing OOF probability artifacts only; no training")
    print(f"Rows: {n_rows:,}")
    print(f"Classes: {CLASS_LABELS}")
    print("=" * 80)

    print("\nArtifacts")
    for name, path in MODEL_PATHS.items():
        print(f"- {name}: {path.relative_to(REPO_ROOT)}")

    print("\nBalanced Accuracy")
    for name in ("S-014", "S-073", "S-082", "S-083"):
        print(f"- {name}: {ba(y, oof[name]):.6f}")

    pairs = [
        ("S-014", "S-082"),
        ("S-073", "S-014"),
        ("S-073", "S-082"),
    ]

    print("\nPairwise Probability Correlations")
    pair_results: dict[tuple[str, str], list[float]] = {}
    for left, right in pairs:
        corrs = pairwise_correlations(oof[left], oof[right])
        pair_results[(left, right)] = corrs
        print(f"- {left} vs {right}: {fmt_corrs(corrs)}")

    print("\nPairwise Argmax Agreement")
    for left, right in pairs:
        agreement = argmax_agreement(oof[left], oof[right])
        print(f"- {left} vs {right}: {agreement:.6f}")

    baseline_corrs = pair_results[("S-014", "S-082")]
    for comp_pair in [("S-073", "S-014"), ("S-073", "S-082")]:
        corrs = pair_results[comp_pair]
        diffs = [baseline - current for baseline, current in zip(baseline_corrs, corrs)]
        print(f"\nCorrelation Delta vs S-014/S-082 Baseline for {comp_pair[0]} vs {comp_pair[1]}")
        for label, diff in zip(CLASS_LABELS, diffs):
            print(f"- {label}: {diff:+.6f}")

    avg_014_082 = (oof["S-014"] + oof["S-082"]) / 2.0
    avg_014_082_073 = (oof["S-014"] + oof["S-082"] + oof["S-073"]) / 3.0

    ba_014_082 = ba(y, avg_014_082)
    ba_014_082_073 = ba(y, avg_014_082_073)
    ba_083 = ba(y, oof["S-083"])

    print("\nEnsemble Checks")
    print(f"- Simple average S-014 + S-082: {ba_014_082:.6f}")
    print(f"- Simple average S-014 + S-082 + S-073: {ba_014_082_073:.6f}")
    print(f"- Current S-083 weighted blend: {ba_083:.6f}")
    print(f"- Delta (3-way avg - S-083): {ba_014_082_073 - ba_083:+.6f}")
    print(f"- Delta (3-way avg - 2-way avg): {ba_014_082_073 - ba_014_082:+.6f}")

    print("\nDecision Facts")
    min_pair_073 = min(
        min(pair_results[("S-073", "S-014")]),
        min(pair_results[("S-073", "S-082")]),
    )
    min_pair_014_082 = min(pair_results[("S-014", "S-082")])
    print(f"- Minimum classwise correlation for S-014 vs S-082: {min_pair_014_082:.6f}")
    print(f"- Minimum classwise correlation involving S-073: {min_pair_073:.6f}")
    print(
        f"- 3-way average regresses vs S-083: "
        f"{'yes' if ba_014_082_073 < ba_083 else 'no'}"
    )


if __name__ == "__main__":
    main()
