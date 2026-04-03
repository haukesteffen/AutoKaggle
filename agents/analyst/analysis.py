#!/usr/bin/env python3
"""
A-010: Do S-045 MLP OOF predictions show meaningfully different High-class
patterns from S-014 XGBoost OOF predictions, suggesting ensemble gains?

Strategy:
- Load existing OOF artifacts (no model training):
    S-045: artifacts/S-045/oof-preds.npy  (N x 3, High=0/Low=1/Medium=2)
    S-014: artifacts/S-014/oof-preds.npy  (N x 3, same class order)
- Load true labels via harness.dataset.load_train_with_folds()
- Compute:
    1. Overall prediction agreement rate (argmax comparison)
    2. High-class disagreement: among true High samples, fraction S-045 correct
       but S-014 misses, and vice versa
    3. Pearson correlation of High-class probabilities between the two models
    4. Simple average ensemble balanced accuracy vs. individual model BAs
- Answer yes/no: do models disagree on High-class in a way that suggests
  ensemble gains?
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import warnings
warnings.filterwarnings('ignore')

from scipy.stats import pearsonr
from sklearn.metrics import balanced_accuracy_score

from harness.dataset import (
    load_train_with_folds,
    split_xy,
    CLASS_LABELS,
)

# CLASS_LABELS = ("High", "Low", "Medium") → 0=High, 1=Low, 2=Medium
HIGH_IDX = 0  # column index for High class in OOF preds

ARTIFACT_ROOT = REPO_ROOT / "artifacts"
S045_OOF_PATH = ARTIFACT_ROOT / "S-045" / "oof-preds.npy"
S014_OOF_PATH = ARTIFACT_ROOT / "S-014" / "oof-preds.npy"


def main():
    print("=" * 80)
    print("A-010: S-045 MLP vs S-014 XGBoost OOF High-class Diversity Analysis")
    print("Method: Load existing OOF artifacts only — no model training")
    print(f"S-045 path: {S045_OOF_PATH}")
    print(f"S-014 path: {S014_OOF_PATH}")
    print("=" * 80)

    # ------------------------------------------------------------------
    # Load artifacts
    # ------------------------------------------------------------------
    oof_045 = np.load(S045_OOF_PATH)  # N x 3
    oof_014 = np.load(S014_OOF_PATH)  # N x 3

    print(f"\nS-045 OOF shape: {oof_045.shape}")
    print(f"S-014 OOF shape: {oof_014.shape}")

    if oof_045.shape != oof_014.shape:
        raise ValueError(
            f"OOF shape mismatch: S-045={oof_045.shape}, S-014={oof_014.shape}"
        )

    n = oof_045.shape[0]

    # ------------------------------------------------------------------
    # Load true labels
    # ------------------------------------------------------------------
    train_df = load_train_with_folds()
    _, y = split_xy(train_df)
    y = y.reset_index(drop=True).to_numpy() if hasattr(y, 'reset_index') else np.asarray(y)

    if len(y) != n:
        raise ValueError(
            f"True label count ({len(y)}) does not match OOF row count ({n})"
        )

    print(f"\nDataset: {n:,} rows")
    print(f"Classes: {CLASS_LABELS} (0=High, 1=Low, 2=Medium)")
    print(f"True High-class count: {(y == HIGH_IDX).sum():,} ({(y == HIGH_IDX).mean()*100:.2f}%)")

    # ------------------------------------------------------------------
    # Argmax predictions
    # ------------------------------------------------------------------
    pred_045 = np.argmax(oof_045, axis=1)
    pred_014 = np.argmax(oof_014, axis=1)

    # ------------------------------------------------------------------
    # 1. Overall prediction agreement
    # ------------------------------------------------------------------
    agreement = np.mean(pred_045 == pred_014)
    disagreement = 1.0 - agreement
    n_disagree = int(disagreement * n)

    print("\n" + "=" * 80)
    print("1. OVERALL PREDICTION AGREEMENT")
    print("=" * 80)
    print(f"\n  Agreement rate:    {agreement:.6f} ({agreement*100:.2f}%)")
    print(f"  Disagreement rate: {disagreement:.6f} ({disagreement*100:.2f}%)")
    print(f"  Disagreeing rows:  {n_disagree:,} of {n:,}")

    # ------------------------------------------------------------------
    # 2. High-class disagreement analysis
    # ------------------------------------------------------------------
    high_mask = (y == HIGH_IDX)
    n_high = high_mask.sum()

    # Among true High samples
    pred_045_high = pred_045[high_mask]
    pred_014_high = pred_014[high_mask]

    # S-045 correct, S-014 wrong (S-045 unique TP)
    s045_correct_014_wrong = (pred_045_high == HIGH_IDX) & (pred_014_high != HIGH_IDX)
    # S-014 correct, S-045 wrong (S-014 unique TP)
    s014_correct_045_wrong = (pred_014_high == HIGH_IDX) & (pred_045_high != HIGH_IDX)
    # Both correct
    both_correct = (pred_045_high == HIGH_IDX) & (pred_014_high == HIGH_IDX)
    # Both wrong
    both_wrong = (pred_045_high != HIGH_IDX) & (pred_014_high != HIGH_IDX)

    n_s045_unique_tp = s045_correct_014_wrong.sum()
    n_s014_unique_tp = s014_correct_045_wrong.sum()
    n_both_correct = both_correct.sum()
    n_both_wrong = both_wrong.sum()

    frac_s045_unique = n_s045_unique_tp / n_high
    frac_s014_unique = n_s014_unique_tp / n_high
    frac_both_correct = n_both_correct / n_high
    frac_both_wrong = n_both_wrong / n_high

    s045_high_recall = (pred_045_high == HIGH_IDX).mean()
    s014_high_recall = (pred_014_high == HIGH_IDX).mean()

    print("\n" + "=" * 80)
    print("2. HIGH-CLASS DISAGREEMENT (among true High-class samples)")
    print("=" * 80)
    print(f"\n  True High-class samples: {n_high:,}")
    print(f"\n  S-045 High recall: {s045_high_recall:.4f} ({int(s045_high_recall*n_high):,}/{n_high:,} correct)")
    print(f"  S-014 High recall: {s014_high_recall:.4f} ({int(s014_high_recall*n_high):,}/{n_high:,} correct)")
    print(f"\n  Disagreement breakdown (among {n_high:,} true High samples):")
    print(f"  {'Category':<45} {'Count':>8} {'Fraction':>10}")
    print(f"  {'-'*65}")
    print(f"  {'Both correct (both TP)':<45} {n_both_correct:>8,} {frac_both_correct:>10.4f}")
    print(f"  {'S-045 correct, S-014 wrong (S-045 unique TP)':<45} {n_s045_unique_tp:>8,} {frac_s045_unique:>10.4f}")
    print(f"  {'S-014 correct, S-045 wrong (S-014 unique TP)':<45} {n_s014_unique_tp:>8,} {frac_s014_unique:>10.4f}")
    print(f"  {'Both wrong (both FN)':<45} {n_both_wrong:>8,} {frac_both_wrong:>10.4f}")
    print(f"  {'TOTAL':<45} {n_high:>8,} {'1.0000':>10}")

    # Where S-045 is wrong but S-014 is right: what does S-045 predict?
    if n_s014_unique_tp > 0:
        s045_wrong_preds = pred_045_high[s014_correct_045_wrong]
        print(f"\n  S-045 wrong predictions on S-014's unique TPs:")
        for cls_idx, cls_name in enumerate(CLASS_LABELS):
            cnt = (s045_wrong_preds == cls_idx).sum()
            if cnt > 0:
                print(f"    S-045 predicted {cls_name}: {cnt:,} ({cnt/n_s014_unique_tp*100:.1f}%)")

    # Where S-014 is wrong but S-045 is right: what does S-014 predict?
    if n_s045_unique_tp > 0:
        s014_wrong_preds = pred_014_high[s045_correct_014_wrong]
        print(f"\n  S-014 wrong predictions on S-045's unique TPs:")
        for cls_idx, cls_name in enumerate(CLASS_LABELS):
            cnt = (s014_wrong_preds == cls_idx).sum()
            if cnt > 0:
                print(f"    S-014 predicted {cls_name}: {cnt:,} ({cnt/n_s045_unique_tp*100:.1f}%)")

    # ------------------------------------------------------------------
    # 3. Pearson correlation of High-class probabilities
    # ------------------------------------------------------------------
    high_proba_045 = oof_045[:, HIGH_IDX]
    high_proba_014 = oof_014[:, HIGH_IDX]

    corr_high, pval_high = pearsonr(high_proba_045, high_proba_014)

    # Also compute for other classes
    low_proba_045 = oof_045[:, 1]
    low_proba_014 = oof_014[:, 1]
    corr_low, _ = pearsonr(low_proba_045, low_proba_014)

    med_proba_045 = oof_045[:, 2]
    med_proba_014 = oof_014[:, 2]
    corr_med, _ = pearsonr(med_proba_045, med_proba_014)

    print("\n" + "=" * 80)
    print("3. OOF PROBABILITY CORRELATION")
    print("=" * 80)
    print(f"\n  {'Class':<12} {'Pearson r':>12} {'p-value':>15}")
    print(f"  {'-'*42}")
    print(f"  {'High (0)':<12} {corr_high:>12.6f} {pval_high:>15.3e}")
    print(f"  {'Low (1)':<12} {corr_low:>12.6f}")
    print(f"  {'Medium (2)':<12} {corr_med:>12.6f}")

    print(f"\n  S-045 High proba: mean={high_proba_045.mean():.6f}, "
          f"std={high_proba_045.std():.6f}, "
          f"min={high_proba_045.min():.6f}, max={high_proba_045.max():.6f}")
    print(f"  S-014 High proba: mean={high_proba_014.mean():.6f}, "
          f"std={high_proba_014.std():.6f}, "
          f"min={high_proba_014.min():.6f}, max={high_proba_014.max():.6f}")

    # Among true High samples specifically
    hp_045_high_samples = high_proba_045[high_mask]
    hp_014_high_samples = high_proba_014[high_mask]
    corr_high_only, _ = pearsonr(hp_045_high_samples, hp_014_high_samples)
    print(f"\n  Among true High samples only:")
    print(f"    S-045 mean High proba: {hp_045_high_samples.mean():.6f}")
    print(f"    S-014 mean High proba: {hp_014_high_samples.mean():.6f}")
    print(f"    Pearson r (High-only samples): {corr_high_only:.6f}")

    # ------------------------------------------------------------------
    # 4. Simple average ensemble balanced accuracy
    # ------------------------------------------------------------------
    oof_avg = (oof_045 + oof_014) / 2.0
    pred_avg = np.argmax(oof_avg, axis=1)

    ba_045 = balanced_accuracy_score(y, pred_045)
    ba_014 = balanced_accuracy_score(y, pred_014)
    ba_avg = balanced_accuracy_score(y, pred_avg)

    print("\n" + "=" * 80)
    print("4. SIMPLE AVERAGE ENSEMBLE BALANCED ACCURACY")
    print("=" * 80)
    print(f"\n  {'Model':<35} {'Balanced Accuracy':>18}")
    print(f"  {'-'*55}")
    print(f"  {'S-045 MLP (standalone)':<35} {ba_045:>18.6f}")
    print(f"  {'S-014 XGBoost (standalone)':<35} {ba_014:>18.6f}")
    print(f"  {'Simple avg ensemble (S-045+S-014)':<35} {ba_avg:>18.6f}")
    print(f"\n  Ensemble lift vs S-045: {ba_avg - ba_045:+.6f}")
    print(f"  Ensemble lift vs S-014: {ba_avg - ba_014:+.6f}")
    print(f"  Ensemble lift vs best:  {ba_avg - max(ba_045, ba_014):+.6f}")

    # High-class recall for ensemble
    ensemble_high_recall = (pred_avg[high_mask] == HIGH_IDX).mean()
    print(f"\n  Ensemble High-class recall: {ensemble_high_recall:.4f}")
    print(f"  S-045 High-class recall:    {s045_high_recall:.4f}")
    print(f"  S-014 High-class recall:    {s014_high_recall:.4f}")

    # ------------------------------------------------------------------
    # Summary and verdict
    # ------------------------------------------------------------------
    DIVERSITY_THRESHOLD = 0.97
    has_complementary_high = min(n_s045_unique_tp, n_s014_unique_tp) > 0
    high_frac_complementary = (n_s045_unique_tp + n_s014_unique_tp) / n_high
    has_low_corr = corr_high < DIVERSITY_THRESHOLD
    ensemble_lifts = ba_avg - max(ba_045, ba_014)

    print("\n" + "=" * 80)
    print("SUMMARY AND VERDICT")
    print("=" * 80)
    print(f"\n  Agreement rate (all classes):    {agreement*100:.2f}%")
    print(f"  High-class proba Pearson r:      {corr_high:.6f} (threshold < {DIVERSITY_THRESHOLD})")
    print(f"  High-class complementary TPs:    {n_s045_unique_tp + n_s014_unique_tp:,} "
          f"({high_frac_complementary*100:.2f}% of true High)")
    print(f"  S-045-only unique TPs:           {n_s045_unique_tp:,} ({frac_s045_unique*100:.2f}%)")
    print(f"  S-014-only unique TPs:           {n_s014_unique_tp:,} ({frac_s014_unique*100:.2f}%)")
    print(f"  Avg ensemble vs best model lift: {ensemble_lifts:+.6f}")
    print(f"\n  Correlation below diversity threshold ({DIVERSITY_THRESHOLD}): {has_low_corr}")
    print(f"  Meaningful complementary High-class TPs: {has_complementary_high}")

    if has_low_corr and has_complementary_high and ensemble_lifts >= 0:
        verdict = "YES — S-045 and S-014 disagree on High-class in a way that suggests ensemble gains."
    elif has_low_corr and ensemble_lifts >= 0:
        verdict = "YES (partial) — Low correlation supports ensemble, but High-class complementarity is weak."
    elif not has_low_corr:
        verdict = "NO — High-class probability correlation is above diversity threshold."
    else:
        verdict = "NO — Correlation is low but ensemble does not lift above best single model."

    print(f"\n  VERDICT: {verdict}")

    print("\n" + "=" * 80)
    print("END OF ANALYSIS")
    print("=" * 80)


if __name__ == "__main__":
    main()
