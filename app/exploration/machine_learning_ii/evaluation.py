from collections.abc import Iterable
from datetime import timedelta

from numpy import array, log1p, sqrt
from pandas import DataFrame
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    explained_variance_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    median_absolute_error,
    r2_score,
)
from sklearn.pipeline import Pipeline

from app.exploration.machine_learning_ii.feature_engineering import partition_by_family


def root_mean_squared_error(
    true: Iterable[float],
    predictions: Iterable[float],
) -> float:
    return sqrt(mean_squared_error(true, predictions))


def root_mean_squared_log_error(
    true: Iterable[float],
    predictions: Iterable[float],
) -> float:
    true_array = array(true)
    predictions_array = array(predictions)

    # guard against negative predictions
    predictions_array = predictions_array.clip(min=0)

    return sqrt(mean_squared_error(log1p(true_array), log1p(predictions_array)))


def scoring(
    true: Iterable[float],
    predictions: Iterable[float],
) -> dict[str, float]:
    return {
        "r2": r2_score(true, predictions),
        "explained_variance": explained_variance_score(true, predictions),
        "mae": mean_absolute_error(true, predictions),
        "median_absolute_error": median_absolute_error(true, predictions),
        "mse": mean_squared_error(true, predictions),
        "rmse": root_mean_squared_error(true, predictions),
        "mape": mean_absolute_percentage_error(true, predictions),
        "rmsle": root_mean_squared_log_error(true, predictions),
    }
