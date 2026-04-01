import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from harness.dataset import TARGET_COLUMN, TEST_PATH, TRAIN_PATH


def main() -> None:
    train = pd.read_csv(TRAIN_PATH)
    test = pd.read_csv(TEST_PATH)

    feature_cols = [c for c in train.columns if c not in ("id", TARGET_COLUMN)]
    numeric_cols = train[feature_cols].select_dtypes(include="number").columns.tolist()
    cat_cols = train[feature_cols].select_dtypes(exclude="number").columns.tolist()

    print("=" * 60)
    print("DATASET DIMENSIONS")
    print("=" * 60)
    print(f"train_rows:    {len(train)}")
    print(f"test_rows:     {len(test)}")
    print(f"total_features: {len(feature_cols)}")
    print(f"numeric_features: {len(numeric_cols)}")
    print(f"categorical_features: {len(cat_cols)}")
    print(f"numeric_cols: {numeric_cols}")
    print(f"categorical_cols: {cat_cols}")

    # -------------------------------------------------------
    # 1. CLASS BALANCE
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("CLASS BALANCE (target = Irrigation_Need)")
    print("=" * 60)
    vc = train[TARGET_COLUMN].value_counts()
    vcp = train[TARGET_COLUMN].value_counts(normalize=True)
    balance_df = pd.DataFrame({"count": vc, "proportion": vcp.round(4)})
    print(balance_df.to_string())
    max_prop = vcp.max()
    min_prop = vcp.min()
    imbalance_ratio = max_prop / min_prop
    print(f"imbalance_ratio (max/min): {imbalance_ratio:.4f}")
    if imbalance_ratio > 2.0:
        print("ALERT: severe_class_imbalance=True")
    else:
        print("severe_class_imbalance=False")

    # -------------------------------------------------------
    # 2. MISSINGNESS
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("MISSINGNESS")
    print("=" * 60)
    train_miss = train[feature_cols].isna().mean().sort_values(ascending=False)
    test_miss = test[feature_cols].isna().mean().sort_values(ascending=False)
    any_train_miss = train_miss[train_miss > 0]
    any_test_miss = test_miss[test_miss > 0]
    if any_train_miss.empty:
        print("train_missing: none")
    else:
        print("train_missing (top):")
        print(any_train_miss.head(10).to_string())
    if any_test_miss.empty:
        print("test_missing: none")
    else:
        print("test_missing (top):")
        print(any_test_miss.head(10).to_string())

    # -------------------------------------------------------
    # 3. BOOLEAN-LIKE NUMERICS
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("BOOLEAN-LIKE NUMERICS (<=2 unique values in numeric cols)")
    print("=" * 60)
    bool_like = []
    for c in numeric_cols:
        u = train[c].dropna().nunique()
        vals = sorted(train[c].dropna().unique().tolist())
        if u <= 2:
            bool_like.append((c, u, vals))
    if bool_like:
        for c, u, vals in bool_like:
            print(f"  {c}: nunique={u}, values={vals}")
    else:
        print("  none found")

    # -------------------------------------------------------
    # 4. CATEGORICAL CARDINALITY
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("CATEGORICAL CARDINALITY")
    print("=" * 60)
    for c in cat_cols:
        n_train = train[c].nunique()
        n_test = test[c].nunique()
        print(f"  {c}: train_unique={n_train}, test_unique={n_test}")
        train_vals = set(train[c].dropna().unique())
        test_vals = set(test[c].dropna().unique())
        only_train = train_vals - test_vals
        only_test = test_vals - train_vals
        if only_train:
            print(f"    only_in_train: {sorted(only_train)}")
        if only_test:
            print(f"    only_in_test:  {sorted(only_test)}")

    # -------------------------------------------------------
    # 5. OUTLIER FLAGS (numeric: values beyond 5 IQR fences)
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("OUTLIER FLAGS (|z-score| > 5)")
    print("=" * 60)
    outlier_summary = []
    for c in numeric_cols:
        col = train[c].dropna()
        mean = col.mean()
        std = col.std()
        if std == 0:
            continue
        z = (col - mean) / std
        n_outlier = (z.abs() > 5).sum()
        if n_outlier > 0:
            pct = n_outlier / len(col) * 100
            outlier_summary.append((c, n_outlier, f"{pct:.3f}%"))
    if outlier_summary:
        out_df = pd.DataFrame(outlier_summary, columns=["feature", "n_outliers", "pct"])
        print(out_df.to_string(index=False))
    else:
        print("  no features with |z|>5 outliers")

    # -------------------------------------------------------
    # 6. TRAIN/TEST DISTRIBUTIONAL SHIFT (KS test, numeric)
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("TRAIN/TEST DISTRIBUTIONAL SHIFT (KS test, numeric features)")
    print("=" * 60)
    shift_results = []
    for c in numeric_cols:
        tr = train[c].dropna().values
        te = test[c].dropna().values
        stat, pval = ks_2samp(tr, te)
        shift_results.append((c, round(stat, 5), round(pval, 6)))
    shift_df = pd.DataFrame(shift_results, columns=["feature", "ks_stat", "p_value"])
    shift_df = shift_df.sort_values("ks_stat", ascending=False)
    print(shift_df.to_string(index=False))
    n_significant = (shift_df["p_value"] < 0.01).sum()
    print(f"\nn_features_with_significant_shift (p<0.01): {n_significant} / {len(numeric_cols)}")
    if n_significant > 0:
        print("ALERT: meaningful_train_test_shift=True")
    else:
        print("meaningful_train_test_shift=False")

    # -------------------------------------------------------
    # 7. NUMERIC FEATURE SUMMARY (range, mean, std)
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("NUMERIC FEATURE SUMMARY (train)")
    print("=" * 60)
    desc = train[numeric_cols].describe().T[["min", "max", "mean", "std"]]
    print(desc.round(4).to_string())

    # -------------------------------------------------------
    # 8. LEAKAGE CHECK: numeric cols that perfectly predict target
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("LEAKAGE SCREEN (numeric feature mean absolute correlation with label-encoded target)")
    print("=" * 60)
    label_map = {v: i for i, v in enumerate(sorted(train[TARGET_COLUMN].unique()))}
    y = train[TARGET_COLUMN].map(label_map)
    corrs = []
    for c in numeric_cols:
        corr = train[c].corr(y)
        corrs.append((c, round(corr, 5)))
    corr_df = pd.DataFrame(corrs, columns=["feature", "pearson_corr_with_label"])
    corr_df = corr_df.reindex(corr_df["pearson_corr_with_label"].abs().sort_values(ascending=False).index)
    print(corr_df.to_string(index=False))
    max_abs_corr = corr_df["pearson_corr_with_label"].abs().max()
    if max_abs_corr > 0.95:
        print(f"\nALERT: possible_leakage=True (max_abs_corr={max_abs_corr:.4f})")
    else:
        print(f"\nmax_abs_corr={max_abs_corr:.4f} — no obvious leakage detected")

    # -------------------------------------------------------
    # SUMMARY VERDICT
    # -------------------------------------------------------
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    issues = []
    if imbalance_ratio > 2.0:
        issues.append(f"severe class imbalance (ratio={imbalance_ratio:.2f})")
    if not any_train_miss.empty:
        issues.append(f"missing values in train ({len(any_train_miss)} features)")
    if not any_test_miss.empty:
        issues.append(f"missing values in test ({len(any_test_miss)} features)")
    if max_abs_corr > 0.95:
        issues.append(f"potential leakage feature (max_abs_corr={max_abs_corr:.4f})")
    if n_significant > 0:
        issues.append(f"train/test shift in {n_significant} features (KS p<0.01)")
    if issues:
        print("critical_issues_found: YES")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("critical_issues_found: NO")
        print("  Dataset appears clean: no missingness, no leakage, no severe imbalance, no significant distributional shift.")


if __name__ == "__main__":
    main()
