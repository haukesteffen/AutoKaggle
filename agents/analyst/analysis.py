import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np
import pandas as pd
from harness.dataset import TARGET_COLUMN, TRAIN_PATH


def load_data():
    """Load train data, targets, and S-005 OOF predictions."""
    train_df = pd.read_csv(TRAIN_PATH, index_col=0)

    # Load S-005 OOF predictions
    oof_preds = np.load(REPO_ROOT / "artifacts" / "S-005" / "oof-preds.npy")

    return train_df, oof_preds


def get_predicted_class(probs):
    """Convert probability array to predicted class index."""
    return np.argmax(probs, axis=1)


def main() -> None:
    train_df, oof_preds = load_data()

    # Map class names to indices (assumed order: Low=0, Medium=1, High=2)
    class_to_idx = {"Low": 0, "Medium": 1, "High": 2}
    idx_to_class = {v: k for k, v in class_to_idx.items()}

    # Get true targets
    y_true = train_df[TARGET_COLUMN].map(class_to_idx).values

    # Get predicted classes
    y_pred = get_predicted_class(oof_preds)

    # Overall accuracy
    accuracy = (y_true == y_pred).sum() / len(y_true)

    # Identify mispredictions
    is_correct = (y_true == y_pred)
    is_mispredicted = ~is_correct

    # Focus on High class (index 2)
    high_mask = y_true == class_to_idx["High"]
    high_correct = is_correct & high_mask
    high_mispredicted = is_mispredicted & high_mask

    print("=" * 70)
    print("OVERALL MODEL PERFORMANCE")
    print("=" * 70)
    print(f"OOF Accuracy: {accuracy:.4f}")
    print(f"Total samples: {len(y_true)}")
    print(f"Correct predictions: {is_correct.sum()}")
    print(f"Mispredictions: {is_mispredicted.sum()}")
    print()

    print("=" * 70)
    print("HIGH CLASS PERFORMANCE (Target = High)")
    print("=" * 70)
    print(f"Total High samples: {high_mask.sum()}")
    print(f"High correctly predicted: {high_correct.sum()}")
    print(f"High mispredicted: {high_mispredicted.sum()}")
    print(f"High recall: {high_correct.sum() / high_mask.sum():.4f}")
    print()

    # Analyze feature distributions in High class
    print("=" * 70)
    print("SOIL_MOISTURE DISTRIBUTION IN HIGH CLASS")
    print("=" * 70)

    high_subset = train_df[high_mask].copy()
    high_correct_subset = train_df[high_correct].copy()
    high_mispredicted_subset = train_df[high_mispredicted].copy()

    # Show overall stats for High class
    print("\nSOIL_MOISTURE stats for all High samples:")
    print(f"  Mean: {high_subset['Soil_Moisture'].mean():.2f}")
    print(f"  Std:  {high_subset['Soil_Moisture'].std():.2f}")
    print(f"  Min:  {high_subset['Soil_Moisture'].min():.2f}")
    print(f"  Max:  {high_subset['Soil_Moisture'].max():.2f}")

    if len(high_correct_subset) > 0:
        print("\nSOIL_MOISTURE stats for correctly predicted High samples:")
        print(f"  Mean: {high_correct_subset['Soil_Moisture'].mean():.2f}")
        print(f"  Std:  {high_correct_subset['Soil_Moisture'].std():.2f}")
        print(f"  Min:  {high_correct_subset['Soil_Moisture'].min():.2f}")
        print(f"  Max:  {high_correct_subset['Soil_Moisture'].max():.2f}")
        print(f"  Count: {len(high_correct_subset)}")

    if len(high_mispredicted_subset) > 0:
        print("\nSOIL_MOISTURE stats for MISPREDICTED High samples:")
        print(f"  Mean: {high_mispredicted_subset['Soil_Moisture'].mean():.2f}")
        print(f"  Std:  {high_mispredicted_subset['Soil_Moisture'].std():.2f}")
        print(f"  Min:  {high_mispredicted_subset['Soil_Moisture'].min():.2f}")
        print(f"  Max:  {high_mispredicted_subset['Soil_Moisture'].max():.2f}")
        print(f"  Count: {len(high_mispredicted_subset)}")

    print()

    # Interaction analysis: Soil_Moisture × Temperature
    print("=" * 70)
    print("INTERACTION: Soil_Moisture × Temperature_C")
    print("=" * 70)

    # Bin Soil_Moisture and Temperature
    sm_bins = pd.cut(train_df["Soil_Moisture"], bins=3, labels=["Low_SM", "Mid_SM", "High_SM"])
    temp_bins = pd.cut(train_df["Temperature_C"], bins=3, labels=["Low_Temp", "Mid_Temp", "High_Temp"])

    interaction_df = pd.DataFrame({
        "SM_bin": sm_bins,
        "Temp_bin": temp_bins,
        "is_high": y_true == class_to_idx["High"]
    })

    pivot_high = interaction_df.groupby(["SM_bin", "Temp_bin"])["is_high"].agg(["sum", "count", "mean"])
    pivot_high.columns = ["High_count", "Total_count", "High_proportion"]
    print("\nHigh-class proportion by Soil_Moisture × Temperature bins:")
    print(pivot_high)
    print()

    # Interaction analysis: Soil_Moisture × Humidity
    print("=" * 70)
    print("INTERACTION: Soil_Moisture × Humidity")
    print("=" * 70)

    humidity_bins = pd.cut(train_df["Humidity"], bins=3, labels=["Low_Humidity", "Mid_Humidity", "High_Humidity"])
    interaction_df = pd.DataFrame({
        "SM_bin": sm_bins,
        "Humidity_bin": humidity_bins,
        "is_high": y_true == class_to_idx["High"]
    })

    pivot_high = interaction_df.groupby(["SM_bin", "Humidity_bin"])["is_high"].agg(["sum", "count", "mean"])
    pivot_high.columns = ["High_count", "Total_count", "High_proportion"]
    print("\nHigh-class proportion by Soil_Moisture × Humidity bins:")
    print(pivot_high)
    print()

    # Interaction analysis: Soil_Moisture × Rainfall
    print("=" * 70)
    print("INTERACTION: Soil_Moisture × Rainfall_mm")
    print("=" * 70)

    rainfall_bins = pd.cut(train_df["Rainfall_mm"], bins=3, labels=["Low_Rain", "Mid_Rain", "High_Rain"])
    interaction_df = pd.DataFrame({
        "SM_bin": sm_bins,
        "Rainfall_bin": rainfall_bins,
        "is_high": y_true == class_to_idx["High"]
    })

    pivot_high = interaction_df.groupby(["SM_bin", "Rainfall_bin"])["is_high"].agg(["sum", "count", "mean"])
    pivot_high.columns = ["High_count", "Total_count", "High_proportion"]
    print("\nHigh-class proportion by Soil_Moisture × Rainfall bins:")
    print(pivot_high)
    print()

    # Interaction analysis: Soil_Moisture × Crop_Type
    print("=" * 70)
    print("INTERACTION: Soil_Moisture × Crop_Type")
    print("=" * 70)

    interaction_df = pd.DataFrame({
        "SM_bin": sm_bins,
        "Crop_Type": train_df["Crop_Type"],
        "is_high": y_true == class_to_idx["High"]
    })

    pivot_high = interaction_df.groupby(["SM_bin", "Crop_Type"])["is_high"].agg(["sum", "count", "mean"])
    pivot_high.columns = ["High_count", "Total_count", "High_proportion"]
    print("\nHigh-class proportion by Soil_Moisture × Crop_Type:")
    print(pivot_high.sort_values("High_proportion", ascending=False).head(10))
    print()

    # Interaction analysis: Soil_Moisture × Season
    print("=" * 70)
    print("INTERACTION: Soil_Moisture × Season")
    print("=" * 70)

    interaction_df = pd.DataFrame({
        "SM_bin": sm_bins,
        "Season": train_df["Season"],
        "is_high": y_true == class_to_idx["High"]
    })

    pivot_high = interaction_df.groupby(["SM_bin", "Season"])["is_high"].agg(["sum", "count", "mean"])
    pivot_high.columns = ["High_count", "Total_count", "High_proportion"]
    print("\nHigh-class proportion by Soil_Moisture × Season:")
    print(pivot_high.sort_values("High_proportion", ascending=False))
    print()

    # Analyze mispredictions more deeply
    print("=" * 70)
    print("MISPREDICTION ANALYSIS (High Class)")
    print("=" * 70)

    if len(high_mispredicted_subset) > 0:
        # What were they predicted as?
        pred_classes = y_pred[high_mispredicted]
        pred_class_names = [idx_to_class[p] for p in pred_classes]
        pred_counts = pd.Series(pred_class_names).value_counts()
        print("\nHigh samples mispredicted as:")
        print(pred_counts)
        print()

        # Feature patterns in mispredicted High samples
        print("Feature comparison: Correctly predicted HIGH vs. Mispredicted HIGH")
        print("-" * 70)

        feature_cols = ["Soil_Moisture", "Temperature_C", "Humidity", "Rainfall_mm",
                       "Wind_Speed_kmh", "Sunlight_Hours"]

        comparison_data = []
        for col in feature_cols:
            correct_mean = high_correct_subset[col].mean() if len(high_correct_subset) > 0 else np.nan
            correct_std = high_correct_subset[col].std() if len(high_correct_subset) > 0 else np.nan
            mispred_mean = high_mispredicted_subset[col].mean() if len(high_mispredicted_subset) > 0 else np.nan
            mispred_std = high_mispredicted_subset[col].std() if len(high_mispredicted_subset) > 0 else np.nan

            diff = mispred_mean - correct_mean if not np.isnan(correct_mean) and not np.isnan(mispred_mean) else 0

            comparison_data.append({
                "Feature": col,
                "Correct_Mean": correct_mean,
                "Correct_Std": correct_std,
                "Mispred_Mean": mispred_mean,
                "Mispred_Std": mispred_std,
                "Difference": diff
            })

        comparison_df = pd.DataFrame(comparison_data)
        print(comparison_df.to_string(index=False))
        print()

    # Check for non-linearity: Soil_Moisture in different regions
    print("=" * 70)
    print("SOIL_MOISTURE NON-LINEARITY CHECK: Stratified by High-class density")
    print("=" * 70)

    # Create finer bins to check for local patterns
    sm_fine_bins = pd.cut(train_df["Soil_Moisture"], bins=5)
    high_by_sm_bin = train_df.groupby(sm_fine_bins).apply(
        lambda x: (x[TARGET_COLUMN] == "High").sum() / len(x) if len(x) > 0 else 0
    )

    print("\nHigh-class prevalence by Soil_Moisture quintile:")
    for i, (bin_range, proportion) in enumerate(high_by_sm_bin.items()):
        print(f"  Bin {i+1} {bin_range}: {proportion:.4f}")

    print()


if __name__ == "__main__":
    main()
