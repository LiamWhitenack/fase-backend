from collections.abc import Callable
from typing import Any

from pandas import DataFrame, Series
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from app.exploration.machine_learning_ii.data_preparation.transformation import (
    inverse_transform_target,
)
from app.exploration.machine_learning_ii.training.helper_classes import (
    RegressionResult,
)


def build_performance_dataframe(
    results: dict[str, dict[str, Any]],
) -> DataFrame:
    data: dict[str, dict[str, float]] = {}
    for key, res in results.items():
        data[key] = {
            "Evaluation Season": res["test_season"],
            r"Train RMSE": res["train_rmse"],
            r"Validation RMSE": res["validation_rmse"],
            r"Test RMSE": res["test_rmse"],
            # r"Train $R^2$": res["train_r2"],
            # r"Validation $R^2$": res["validation_r2"],
            # r"Test $R^2$": res["test_r2"],
        }

    df = DataFrame.from_dict(data, "index")
    if len(set(df["Evaluation Season"])) == 1:
        df.pop("Evaluation Season")

    return df


def build_performance_dataframe_classification(
    results: dict[str, dict[str, Any]],
) -> DataFrame:
    data: dict[str, dict[str, float]] = {}

    for key, res in results.items():
        data[key] = {
            "Evaluation Season": res["test_season"],
            # classification metrics
            "Train Accuracy": res["train_accuracy"],
            "Validation Accuracy": res["validation_accuracy"],
            "Test Accuracy": res["test_accuracy"],
            "Train AUC": res["train_auc"],
            "Validation AUC": res["validation_auc"],
            "Test AUC": res["test_auc"],
        }

    df = DataFrame.from_dict(data, orient="index")

    if len(set(df["Evaluation Season"])) == 1:
        df = df.drop(columns=["Evaluation Season"])

    return df


def build_feature_importance_dataframe(
    results: dict[str, dict[str, Any]],
    *,
    top_n_features: int | None = 5,
) -> DataFrame:
    data: dict[str, dict[str, float]] = {}
    for key, res in results.items():
        # Add top feature importances
        if top_n_features and res["feature_importance"] is not None:
            top_features = sorted(res["feature_importance"], key=lambda fi: abs(fi[0]))[
                -top_n_features:
            ]
            data[key] = {"Evaluation Season": res["test_season"]}

            for i, (importance, name) in enumerate(top_features, start=1):
                data[key][f"feature_{i}_name"] = name
                data[key][f"feature_{i}_importance"] = abs(importance)

    df = DataFrame.from_dict(data, "index")
    if len(set(df["Evaluation Season"])) == 1:
        df.pop("Evaluation Season")
    return df
