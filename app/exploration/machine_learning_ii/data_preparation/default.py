from collections.abc import Callable

import optuna
from pandas import DataFrame, Series
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

from app.crud.read.contracts_for_ml import contracts_for_ml
from app.exploration.machine_learning_ii.data_preparation.add_engineered_features import (
    add_engineered_features,
    add_position_ordinal,
    add_season_deltas,
)
from app.exploration.machine_learning_ii.data_preparation.basic import (
    PreparedPipelineData,
    get_numeric_and_categorical_columns,
)
from app.exploration.machine_learning_ii.data_preparation.position_labeling_helper import (
    PcaPrismTransformer,
)
from app.exploration.machine_learning_ii.data_preparation.transformation import (
    transform_target,
)
from app.exploration.machine_learning_ii.train_models.helper_classes import (
    PreparedData,
)


def default_feature_builder() -> DataFrame:
    working = contracts_for_ml()
    working = add_engineered_features(working)
    working = add_position_ordinal(working)
    # working = add_season_deltas(working)
    return working


def prepare_training_data(
    *,
    target_column: str = "relative_dollars",
    feature_builder: Callable[[], DataFrame] | None = None,
    target_transform: Callable[[Series], Series] = transform_target,
) -> PreparedData:
    if feature_builder is None:
        processed_dataframe = default_feature_builder()
    else:
        processed_dataframe = feature_builder()

    target = processed_dataframe.pop(target_column)
    transformed_target = target_transform(target)

    numeric_columns, categorical_columns = get_numeric_and_categorical_columns(
        processed_dataframe
    )

    return PreparedData(
        features=processed_dataframe,
        target=transformed_target,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )


def build_default_preprocessor(
    features: DataFrame,
    numeric_columns: list[str],
) -> ColumnTransformer:
    categorical_columns = [
        column for column in features.columns if column not in numeric_columns
    ]

    return ColumnTransformer(
        transformers=[
            (
                "categorical",
                Pipeline(
                    steps=[
                        (
                            "onehot",
                            OneHotEncoder(
                                handle_unknown="ignore",
                                sparse_output=False,
                            ),
                        ),
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                    ]
                ),
                categorical_columns,
            ),
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
                        ("scaler", RobustScaler()),
                    ]
                ),
                numeric_columns,
            ),
            (
                "prism",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
                        ("prism", PcaPrismTransformer()),
                    ]
                ),
                numeric_columns,
            ),
        ],
        remainder="drop",
    )


def prepare_data(df: DataFrame) -> PreparedPipelineData:
    df = df.copy()

    if "relative_dollars" not in df.columns:
        raise KeyError(f"Missing target column: relative_dollars")

    df = df.dropna(subset=["relative_dollars"])

    features_engineered = add_engineered_features(df)
    y_raw = features_engineered["relative_dollars"]
    y_log = transform_target(y_raw)

    numeric_cols, categorical_cols = get_numeric_and_categorical_columns(
        features_engineered
    )
    feature_cols = numeric_cols + categorical_cols

    X = features_engineered[feature_cols].copy()

    preprocessor = build_default_preprocessor(X, numeric_cols)
    X_transformed = preprocessor.fit_transform(X)
    feature_names = list(preprocessor.get_feature_names_out())

    return PreparedPipelineData(
        features_raw=X.copy(),
        features_engineered=X.copy(),
        target_raw=y_raw,
        target_log=y_log,
        transformed_matrix=X_transformed,
        transformed_feature_names=feature_names,
    )
