from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any

import optuna
from pandas import DataFrame, Series
from pandas.errors import PerformanceWarning
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import mean_squared_error, r2_score

from app.exploration.machine_learning_ii.custom_types import ModelBuilder
from app.exploration.machine_learning_ii.data_preparation.default import (
    default_feature_builder,
)
from app.exploration.machine_learning_ii.training.helper_classes import (
    PreparedData,
)
from app.exploration.machine_learning_ii.training.models import (
    build_decision_tree_model,
    build_elastic_net_model,
    build_extra_trees_model,
    build_knn_model,
    build_lasso_model,
    build_random_forest_model,
    build_ridge_model,
    build_xgboost_model,
)
from app.exploration.machine_learning_ii.training.table_results import (
    build_feature_importance_dataframe,
    build_performance_dataframe,
)


def optimize_regression_pipeline(
    *,
    test_season: int,
    random_state: int = 42,
    n_trials: int = 1,
    df: DataFrame,
    model_builder: ModelBuilder = build_xgboost_model,
    scoring_function: Callable[[Series, Series], float] = r2_score,
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    study: optuna.Study | None = None

    prepared_data = PreparedData(df, test_season)

    if n_trials > 1:
        study = find_best_hyperparameters(
            n_trials, prepared_data, model_builder=model_builder
        )
    pipeline = prepared_data.build_training_pipeline(
        None if study is None else study.best_trial,  # ty:ignore[invalid-argument-type]
        model_builder=model_builder,
    )

    evaluation = prepared_data.score_pipeline(pipeline)

    print("evaluating feature importance...")
    feature_importance = prepared_data.get_permutation_feature_importance(
        pipeline=pipeline,
        scoring_function=scoring_function,
        random_state=random_state,
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
        "feature_importance": feature_importance,
        "pipeline": pipeline,
        "model": pipeline.named_steps["model"],
        "preprocessor": pipeline.named_steps["preprocessor"],
        "study": study,
    }


def find_best_hyperparameters(
    n_trials: int, prepared_data: PreparedData, model_builder: ModelBuilder
) -> optuna.Study:
    def objective(trial: optuna.Trial) -> float:
        pipeline = prepared_data.build_training_pipeline(
            trial=trial, model_builder=model_builder
        )

        evaluation = prepared_data.score_pipeline(pipeline)

        return evaluation.test.mse

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


def classification(
    n_trials: int = 30,
    test_season: int = 2026,
) -> None:
    warnings.filterwarnings("error", category=UserWarning)
    res: dict[str, dict] = {}
    df_original = default_feature_builder()
    for name, model in {
        "xgboost": build_xgboost_model,
        "decision_tree": build_decision_tree_model,
        "ridge": build_ridge_model,
        "knn": build_knn_model,
        "elastic_net": build_elastic_net_model,
        "lasso": build_lasso_model,
        "random_forest": build_random_forest_model,
        "extra_trees": build_extra_trees_model,
    }.items():
        df = df_original.copy()
        df = df[df["contract_type"].apply(lambda x: x is None or x != x)]
        print(f"starting {name} ...")
        res[name] = optimize_regression_pipeline(
            test_season=test_season, model_builder=model, n_trials=n_trials, df=df
        )

    for table, name in (
        (build_feature_importance_dataframe(res), "feature_importance"),
        (build_performance_dataframe(res), "performance"),
    ):
        if test_season != 2026:
            name += f"_{test_season}"
        table.to_latex(
            f"documentation/report/tables/{name}.tex",
            index=False,
            escape=True,
            float_format="%.4f",
            column_format="lccccccccc",
        )


def main(
    filter_to_only_mid_contracts: bool = False,
    n_trials: int = 30,
    test_season: int = 2026,
) -> None:
    warnings.filterwarnings("error", category=UserWarning)
    res: dict[str, dict] = {}
    df_original = default_feature_builder()
    for name, model in {
        "xgboost": build_xgboost_model,
        "decision_tree": build_decision_tree_model,
        "ridge": build_ridge_model,
        "knn": build_knn_model,
        "elastic_net": build_elastic_net_model,
        "lasso": build_lasso_model,
        "random_forest": build_random_forest_model,
        "extra_trees": build_extra_trees_model,
    }.items():
        df = df_original.copy()
        if filter_to_only_mid_contracts:
            df = df[df["contract_type"].apply(lambda x: x is None or x != x)]
        print(f"starting {name} ...")
        res[name] = optimize_regression_pipeline(
            test_season=test_season, model_builder=model, n_trials=n_trials, df=df
        )

    for table, name in (
        (build_feature_importance_dataframe(res), "feature_importance"),
        (build_performance_dataframe(res), "performance"),
    ):
        if filter_to_only_mid_contracts:
            name += "_filtered"
        if test_season != 2026:
            name += f"_{test_season}"
        table.to_latex(
            f"documentation/report/tables/{name}.tex",
            index=False,
            escape=True,
            float_format="%.4f",
            column_format="lccccccccc",
        )


if __name__ == "__main__":
    main()
