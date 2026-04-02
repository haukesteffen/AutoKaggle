#!/usr/bin/env python3
"""
Analysis of S-014 XGBoost model (CV=0.9709) to understand:
- Fold stability and which folds drive the score
- Feature importance, especially SM² contribution
- Subgroup performance by target class, season, region
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
import pickle
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, recall_score
from harness.dataset import (
    load_train_with_folds, split_xy, class_probabilities_to_indices,
    CLASS_LABELS, encode_target_labels, TARGET_COLUMN, FOLD_COLUMN
)


ARTIFACTS_DIR = Path(REPO_ROOT) / "artifacts" / "S-014"


def main():
    # Load model, OOF predictions, train data with folds
    print("=" * 70)
    print("S-014 MODEL ANALYSIS (XGBoost, depth=5, subsample=0.8, colsample=0.8)")
    print("=" * 70)

    # Load model - with fallback if pickle fails
    model = None
    try:
        with open(ARTIFACTS_DIR / "model.pkl", "rb") as f:
            model = pickle.load(f)
    except (ModuleNotFoundError, ImportError, pickle.UnpicklingError) as e:
        print(f"Note: Could not load pickled model ({type(e).__name__}). Feature importance will be unavailable.")

    # Load OOF predictions
    oof_preds = np.load(ARTIFACTS_DIR / "oof-preds.npy")

    # Load train data with folds and target
    train_df = load_train_with_folds()
    raw_X, y = split_xy(train_df)

    # Decode target labels for reporting
    y_labels = pd.Series([CLASS_LABELS[i] for i in y], name="Irrigation_Need")

    print("\n" + "=" * 70)
    print("FOLD-BY-FOLD PERFORMANCE")
    print("=" * 70)

    fold_scores = []
    fold_details = []

    for fold in sorted(train_df[FOLD_COLUMN].unique()):
        fold_mask = train_df[FOLD_COLUMN] == fold
        y_fold = y[fold_mask.to_numpy()]
        oof_fold = oof_preds[fold_mask.to_numpy(), :]

        y_pred = class_probabilities_to_indices(oof_fold)
        fold_score = balanced_accuracy_score(y_fold, y_pred)
        fold_scores.append(fold_score)

        # Per-class recall for this fold
        recalls = {}
        for i, label in enumerate(CLASS_LABELS):
            class_mask = y_fold == i
            if class_mask.sum() > 0:
                class_recall = recall_score(y_fold, y_pred, labels=[i], average='macro')
                recalls[label] = class_recall
            else:
                recalls[label] = np.nan

        fold_details.append({
            'fold': fold,
            'score': fold_score,
            'n_samples': fold_mask.sum(),
            'recalls': recalls
        })

        print(f"Fold {fold}: score={fold_score:.6f}, n={fold_mask.sum()}, "
              f"recalls: High={recalls['High']:.4f}, Low={recalls['Low']:.4f}, Medium={recalls['Medium']:.4f}")

    print(f"\nFold Scores: {[f'{s:.6f}' for s in fold_scores]}")
    print(f"Mean CV: {np.mean(fold_scores):.6f}")
    print(f"Std CV: {np.std(fold_scores):.6f}")
    print(f"Min Fold: {np.argmin(fold_scores)} ({np.min(fold_scores):.6f})")
    print(f"Max Fold: {np.argmax(fold_scores)} ({np.max(fold_scores):.6f})")

    # Overall fold metrics
    y_pred_all = class_probabilities_to_indices(oof_preds)
    overall_score = balanced_accuracy_score(y, y_pred_all)
    print(f"Overall Balanced Accuracy (OOF): {overall_score:.6f}")

    print("\n" + "=" * 70)
    print("PER-CLASS PERFORMANCE (OVERALL OOF)")
    print("=" * 70)

    for i, label in enumerate(CLASS_LABELS):
        class_mask = y == i
        class_recall = recall_score(y, y_pred_all, labels=[i], average='macro')
        class_count = class_mask.sum()
        class_pct = 100 * class_count / len(y)

        # Confusion matrix for this class
        cm = confusion_matrix(y, y_pred_all, labels=list(range(len(CLASS_LABELS))))
        tp = cm[i, i]
        fp = cm[:, i].sum() - tp
        fn = cm[i, :].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0

        print(f"\n{label} (class idx {i}):")
        print(f"  Count: {class_count} ({class_pct:.2f}%)")
        print(f"  Recall: {class_recall:.6f}")
        print(f"  Precision: {precision:.6f}")
        print(f"  TP={tp}, FP={fp}, FN={fn}")

    print("\n" + "=" * 70)
    print("FEATURE IMPORTANCE (from S-014 model)")
    print("=" * 70)

    # Extract feature importance from the model
    # The model is wrapped, so we need to access the underlying xgb_model
    if model is not None:
        if hasattr(model, 'xgb_model'):
            xgb_model = model.xgb_model
            if hasattr(xgb_model, 'get_booster'):
                booster = xgb_model.get_booster()
                importance_dict = booster.get_score(importance_type='weight')

                # Sort by importance
                sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                print(f"\nTop 10 Features by Weight (total features: {len(importance_dict)}):")
                for rank, (feat_name, importance) in enumerate(sorted_importance[:10], 1):
                    print(f"  {rank}. {feat_name}: {importance}")

                # Check for SM² presence
                sm_squared_found = False
                for feat_name, importance in sorted_importance:
                    if 'Soil_Moisture' in feat_name and '2' in feat_name:
                        sm_squared_found = True
                        rank = [f[0] for f in sorted_importance].index(feat_name) + 1
                        print(f"\nSoil_Moisture² found at rank {rank} with importance {importance}")
                        break

                if not sm_squared_found:
                    print(f"\nNote: Soil_Moisture² (or polynomial term) not found in top features.")
                    print("Checking for all polynomial terms...")
                    poly_terms = [f for f in importance_dict.keys() if any(c.isdigit() for c in f) and 'soil_moisture' in f.lower()]
                    if poly_terms:
                        print(f"Polynomial terms found: {poly_terms}")
        else:
            print("Note: Model wrapper does not expose feature importance directly.")
    else:
        print("Note: Model pickle could not be loaded. Feature importance unavailable.")

    print("\n" + "=" * 70)
    print("SUBGROUP ANALYSIS: PERFORMANCE BY REGION")
    print("=" * 70)

    for region in sorted(train_df['Region'].unique()):
        region_mask = train_df['Region'] == region
        y_region = y[region_mask.to_numpy()]
        oof_region = oof_preds[region_mask.to_numpy(), :]
        y_pred_region = class_probabilities_to_indices(oof_region)

        region_score = balanced_accuracy_score(y_region, y_pred_region)
        region_count = region_mask.sum()
        region_pct = 100 * region_count / len(y)

        print(f"\n{region} (n={region_count}, {region_pct:.2f}%):")
        print(f"  Balanced Accuracy: {region_score:.6f}")

        for i, label in enumerate(CLASS_LABELS):
            class_mask = y_region == i
            if class_mask.sum() > 0:
                class_recall = recall_score(y_region, y_pred_region, labels=[i], average='macro')
                print(f"  {label} Recall: {class_recall:.6f} (n={class_mask.sum()})")

    print("\n" + "=" * 70)
    print("SUBGROUP ANALYSIS: PERFORMANCE BY SEASON")
    print("=" * 70)

    for season in sorted(train_df['Season'].unique()):
        season_mask = train_df['Season'] == season
        y_season = y[season_mask.to_numpy()]
        oof_season = oof_preds[season_mask.to_numpy(), :]
        y_pred_season = class_probabilities_to_indices(oof_season)

        season_score = balanced_accuracy_score(y_season, y_pred_season)
        season_count = season_mask.sum()
        season_pct = 100 * season_count / len(y)

        print(f"\n{season} (n={season_count}, {season_pct:.2f}%):")
        print(f"  Balanced Accuracy: {season_score:.6f}")

        for i, label in enumerate(CLASS_LABELS):
            class_mask = y_season == i
            if class_mask.sum() > 0:
                class_recall = recall_score(y_season, y_pred_season, labels=[i], average='macro')
                print(f"  {label} Recall: {class_recall:.6f} (n={class_mask.sum()})")

    print("\n" + "=" * 70)
    print("SUBGROUP ANALYSIS: HIGH CLASS RECALL BY REGION & SEASON")
    print("=" * 70)

    high_class_idx = CLASS_LABELS.index('High')

    # By Region
    print("\nHigh-class Recall by Region:")
    region_recalls = {}
    for region in sorted(train_df['Region'].unique()):
        region_mask = train_df['Region'] == region
        y_region = y[region_mask.to_numpy()]
        oof_region = oof_preds[region_mask.to_numpy(), :]
        y_pred_region = class_probabilities_to_indices(oof_region)

        high_mask = y_region == high_class_idx
        if high_mask.sum() > 0:
            high_recall = recall_score(y_region, y_pred_region, labels=[high_class_idx], average='macro')
            region_recalls[region] = (high_recall, high_mask.sum())
            print(f"  {region}: {high_recall:.6f} (n_high={high_mask.sum()})")
        else:
            region_recalls[region] = (np.nan, 0)
            print(f"  {region}: no High samples")

    # By Season
    print("\nHigh-class Recall by Season:")
    season_recalls = {}
    for season in sorted(train_df['Season'].unique()):
        season_mask = train_df['Season'] == season
        y_season = y[season_mask.to_numpy()]
        oof_season = oof_preds[season_mask.to_numpy(), :]
        y_pred_season = class_probabilities_to_indices(oof_season)

        high_mask = y_season == high_class_idx
        if high_mask.sum() > 0:
            high_recall = recall_score(y_season, y_pred_season, labels=[high_class_idx], average='macro')
            season_recalls[season] = (high_recall, high_mask.sum())
            print(f"  {season}: {high_recall:.6f} (n_high={high_mask.sum()})")
        else:
            season_recalls[season] = (np.nan, 0)
            print(f"  {season}: no High samples")

    # By Crop Type
    print("\nHigh-class Recall by Crop_Type:")
    crop_recalls = {}
    for crop in sorted(train_df['Crop_Type'].unique()):
        crop_mask = train_df['Crop_Type'] == crop
        y_crop = y[crop_mask.to_numpy()]
        oof_crop = oof_preds[crop_mask.to_numpy(), :]
        y_pred_crop = class_probabilities_to_indices(oof_crop)

        high_mask = y_crop == high_class_idx
        if high_mask.sum() > 0:
            high_recall = recall_score(y_crop, y_pred_crop, labels=[high_class_idx], average='macro')
            crop_recalls[crop] = (high_recall, high_mask.sum())
            print(f"  {crop}: {high_recall:.6f} (n_high={high_mask.sum()})")
        else:
            crop_recalls[crop] = (np.nan, 0)
            print(f"  {crop}: no High samples")

    print("\n" + "=" * 70)
    print("SUMMARY: HARDEST FOLDS & SUBGROUPS")
    print("=" * 70)

    # Find hardest fold
    hardest_fold_idx = np.argmin(fold_scores)
    hardest_fold_score = fold_scores[hardest_fold_idx]
    print(f"\nHardest Fold: Fold {hardest_fold_idx} with score {hardest_fold_score:.6f}")

    # Find worst subgroup by High-class recall
    valid_recalls = {k: v[0] for k, v in season_recalls.items() if not np.isnan(v[0])}
    if valid_recalls:
        worst_season = min(valid_recalls.items(), key=lambda x: x[1])
        print(f"Worst Season for High-class Recall: {worst_season[0]} ({worst_season[1]:.6f})")

    valid_region_recalls = {k: v[0] for k, v in region_recalls.items() if not np.isnan(v[0])}
    if valid_region_recalls:
        worst_region = min(valid_region_recalls.items(), key=lambda x: x[1])
        print(f"Worst Region for High-class Recall: {worst_region[0]} ({worst_region[1]:.6f})")

    # Find worst crop
    valid_crop_recalls = {k: v[0] for k, v in crop_recalls.items() if not np.isnan(v[0])}
    if valid_crop_recalls:
        worst_crop = min(valid_crop_recalls.items(), key=lambda x: x[1])
        print(f"Worst Crop for High-class Recall: {worst_crop[0]} ({worst_crop[1]:.6f})")


if __name__ == "__main__":
    main()
