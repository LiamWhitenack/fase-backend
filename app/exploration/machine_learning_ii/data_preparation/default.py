from pandas import DataFrame, Series
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

from app.crud.read.contracts_for_ml import contracts_for_ml, drop_leakage_columns
from app.exploration.machine_learning_ii.data_preparation.add_engineered_features import (
    add_engineered_features,
    add_lag_features,
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


def default_feature_builder() -> DataFrame:
    working = contracts_for_ml()
    working = add_engineered_features(working)
    working = add_lag_features(working)
    working = add_position_ordinal(working)
    working = add_season_deltas(working)
    return drop_leakage_columns(working)


def build_default_preprocessor(
    features: DataFrame,
    numeric_columns: list[str],
) -> ColumnTransformer:
    categorical_columns = [
        column for column in features.columns if column not in numeric_columns
    ]

    def safe_columns(columns: list[str], available: list[str]) -> list[str]:
        return [c for c in columns if c in available]

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
                        # ("imputer", SimpleImputer(strategy="most_frequent")),
                    ]
                ),
                categorical_columns,
            ),
            (
                "numeric",
                "passthrough",
                numeric_columns,
            ),
            # (
            #     "prism",
            #     Pipeline(
            #         steps=[
            #             # ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
            #             ("prism", PcaPrismTransformer()),
            #         ]
            #     ),
            #     numeric_columns,
            # ),
            (
                "passthrough",
                "passthrough",
                safe_columns(
                    ["validation", "contract_type"],
                    features.columns.to_list(),
                ),
            ),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")


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
