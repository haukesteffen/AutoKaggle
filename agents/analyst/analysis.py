#!/usr/bin/env python3
"""
A-011: Do S-052 LR OOF predictions (CV=0.9286) show meaningfully different
High-class prediction patterns from S-014 XGBoost OOF predictions (CV=0.9709)?
Specifically: does S-052 recover a meaningful fraction of High-class TPs that
S-014 misses, suggesting ensemble value?

Strategy:
- Load existing OOF artifacts (no model training):
    S-052: artifacts/S-052/oof-preds.npy  (N x 3, High=0/Low=1/Medium=2)
    S-014: artifacts/S-014/oof-preds.npy  (N x 3, same class order)
- Load true labels via harness.dataset.load_train_with_folds()
- Compute (same methodology as A-010):
    1. Overall prediction agreement rate (argmax comparison)
    2. High-class disagreement: among true High samples, fraction S-052 correct
       but S-014 misses, and vice versa
    3. Pearson correlation of High-class probabilities between the two models
    4. Simple average ensemble balanced accuracy vs. individual model BAs
- Answer yes/no: does S-052 LR recover a meaningful number of unique High TPs vs S-014?
- Context: compare against A-010 (S-045 MLP had 98.8% agreement, 104 unique High TPs)
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
S052_OOF_PATH = ARTIFACT_ROOT / "S-052" / "oof-preds.npy"
S014_OOF_PATH = ARTIFACT_ROOT / "S-014" / "oof-preds.npy"


def main():
    print("=" * 80)
    print("A-011: S-052 LR vs S-014 XGBoost OOF High-class Diversity Analysis")
    print("Method: Load existing OOF artifacts only — no model training")
    print(f"S-052 path: {S052_OOF_PATH}")
    print(f"S-014 path: {S014_OOF_PATH}")
    print("=" * 80)

    # ------------------------------------------------------------------
    # Load artifacts
    # ------------------------------------------------------------------
    oof_052 = np.load(S052_OOF_PATH)  # N x 3
    oof_014 = np.load(S014_OOF_PATH)  # N x 3

    print(f"\nS-052 OOF shape: {oof_052.shape}")
    print(f"S-014 OOF shape: {oof_014.shape}")

    if oof_052.shape != oof_014.shape:
        raise ValueError(
            f"OOF shape mismatch: S-052={oof_052.shape}, S-014={oof_014.shape}"
        )

    n = oof_052.shape[0]

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
    pred_052 = np.argmax(oof_052, axis=1)
    pred_014 = np.argmax(oof_014, axis=1)

    # ------------------------------------------------------------------
    # 1. Overall prediction agreement
    # ------------------------------------------------------------------
    agreement = np.mean(pred_052 == pred_014)
    disagreement = 1.0 - agreement
    n_disagree = int(disagreement * n)

    print("\n" + "=" * 80)
    print("1. OVERALL PREDICTION AGREEMENT")
    print("=" * 80)
    print(f"\n  Agreement rate:    {agreement:.6f} ({agreement*100:.2f}%)")
    print(f"  Disagreement rate: {disagreement:.6f} ({disagreement*100:.2f}%)")
    print(f"  Disagreeing rows:  {n_disagree:,} of {n:,}")
    print(f"\n  Context (A-010): S-045 MLP had 98.80% agreement with S-014")
    print(f"  S-052 LR agreement: {agreement*100:.2f}%  "
          f"({'more' if agreement < 0.9880 else 'less'} diverse than S-045 MLP)")

    # ------------------------------------------------------------------
    # 2. High-class disagreement analysis
    # ------------------------------------------------------------------
    high_mask = (y == HIGH_IDX)
    n_high = high_mask.sum()

    # Among true High samples
    pred_052_high = pred_052[high_mask]
    pred_014_high = pred_014[high_mask]

    # S-052 correct, S-014 wrong (S-052 unique TP)
    s052_correct_014_wrong = (pred_052_high == HIGH_IDX) & (pred_014_high != HIGH_IDX)
    # S-014 correct, S-052 wrong (S-014 unique TP)
    s014_correct_052_wrong = (pred_014_high == HIGH_IDX) & (pred_052_high != HIGH_IDX)
    # Both correct
    both_correct = (pred_052_high == HIGH_IDX) & (pred_014_high == HIGH_IDX)
    # Both wrong
    both_wrong = (pred_052_high != HIGH_IDX) & (pred_014_high != HIGH_IDX)

    n_s052_unique_tp = s052_correct_014_wrong.sum()
    n_s014_unique_tp = s014_correct_052_wrong.sum()
    n_both_correct = both_correct.sum()
    n_both_wrong = both_wrong.sum()

    frac_s052_unique = n_s052_unique_tp / n_high
    frac_s014_unique = n_s014_unique_tp / n_high
    frac_both_correct = n_both_correct / n_high
    frac_both_wrong = n_both_wrong / n_high

    s052_high_recall = (pred_052_high == HIGH_IDX).mean()
    s014_high_recall = (pred_014_high == HIGH_IDX).mean()

    print("\n" + "=" * 80)
    print("2. HIGH-CLASS DISAGREEMENT (among true High-class samples)")
    print("=" * 80)
    print(f"\n  True High-class samples: {n_high:,}")
    print(f"\n  S-052 High recall: {s052_high_recall:.4f} ({int(s052_high_recall*n_high):,}/{n_high:,} correct)")
    print(f"  S-014 High recall: {s014_high_recall:.4f} ({int(s014_high_recall*n_high):,}/{n_high:,} correct)")
    print(f"\n  Disagreement breakdown (among {n_high:,} true High samples):")
    print(f"  {'Category':<45} {'Count':>8} {'Fraction':>10}")
    print(f"  {'-'*65}")
    print(f"  {'Both correct (both TP)':<45} {n_both_correct:>8,} {frac_both_correct:>10.4f}")
    print(f"  {'S-052 correct, S-014 wrong (S-052 unique TP)':<45} {n_s052_unique_tp:>8,} {frac_s052_unique:>10.4f}")
    print(f"  {'S-014 correct, S-052 wrong (S-014 unique TP)':<45} {n_s014_unique_tp:>8,} {frac_s014_unique:>10.4f}")
    print(f"  {'Both wrong (both FN)':<45} {n_both_wrong:>8,} {frac_both_wrong:>10.4f}")
    print(f"  {'TOTAL':<45} {n_high:>8,} {'1.0000':>10}")

    # Context vs A-010 (S-045 MLP)
    print(f"\n  Context (A-010): S-045 MLP had 104 unique TPs vs S-014's 353 unique TPs")
    print(f"  S-052 LR unique TPs: {n_s052_unique_tp:,} (S-014's unique TPs: {n_s014_unique_tp:,})")

    # Where S-052 is wrong but S-014 is right: what does S-052 predict?
    if n_s014_unique_tp > 0:
        s052_wrong_preds = pred_052_high[s014_correct_052_wrong]
        print(f"\n  S-052 wrong predictions on S-014's unique TPs:")
        for cls_idx, cls_name in enumerate(CLASS_LABELS):
            cnt = (s052_wrong_preds == cls_idx).sum()
            if cnt > 0:
                print(f"    S-052 predicted {cls_name}: {cnt:,} ({cnt/n_s014_unique_tp*100:.1f}%)")

    # Where S-014 is wrong but S-052 is right: what does S-014 predict?
    if n_s052_unique_tp > 0:
        s014_wrong_preds = pred_014_high[s052_correct_014_wrong]
        print(f"\n  S-014 wrong predictions on S-052's unique TPs:")
        for cls_idx, cls_name in enumerate(CLASS_LABELS):
            cnt = (s014_wrong_preds == cls_idx).sum()
            if cnt > 0:
                print(f"    S-014 predicted {cls_name}: {cnt:,} ({cnt/n_s052_unique_tp*100:.1f}%)")

    # ------------------------------------------------------------------
    # 3. Pearson correlation of High-class probabilities
    # ------------------------------------------------------------------
    high_proba_052 = oof_052[:, HIGH_IDX]
    high_proba_014 = oof_014[:, HIGH_IDX]

    corr_high, pval_high = pearsonr(high_proba_052, high_proba_014)

    # Also compute for other classes
    low_proba_052 = oof_052[:, 1]
    low_proba_014 = oof_014[:, 1]
    corr_low, _ = pearsonr(low_proba_052, low_proba_014)

    med_proba_052 = oof_052[:, 2]
    med_proba_014 = oof_014[:, 2]
    corr_med, _ = pearsonr(med_proba_052, med_proba_014)

    print("\n" + "=" * 80)
    print("3. OOF PROBABILITY CORRELATION")
    print("=" * 80)
    print(f"\n  {'Class':<12} {'Pearson r':>12} {'p-value':>15}")
    print(f"  {'-'*42}")
    print(f"  {'High (0)':<12} {corr_high:>12.6f} {pval_high:>15.3e}")
    print(f"  {'Low (1)':<12} {corr_low:>12.6f}")
    print(f"  {'Medium (2)':<12} {corr_med:>12.6f}")

    print(f"\n  S-052 High proba: mean={high_proba_052.mean():.6f}, "
          f"std={high_proba_052.std():.6f}, "
          f"min={high_proba_052.min():.6f}, max={high_proba_052.max():.6f}")
    print(f"  S-014 High proba: mean={high_proba_014.mean():.6f}, "
          f"std={high_proba_014.std():.6f}, "
          f"min={high_proba_014.min():.6f}, max={high_proba_014.max():.6f}")

    # Among true High samples specifically
    hp_052_high_samples = high_proba_052[high_mask]
    hp_014_high_samples = high_proba_014[high_mask]
    corr_high_only, _ = pearsonr(hp_052_high_samples, hp_014_high_samples)
    print(f"\n  Among true High samples only:")
    print(f"    S-052 mean High proba: {hp_052_high_samples.mean():.6f}")
    print(f"    S-014 mean High proba: {hp_014_high_samples.mean():.6f}")
    print(f"    Pearson r (High-only samples): {corr_high_only:.6f}")

    print(f"\n  Context (A-010): S-045 MLP had High proba Pearson r = 0.961 vs S-014")
    print(f"  S-052 LR High proba Pearson r: {corr_high:.6f} "
          f"({'more' if corr_high < 0.961 else 'less'} diverse than S-045 MLP)")

    # ------------------------------------------------------------------
    # 4. Simple average ensemble balanced accuracy
    # ------------------------------------------------------------------
    oof_avg = (oof_052 + oof_014) / 2.0
    pred_avg = np.argmax(oof_avg, axis=1)

    ba_052 = balanced_accuracy_score(y, pred_052)
    ba_014 = balanced_accuracy_score(y, pred_014)
    ba_avg = balanced_accuracy_score(y, pred_avg)

    print("\n" + "=" * 80)
    print("4. SIMPLE AVERAGE ENSEMBLE BALANCED ACCURACY")
    print("=" * 80)
    print(f"\n  {'Model':<35} {'Balanced Accuracy':>18}")
    print(f"  {'-'*55}")
    print(f"  {'S-052 LR (standalone)':<35} {ba_052:>18.6f}")
    print(f"  {'S-014 XGBoost (standalone)':<35} {ba_014:>18.6f}")
    print(f"  {'Simple avg ensemble (S-052+S-014)':<35} {ba_avg:>18.6f}")
    print(f"\n  Ensemble lift vs S-052: {ba_avg - ba_052:+.6f}")
    print(f"  Ensemble lift vs S-014: {ba_avg - ba_014:+.6f}")
    print(f"  Ensemble lift vs best:  {ba_avg - max(ba_052, ba_014):+.6f}")

    # High-class recall for ensemble
    ensemble_high_recall = (pred_avg[high_mask] == HIGH_IDX).mean()
    print(f"\n  Ensemble High-class recall: {ensemble_high_recall:.4f}")
    print(f"  S-052 High-class recall:    {s052_high_recall:.4f}")
    print(f"  S-014 High-class recall:    {s014_high_recall:.4f}")

    print(f"\n  Context (A-010): S-045 MLP ensemble had lift vs S-014: -0.003000 (negative)")

    # ------------------------------------------------------------------
    # Summary and verdict
    # ------------------------------------------------------------------
    DIVERSITY_THRESHOLD = 0.97
    has_complementary_high = n_s052_unique_tp > 0
    high_frac_complementary = (n_s052_unique_tp + n_s014_unique_tp) / n_high
    has_low_corr = corr_high < DIVERSITY_THRESHOLD
    ensemble_lift = ba_avg - max(ba_052, ba_014)

    # Meaningful threshold: > 104 (S-045 baseline) = meaningfully more unique TPs
    s045_baseline_unique_tps = 104
    more_unique_than_mlp = n_s052_unique_tp > s045_baseline_unique_tps

    print("\n" + "=" * 80)
    print("SUMMARY AND VERDICT")
    print("=" * 80)
    print(f"\n  Agreement rate (all classes):    {agreement*100:.2f}%")
    print(f"    vs S-045 MLP baseline:          98.80%")
    print(f"  High-class proba Pearson r:      {corr_high:.6f} (threshold < {DIVERSITY_THRESHOLD})")
    print(f"    vs S-045 MLP baseline:          0.961000")
    print(f"  S-052 unique High TPs:           {n_s052_unique_tp:,}")
    print(f"    vs S-045 MLP baseline:          104")
    print(f"  S-014 unique High TPs:           {n_s014_unique_tp:,}")
    print(f"    vs S-045 MLP baseline:          353")
    print(f"  Avg ensemble vs best model lift: {ensemble_lift:+.6f}")
    print(f"    vs S-045 MLP baseline:          -0.003000")
    print(f"\n  Correlation below diversity threshold ({DIVERSITY_THRESHOLD}): {has_low_corr}")
    print(f"  Meaningful complementary High-class TPs: {has_complementary_high}")
    print(f"  More unique TPs than S-045 MLP ({s045_baseline_unique_tps}): {more_unique_than_mlp}")

    if has_low_corr and more_unique_than_mlp and ensemble_lift >= 0:
        verdict = ("YES — S-052 LR recovers more unique High TPs than S-045 MLP, "
                   "low correlation, and ensemble lifts above best single model.")
    elif has_low_corr and more_unique_than_mlp and ensemble_lift < 0:
        verdict = ("PARTIAL YES — S-052 LR recovers more unique High TPs than S-045 MLP "
                   "and has lower correlation with S-014, but simple average ensemble "
                   "does not lift above best. Weighted blend or threshold optimization needed.")
    elif has_low_corr and not more_unique_than_mlp:
        verdict = ("NO — S-052 LR has lower correlation than MLP but does NOT recover "
                   "more unique High TPs than S-045 MLP baseline (104). Not meaningfully more diverse.")
    elif not has_low_corr:
        verdict = "NO — High-class probability correlation is above diversity threshold."
    else:
        verdict = "NO — Insufficient complementary High-class TPs and no ensemble lift."

    print(f"\n  VERDICT: {verdict}")

    print("\n" + "=" * 80)
    print("END OF ANALYSIS")
    print("=" * 80)


if __name__ == "__main__":
    main()
