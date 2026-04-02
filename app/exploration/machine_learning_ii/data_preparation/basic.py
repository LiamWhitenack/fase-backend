from dataclasses import dataclass

from numpy import ndarray
from pandas import DataFrame, Series
from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,  # ty:ignore[unresolved-import]
    is_numeric_dtype,
    is_object_dtype,
    is_string_dtype,
)
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, PolynomialFeatures, RobustScaler


def get_numeric_and_categorical_columns(
    df: DataFrame,
    exclude_cols: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    exclude = set(exclude_cols or [])

    numeric_cols = [
        col
        for col in df.columns
        if col not in exclude
        and is_numeric_dtype(df[col])
        and not is_bool_dtype(df[col])
    ]

    categorical_cols = [
        col
        for col in df.columns
        if col not in exclude
        and (
            is_object_dtype(df[col])
            or is_string_dtype(df[col])
            or is_categorical_dtype(df[col])
            or is_bool_dtype(df[col])
        )
    ]

    return numeric_cols, categorical_cols


def add_polynomial_structure(
    X_transformed: ndarray,
    feature_names: list[str],
    max_base_features: int = 12,
) -> tuple[ndarray, list[str]]:
    """
    Adds limited interaction structure to the most interpretable base features.
    This avoids exploding dimensionality while still capturing nonlinear patterns.
    """
    if X_transformed.shape[1] <= max_base_features:
        selected = X_transformed
        selected_names = feature_names
    else:
        selected = X_transformed[:, :max_base_features]
        selected_names = feature_names[:max_base_features]

    poly = PolynomialFeatures(
        degree=2,
        include_bias=False,
        interaction_only=False,
    )
    X_poly = poly.fit_transform(selected)
    poly_names = list(poly.get_feature_names_out(selected_names))
    return X_poly, poly_names


@dataclass
class PreparedPipelineData:
    features_raw: DataFrame
    features_engineered: DataFrame
    target_raw: Series
    target_log: Series
    transformed_matrix: ndarray
    transformed_feature_names: list[str]
