from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any, Literal

import optuna
import xgboost
from pandas import DataFrame, Series
from pandas.errors import PerformanceWarning
from sklearn.base import ClassifierMixin
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_squared_error, r2_score

import app.exploration.machine_learning_ii.training.regression_models as regression
from app.exploration.machine_learning_ii.custom_types import ModelBuilder
from app.exploration.machine_learning_ii.data_preparation.default import (
    default_feature_builder,
)
from app.exploration.machine_learning_ii.plotting_utils import (
    plot_residuals_to_downloads,
    save_multiclass_confusion_matrices,
)
from app.exploration.machine_learning_ii.training import hybrid_models
from app.exploration.machine_learning_ii.training.helper_classes import (
    PreparedData,
    RegressionResult,
    RegressionResults,
)
from app.exploration.machine_learning_ii.training.hybrid_models import XGBHybridModel
from app.exploration.machine_learning_ii.training.table_results import (
    build_feature_importance_dataframe,
    build_performance_dataframe,
)


def optimize_hybrid_regression_pipeline(
    *,
    df: DataFrame,
    test_season: int,
    n_trials: int = 1,
    scoring_function: Callable[[Series, Series], float] = r2_score,
    get_feature_importance: bool,
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    study: optuna.Study | None = None

    prepared_data = PreparedData(df, test_season, "hybrid")

    if n_trials > 1:
        study = find_best_hybrid_hyperparameters(
            n_trials, prepared_data, model_builder="hybrid"
        )
    pipeline = prepared_data.build_training_pipeline(
        hybrid_models.build_hybrid_model,
        trial=None if study is None else study.best_trial,  # ty:ignore[invalid-argument-type]
    )

    evaluation: RegressionResults = prepared_data.score_validated_pipeline(pipeline)

    plot_residuals_to_downloads(
        pipeline=pipeline,
        prepared_data=prepared_data,
    )

    if get_feature_importance:
        print("evaluating feature importance...")
        feature_importance = prepared_data.get_permutation_feature_importance(
            pipeline=pipeline,
            scoring_function=scoring_function,
        )

    return {
        "best_params": None if study is None else study.best_params,
        "best_value": None if study is None else study.best_value,
        "validation_season": test_season - 1,
        "test_season": test_season,
        "train_mae": evaluation.train.mae,
        "validation_mae": evaluation.validation.mae,
        "test_mae": evaluation.test.mae,
        "train_rmse": evaluation.train.rmse,
        "validation_rmse": evaluation.validation.rmse,
        "test_rmse": evaluation.test.rmse,
        "train_r2": evaluation.train.r2,
        "validation_r2": evaluation.validation.r2,
        "test_r2": evaluation.test.r2,
        "feature_importance": feature_importance if get_feature_importance else None,
        "pipeline": pipeline,
        "model": pipeline.named_steps["model"],
        "preprocessor": pipeline.named_steps["preprocessor"],
        "study": study,
    }


def find_best_hyperparameters(
    n_trials: int,
    prepared_data: PreparedData,
    model_builder: ModelBuilder,
) -> optuna.Study:
    def objective(trial: optuna.Trial) -> float:
        pipeline = prepared_data.build_training_pipeline(
            trial=trial, model_builder=model_builder
        )

        evaluation = prepared_data.score_pipeline(pipeline)

        return evaluation.test.rmse

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PerformanceWarning)
        warnings.simplefilter("ignore", ConvergenceWarning)
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction="minimize")
        study.optimize(
            objective,
            n_trials=n_trials,
            show_progress_bar=True,
        )

    return study


def find_best_hybrid_hyperparameters(
    n_trials: int,
    prepared_data: PreparedData,
    model_builder: ModelBuilder | Literal["hybrid"],
) -> optuna.Study:
    if model_builder == "hybrid":
        model_builder = hybrid_models.build_hybrid_model
        score_pipeline = prepared_data.score_validated_pipeline
    else:
        score_pipeline = prepared_data.score_pipeline

    def objective(trial: optuna.Trial) -> float:
        pipeline = prepared_data.build_training_pipeline(
            trial=trial, model_builder=model_builder
        )

        evaluation = score_pipeline(pipeline)
        return (
            evaluation.test.mse
            if model_builder == "hybrid"
            else evaluation.validation.rmse
        )

    with warnings.catch_warnings():
        # warnings.simplefilter("ignore", PerformanceWarning)
        # warnings.simplefilter("ignore", ConvergenceWarning)
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction="minimize")
        study.optimize(
            objective,
            n_trials=n_trials,
            show_progress_bar=True,
        )

    return study


def main(n_trials: int = 100, feature_importance: bool = False) -> None:
    res: dict[int, dict] = {}
    df_original = default_feature_builder()
    for year in range(2016, 2027):
        df = df_original.copy()
        res[year] = optimize_hybrid_regression_pipeline(
            test_season=year,
            n_trials=n_trials,
            df=df,
            get_feature_importance=False,
        )
        print(res[year]["test_rmse"])

    tables_names: list[tuple[DataFrame, str]] = [
        (build_performance_dataframe(res), "performance")  # ty:ignore[invalid-argument-type]
    ]
    if feature_importance:
        tables_names.append(
            (build_feature_importance_dataframe(res), "feature_importance")  # ty:ignore[invalid-argument-type]
        )
    for table, test_season in tables_names:
        table.to_latex(
            f"documentation/report/tables/xgboost_hybrid_{test_season}.tex",
            index=False,
            escape=True,
            float_format="%.4f",
            column_format="lccccccccc",
        )


if __name__ == "__main__":
    main()
    pass
