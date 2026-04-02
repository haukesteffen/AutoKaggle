#!/usr/bin/env python3
"""
A-007: Do the three A-006 candidate threshold indicators — I(Temperature<25),
I(SM>=35), and I(SM>=25 AND Temperature<33) — have sufficient selectivity
(High-class enrichment above the 3.3% baseline) within the out-of-subgroup zone
to justify adding them to the S-035 feature set in a logistic regression?

Strategy:
- Load S-032 OOF predictions and training data
- For each candidate indicator zone, compute:
  1. Total High-class prevalence vs baseline (3.3%)
  2. High-class sample count vs total samples in zone
  3. FN rate within zone (from S-032 OOF)
  4. Whether indicator is selective (enrichment above baseline)
- Also check: I(Temp<25 AND SM>=35) combined indicator
- All computations are WITHIN the out-of-subgroup zone (SM>=20 OR Rainfall>=1000)
  as well as globally (full dataset), to correctly assess indicator selectivity
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

from harness.dataset import (
    load_train_with_folds, split_xy,
    CLASS_LABELS, TARGET_COLUMN, FOLD_COLUMN,
    class_probabilities_to_indices,
)

OOF_PATH = REPO_ROOT / "artifacts" / "S-032" / "oof-preds.npy"

# CLASS_LABELS = ("High", "Low", "Medium") → 0=High, 1=Low, 2=Medium
HIGH_IDX = 0
LOW_IDX = 1
MED_IDX = 2


def pct(num, denom):
    return 100.0 * num / denom if denom > 0 else 0.0


def enrich_ratio(prev, baseline):
    return prev / baseline if baseline > 0 else float('nan')


def indicator_stats(name, zone_mask, all_high_mask, oof_preds_argmax, y, baseline_pct, label=""):
    """Compute prevalence, FN rate, and enrichment for an indicator zone."""
    n_zone = int(zone_mask.sum())
    n_zone_high = int((zone_mask & all_high_mask).sum())
    # FNs: High-class in zone, predicted as not-High by S-032
    n_zone_fn = int((zone_mask & all_high_mask & (oof_preds_argmax != HIGH_IDX)).sum())
    n_zone_tp = int((zone_mask & all_high_mask & (oof_preds_argmax == HIGH_IDX)).sum())

    prev_pct = pct(n_zone_high, n_zone)
    fn_rate = pct(n_zone_fn, n_zone_fn + n_zone_tp) if (n_zone_fn + n_zone_tp) > 0 else float('nan')
    enrichment = prev_pct / baseline_pct if baseline_pct > 0 else float('nan')

    return {
        'name': name,
        'label': label,
        'n_zone': n_zone,
        'n_high': n_zone_high,
        'prev_pct': prev_pct,
        'enrichment': enrichment,
        'n_fn': n_zone_fn,
        'n_tp': n_zone_tp,
        'fn_rate': fn_rate,
    }


def print_stats_table(rows, title, baseline_pct):
    print(f"\n{title}")
    print("-" * 110)
    print(f"  {'Indicator':<35} {'n_zone':>9} {'n_High':>8} {'High%':>7} {'Enrichment':>11} {'n_FN':>6} {'n_TP':>6} {'FN rate':>8}")
    print(f"  {'Baseline (3.3%)':<35} {'':>9} {'':>8} {baseline_pct:>6.2f}% {'1.00×':>11}")
    print("-" * 110)
    for r in rows:
        enrichment_str = f"{r['enrichment']:.2f}×" if not np.isnan(r['enrichment']) else "N/A"
        fn_rate_str = f"{r['fn_rate']:.1f}%" if not np.isnan(r['fn_rate']) else "N/A"
        print(f"  {r['name']:<35} {r['n_zone']:>9} {r['n_high']:>8} {r['prev_pct']:>6.2f}% {enrichment_str:>11} "
              f"{r['n_fn']:>6} {r['n_tp']:>6} {fn_rate_str:>8}")
    print("-" * 110)


def main():
    print("=" * 80)
    print("A-007: Selectivity of candidate threshold indicators for S-035 LR feature set")
    print("=" * 80)

    # -----------------------------------------------------------------------
    # Load data and OOF predictions
    # -----------------------------------------------------------------------
    train_df = load_train_with_folds()
    raw_X, y = split_xy(train_df)

    oof_preds = np.load(OOF_PATH)
    assert oof_preds.shape == (len(train_df), 3), \
        f"Unexpected OOF shape: {oof_preds.shape}"

    y_pred = class_probabilities_to_indices(oof_preds)

    sm = raw_X["Soil_Moisture"].values
    rainfall = raw_X["Rainfall_mm"].values
    temp = raw_X["Temperature_C"].values

    n_total = len(y)
    n_total_high = int((y == HIGH_IDX).sum())
    baseline_pct = pct(n_total_high, n_total)  # ~3.3%

    print(f"\nDataset: {n_total} rows, {n_total_high} High-class ({baseline_pct:.2f}% baseline)")

    # -----------------------------------------------------------------------
    # Define zones
    # -----------------------------------------------------------------------
    in_subgroup = (sm < 20) & (rainfall < 1000)
    out_subgroup = ~in_subgroup   # out-of-subgroup: SM>=20 OR Rainfall>=1000

    n_out_subgroup = int(out_subgroup.sum())
    n_out_high = int((out_subgroup & (y == HIGH_IDX)).sum())
    out_baseline_pct = pct(n_out_high, n_out_subgroup)
    print(f"Out-of-subgroup zone: {n_out_subgroup} rows, {n_out_high} High-class ({out_baseline_pct:.2f}% baseline in zone)")
    print(f"Full dataset baseline: {baseline_pct:.2f}%")

    all_high_mask = (y == HIGH_IDX)

    # -----------------------------------------------------------------------
    # SECTION 1: Indicator selectivity on FULL dataset
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("SECTION 1: INDICATOR SELECTIVITY — FULL DATASET")
    print("=" * 80)

    # The three candidate indicators from AK-024
    indicator_masks_full = [
        ("I(Temp<25)",             temp < 25),
        ("I(SM>=35)",              sm >= 35),
        ("I(SM>=25 AND Temp<33)",  (sm >= 25) & (temp < 33)),
        ("I(Temp<25 AND SM>=35)",  (temp < 25) & (sm >= 35)),   # bonus combined
    ]

    rows_full = []
    for name, mask in indicator_masks_full:
        r = indicator_stats(name, mask, all_high_mask, y_pred, y, baseline_pct)
        rows_full.append(r)

    print_stats_table(rows_full, "Indicator selectivity on full dataset", baseline_pct)

    # -----------------------------------------------------------------------
    # SECTION 2: Indicator selectivity WITHIN OUT-OF-SUBGROUP zone only
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("SECTION 2: INDICATOR SELECTIVITY — OUT-OF-SUBGROUP ZONE ONLY")
    print("(restricted to rows where SM>=20 OR Rainfall>=1000)")
    print("=" * 80)

    indicator_masks_out = [
        ("I(Temp<25) in OOS",             out_subgroup & (temp < 25)),
        ("I(SM>=35) in OOS",              out_subgroup & (sm >= 35)),
        ("I(SM>=25&Temp<33) in OOS",      out_subgroup & (sm >= 25) & (temp < 33)),
        ("I(Temp<25&SM>=35) in OOS",      out_subgroup & (temp < 25) & (sm >= 35)),
    ]

    rows_out = []
    for name, mask in indicator_masks_out:
        r = indicator_stats(name, mask, all_high_mask, y_pred, y, baseline_pct)
        rows_out.append(r)

    print_stats_table(rows_out, "Indicator selectivity within out-of-subgroup zone", baseline_pct)

    # -----------------------------------------------------------------------
    # SECTION 3: Prevalence comparison — IN indicator vs NOT in indicator
    #            (within out-of-subgroup zone) — key enrichment signal
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("SECTION 3: IN-INDICATOR vs NOT-IN-INDICATOR PREVALENCE")
    print("(within out-of-subgroup zone; compares High% in zone vs complement)")
    print("=" * 80)

    candidate_names = [
        "I(Temp<25)",
        "I(SM>=35)",
        "I(SM>=25 AND Temp<33)",
        "I(Temp<25 AND SM>=35)",
    ]
    candidate_masks_raw = [
        temp < 25,
        sm >= 35,
        (sm >= 25) & (temp < 33),
        (temp < 25) & (sm >= 35),
    ]

    print(f"\n  {'Indicator':<35} {'In-zone':>10} {'High% IN':>10} {'High% OUT':>11} {'Enrichment IN':>14} {'Signal useful?':>15}")
    print(f"  {'':35} {'n_rows':>10}")
    print(f"  " + "-" * 100)

    for name, raw_mask in zip(candidate_names, candidate_masks_raw):
        # IN indicator & out-of-subgroup
        in_ind_oos = out_subgroup & raw_mask
        # NOT in indicator & out-of-subgroup
        not_in_ind_oos = out_subgroup & ~raw_mask

        n_in = int(in_ind_oos.sum())
        n_in_high = int((in_ind_oos & all_high_mask).sum())
        n_out_ind = int(not_in_ind_oos.sum())
        n_out_ind_high = int((not_in_ind_oos & all_high_mask).sum())

        prev_in = pct(n_in_high, n_in)
        prev_out_ind = pct(n_out_ind_high, n_out_ind)
        enrichment = prev_in / baseline_pct if baseline_pct > 0 else float('nan')

        # For LR: signal is useful if prev_in > baseline AND there's contrast with complement
        # Also useful if prev_in < baseline (negative signal — indicators of LOW prevalence also help)
        if prev_in > baseline_pct * 1.1:
            signal = "YES (enriched)"
        elif prev_in < baseline_pct * 0.9:
            signal = "YES (depleted)"
        else:
            signal = "NO (near baseline)"

        print(f"  {name:<35} {n_in:>10} {prev_in:>9.3f}% {prev_out_ind:>10.3f}% {enrichment:>13.2f}× {signal:>15}")

    # -----------------------------------------------------------------------
    # SECTION 4: Detailed per-indicator FN breakdown
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("SECTION 4: PER-INDICATOR FN/TP BREAKDOWN (S-032 OOF)")
    print("=" * 80)

    out_high_mask = out_subgroup & all_high_mask
    total_out_fn = int((out_high_mask & (y_pred != HIGH_IDX)).sum())

    print(f"\n  Total out-of-subgroup High-class FNs (S-032): {total_out_fn}")
    print(f"  Total out-of-subgroup High-class TPs (S-032): {int((out_high_mask & (y_pred == HIGH_IDX)).sum())}")
    print()

    for name, raw_mask in zip(candidate_names, candidate_masks_raw):
        # Within out-of-subgroup
        zone_mask = out_subgroup & raw_mask
        n_zone = int(zone_mask.sum())
        n_zone_high = int((zone_mask & all_high_mask).sum())
        n_zone_fn = int((zone_mask & all_high_mask & (y_pred != HIGH_IDX)).sum())
        n_zone_tp = int((zone_mask & all_high_mask & (y_pred == HIGH_IDX)).sum())
        prev = pct(n_zone_high, n_zone)
        fn_rate = pct(n_zone_fn, n_zone_fn + n_zone_tp) if (n_zone_fn + n_zone_tp) > 0 else 0.0
        fn_capture = pct(n_zone_fn, total_out_fn)
        enrichment = prev / baseline_pct

        print(f"  Indicator: {name}")
        print(f"    Zone size (out-of-subgroup): {n_zone:>8} rows ({pct(n_zone, n_out_subgroup):.1f}% of out-of-subgroup)")
        print(f"    High-class in zone:          {n_zone_high:>8} ({prev:.3f}% prevalence)")
        print(f"    Enrichment vs 3.3% baseline: {enrichment:.2f}×")
        print(f"    FNs in zone (S-032):         {n_zone_fn:>8} ({fn_capture:.1f}% of all out-subgroup FNs)")
        print(f"    TPs in zone (S-032):         {n_zone_tp:>8}")
        print(f"    FN rate in zone:             {fn_rate:.1f}%")
        print(f"    Net info for LR: prev {'ABOVE' if prev > baseline_pct else 'BELOW/AT'} baseline "
              f"({'enriched' if prev > baseline_pct else 'depleted'}) → "
              f"{'useful indicator' if abs(prev - baseline_pct) / baseline_pct > 0.1 else 'weak signal'}")
        print()

    # -----------------------------------------------------------------------
    # SECTION 5: Summary verdict table
    # -----------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("SECTION 5: VERDICT SUMMARY TABLE")
    print("=" * 80)
    print(f"\n  Baseline High%: {baseline_pct:.2f}%")
    print(f"  Out-of-subgroup baseline High%: {out_baseline_pct:.2f}%")
    print()
    print(f"  {'Indicator':<35} {'High% in zone':>14} {'Enrichment':>11} {'FN rate':>9} {'Justify adding?':>16}")
    print("  " + "-" * 90)

    for name, raw_mask in zip(candidate_names, candidate_masks_raw):
        zone_mask = out_subgroup & raw_mask
        n_zone = int(zone_mask.sum())
        n_zone_high = int((zone_mask & all_high_mask).sum())
        n_zone_fn = int((zone_mask & all_high_mask & (y_pred != HIGH_IDX)).sum())
        n_zone_tp = int((zone_mask & all_high_mask & (y_pred == HIGH_IDX)).sum())
        prev = pct(n_zone_high, n_zone)
        fn_rate = pct(n_zone_fn, n_zone_fn + n_zone_tp) if (n_zone_fn + n_zone_tp) > 0 else 0.0
        enrichment = prev / baseline_pct

        # Justify: enrichment must be meaningfully above 1.0 AND zone is large enough
        if enrichment > 1.5 and n_zone_high >= 50:
            justify = "YES"
        elif enrichment < 0.7:
            justify = "MAYBE (depleted)"
        else:
            justify = "NO"

        print(f"  {name:<35} {prev:>13.3f}% {enrichment:>10.2f}× {fn_rate:>8.1f}% {justify:>16}")

    print()
    print(f"  NOTE: 'FN rate' is not the same as selectivity. An indicator can have a high FN rate")
    print(f"  but LOW High-class prevalence (e.g., SM>=35). High FN rate means the model fails there,")
    print(f"  but it does NOT mean the indicator zone is enriched for High-class samples.")
    print(f"  For a new indicator to help LR, its zone must have HIGH prevalence (enrichment > 1.0).")

    print("\n" + "=" * 80)
    print("END OF ANALYSIS")
    print("=" * 80)


if __name__ == "__main__":
    main()
