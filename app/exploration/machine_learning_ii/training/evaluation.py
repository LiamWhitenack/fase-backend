from collections.abc import Callable
from typing import Any

from pandas import DataFrame, Series
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from app.exploration.machine_learning_ii.data_preparation.transformation import (
    inverse_transform_target,
)
from app.exploration.machine_learning_ii.training.helper_classes import (
    EvaluationResult,
)


def score_pipeline(
    pipeline: Pipeline,
    *,
    X_train: DataFrame,
    X_test: DataFrame,
    y_train: Series,
    y_test: Series,
    inverse_target_transform: Callable[[Series], Series],
) -> EvaluationResult:
    pipeline.fit(X_train, y_train)

    train_predictions_transformed = Series(
        pipeline.predict(X_train),
        index=y_train.index,
        name=y_train.name,
    )
    test_predictions_transformed = Series(
        pipeline.predict(X_test),
        index=y_test.index,
        name=y_test.name,
    )

    train_predictions = inverse_target_transform(
        train_predictions_transformed,
    )
    test_predictions = inverse_target_transform(
        test_predictions_transformed,
    )
    y_train_original = inverse_target_transform(y_train)
    y_test_original = inverse_target_transform(y_test)

    return EvaluationResult(
        train_predictions=train_predictions,
        test_predictions=test_predictions,
        y_train_original=y_train_original,
        y_test_original=y_test_original,
        train_mae=mean_absolute_error(y_train_original, train_predictions),
        test_mae=mean_absolute_error(y_test_original, test_predictions),
        train_rmse=root_mean_squared_error(y_train_original, train_predictions),
        test_rmse=root_mean_squared_error(y_test_original, test_predictions),
        train_r2=r2_score(y_train_original, train_predictions),
        test_r2=r2_score(y_test_original, test_predictions),
    )


def build_results_dataframe(
    results: list[dict[str, Any]],
    *,
    top_n_features: int | None = 5,
) -> DataFrame:
    """
    Convert a list of training result dicts into a clean DataFrame
    suitable for reporting / papers.

    Parameters
    ----------
    results : list of dict
        Output from your training pipeline
    include_params : bool
        Whether to expand best_params into columns
    top_n_features : int | None
        Number of top features to include (None = skip)

    Returns
    -------
    DataFrame
    """
    rows: list[dict[str, Any]] = []

    for res in results:
        row: dict[str, Any] = {
            "validation_season": res["validation_season"],
            "test_season": res["test_season"],
            "train_mae": res["train_mae"],
            "test_mae": res["test_mae"],
            "train_rmse": res["train_rmse"],
            "test_rmse": res["test_rmse"],
            "train_r2": res["train_r2"],
            "test_r2": res["test_r2"],
            "best_value": res["best_value"],
        }

        # Add top feature importances
        if top_n_features and res["feature_importance"] is not None:
            top_features = res["feature_importance"][:top_n_features]

            for i, (importance, name) in enumerate(top_features, start=1):
                row[f"feature_{i}_name"] = name
                row[f"feature_{i}_importance"] = importance

        rows.append(row)

    return DataFrame(rows)
