import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from harness.dataset import RANDOM_STATE


EXPERIMENT_NAME = "baseline_hist_gradient_boosting"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    return df.copy()


def build_model(schema: pd.DataFrame) -> Pipeline:
    numeric_columns = schema.select_dtypes(include=["number"]).columns.tolist()
    categorical_columns = [column for column in schema.columns if column not in numeric_columns]

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
