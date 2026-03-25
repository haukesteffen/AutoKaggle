import time

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from prepare import (
    FOLD_COLUMN,
    FOLD_ROW_INDEX_COLUMN,
    FOLDS_PATH,
    ID_COLUMN,
    NEGATIVE_LABEL,
    POSITIVE_LABEL,
    RANDOM_STATE,
    TARGET_COLUMN,
    TRAIN_PATH,
)


def load_training_frame() -> pd.DataFrame:
    train_df = pd.read_csv(TRAIN_PATH)
    folds_df = pd.read_csv(FOLDS_PATH).sort_values(FOLD_ROW_INDEX_COLUMN).reset_index(drop=True)

    expected_indices = pd.Series(np.arange(len(train_df)), name=FOLD_ROW_INDEX_COLUMN)
    if len(folds_df) != len(train_df) or not folds_df[FOLD_ROW_INDEX_COLUMN].equals(expected_indices):
        raise ValueError("fold assignments do not align with the training rows")

    train_df[FOLD_COLUMN] = folds_df[FOLD_COLUMN].to_numpy()
    return train_df


def build_pipeline(X: pd.DataFrame) -> Pipeline:
    numeric_columns = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = [column for column in X.columns if column not in numeric_columns]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                    ]
                ),
                numeric_columns,
            ),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical_columns,
            ),
        ]
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", HistGradientBoostingClassifier(random_state=RANDOM_STATE)),
        ]
    )


def evaluate() -> tuple[list[float], float]:
    train_df = load_training_frame()
    y = train_df[TARGET_COLUMN].map({NEGATIVE_LABEL: 0, POSITIVE_LABEL: 1}).to_numpy()
    X = train_df.drop(columns=[ID_COLUMN, TARGET_COLUMN, FOLD_COLUMN])

    fold_scores: list[float] = []
    training_start = time.perf_counter()

    for fold in sorted(train_df[FOLD_COLUMN].unique()):
        train_mask = train_df[FOLD_COLUMN] != fold
        valid_mask = ~train_mask

        pipeline = build_pipeline(X)
        pipeline.fit(X.loc[train_mask], y[train_mask.to_numpy()])

        valid_pred = pipeline.predict_proba(X.loc[valid_mask])[:, 1]
        fold_score = roc_auc_score(y[valid_mask.to_numpy()], valid_pred)
        fold_scores.append(float(fold_score))

    training_seconds = time.perf_counter() - training_start
    return fold_scores, training_seconds


def main() -> None:
    total_start = time.perf_counter()
    fold_scores, training_seconds = evaluate()
    total_seconds = time.perf_counter() - total_start

    print("---")
    print(f"mean_cv_roc_auc:  {np.mean(fold_scores):.6f}")
    print(f"std_cv_roc_auc:   {np.std(fold_scores):.6f}")
    print(f"training_seconds: {training_seconds:.1f}")
    print(f"total_seconds:    {total_seconds:.1f}")


if __name__ == "__main__":
    main()
