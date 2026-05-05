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
