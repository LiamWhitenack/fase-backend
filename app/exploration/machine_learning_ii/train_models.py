from __future__ import annotations

import warnings
from collections.abc import Callable
from typing import Any

import optuna
from pandas import DataFrame, Series
from pandas.errors import PerformanceWarning
from sklearn.base import ClassifierMixin
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

import app.exploration.machine_learning_ii.training.classification_models as classification
import app.exploration.machine_learning_ii.training.regression_models as regression
from app.exploration.machine_learning_ii.custom_types import ModelBuilder
from app.exploration.machine_learning_ii.data_preparation.default import (
    default_feature_builder,
)
from app.exploration.machine_learning_ii.plotting_utils import (
    plot_residuals_to_downloads,
    save_multiclass_confusion_matrices,
)
from app.exploration.machine_learning_ii.training.helper_classes import (
    ClassificationResults,
    PreparedData,
    RegressionResults,
)
from app.exploration.machine_learning_ii.training.table_results import (
    build_feature_importance_dataframe,
    build_performance_dataframe,
    build_performance_dataframe_classification,
)


def optimize_classification_pipeline(
    *,
    test_season: int,
    random_state: int = 42,
    n_trials: int = 1,
    df: DataFrame,
    model_builder: ModelBuilder,
    scoring_function: Callable[[Series, Series], float] = accuracy_score,
    get_feature_importance: bool,
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    study: optuna.Study | None = None

    prepared_data = PreparedData(df, test_season, mode="classification")

    if n_trials > 1:
        study = find_best_hyperparameters(
            n_trials, prepared_data, model_builder=model_builder
        )

    pipeline = prepared_data.build_training_pipeline(
        None if study is None else study.best_trial,  # ty:ignore[invalid-argument-type]
        model_builder=model_builder,
    )

    evaluation: ClassificationResults = prepared_data.score_pipeline(pipeline)  # ty:ignore[invalid-assignment]

    if get_feature_importance:
        print("evaluating feature importance...")
        feature_importance = prepared_data.get_permutation_feature_importance(
            pipeline=pipeline,
            scoring_function=scoring_function,
            random_state=random_state,
        )

    # save_multiclass_confusion_matrices(
    #     prepared_data=prepared_data,
    #     pipeline=pipeline,
    #     labels=["unsigned", "minimum", "maximum", "between"],
    # )

    return {
        "best_params": None if study is None else study.best_params,
        "best_value": None if study is None else study.best_value,
        "validation_season": test_season - 1,
        "test_season": test_season,
        # classification metrics
        "train_accuracy": evaluation.train.accuracy,
        "validation_accuracy": evaluation.validation.accuracy,
        "test_accuracy": evaluation.test.accuracy,
        "train_log_loss": evaluation.train.log_loss,
        "validation_log_loss": evaluation.validation.log_loss,
        "test_log_loss": evaluation.test.log_loss,
        "train_f1": evaluation.train.f1,
        "validation_f1": evaluation.validation.f1,
        "test_f1": evaluation.test.f1,
        "train_auc": evaluation.train.auc,
        "validation_auc": evaluation.validation.auc,
        "test_auc": evaluation.test.auc,
        "train_precision_weighted": evaluation.train.precision,
        "validation_precision_weighted": evaluation.validation.precision,
        "test_precision_weighted": evaluation.test.precision,
        "train_log_loss": evaluation.train.log_loss,
        "validation_log_loss": evaluation.validation.log_loss,
        "test_log_loss": evaluation.test.log_loss,
        "train_auc": evaluation.train.auc,
        "validation_auc": evaluation.validation.auc,
        "test_auc": evaluation.test.auc,
        "feature_importance": feature_importance if get_feature_importance else None,
        "pipeline": pipeline,
        "model": pipeline.named_steps["model"],
        "preprocessor": pipeline.named_steps["preprocessor"],
        "study": study,
    }


def optimize_regression_pipeline(
    *,
    test_season: int,
    random_state: int = 42,
    n_trials: int = 1,
    df: DataFrame,
    model_builder: ModelBuilder = regression.build_xgboost_model,
    scoring_function: Callable[[Series, Series], float] = r2_score,
    get_feature_importance: bool,
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    study: optuna.Study | None = None

    prepared_data = PreparedData(df, test_season, "regression")

    if n_trials > 1:
        study = find_best_hyperparameters(
            n_trials, prepared_data, model_builder=model_builder
        )
    pipeline = prepared_data.build_training_pipeline(
        None if study is None else study.best_trial,  # ty:ignore[invalid-argument-type]
        model_builder=model_builder,
    )

    evaluation: RegressionResults = prepared_data.score_pipeline(pipeline)  # ty:ignore[invalid-assignment]

    # plot_residuals_to_downloads(
    #     pipeline=pipeline,
    #     prepared_data=prepared_data,
    # )

    if get_feature_importance:
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

        if prepared_data.mode == "classification":
            return evaluation.test.auc  # ty:ignore[possibly-missing-attribute]
        else:
            return evaluation.test.mse  # ty:ignore[possibly-missing-attribute]

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PerformanceWarning)
        warnings.simplefilter("ignore", ConvergenceWarning)
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(
            direction="minimize" if prepared_data.mode == "regression" else "maximize"
        )
        study.optimize(
            objective,
            n_trials=n_trials,
            show_progress_bar=True,
        )

    return study


def classify_contracts(
    n_trials: int = 30, test_season: int = 2026, feature_importance: bool = False
) -> None:
    # warnings.filterwarnings("error", category=UserWarning)
    res: dict[str, dict] = {}
    df_original = default_feature_builder()
    for name, model in {
        # "Decision Tree": classification.build_decision_tree_model,
        # "Extra Trees": classification.build_extra_trees_model,
        # "KNN": classification.build_knn_model,
        # "Random Forest": classification.build_random_forest_model,
        "XGBoost": classification.build_xgboost_model,
        # "logistic_regression": classification.build_logistic_regression_model,
    }.items():
        df = df_original.copy()
        print(f"starting {name} ...")
        res[name] = optimize_classification_pipeline(
            test_season=test_season,
            model_builder=model,
            n_trials=n_trials,
            df=df,
            get_feature_importance=feature_importance,
        )

    tables_names: list[tuple[DataFrame, str]] = [
        (build_performance_dataframe_classification(res), "performance")
    ]
    if feature_importance:
        tables_names.append(
            (build_feature_importance_dataframe(res), "feature_importance")
        )

    for table, name in tables_names:
        if test_season != 2026:
            name += f"_{test_season}"
        table.to_latex(
            f"documentation/report/tables/{name}_classification.tex",
            escape=True,
            float_format="%.4f",
            column_format="lccccccccc",
        )


def main(
    filter_to_only_mid_contracts: bool = False,
    n_trials: int = 30,
    test_season: int = 2026,
    feature_importance: bool = False,
) -> None:
    res: dict[str, dict] = {}
    df_original = default_feature_builder()
    for name, model in {
        # "Decision Tree": regression.build_decision_tree_model,
        # "Elastic Net": regression.build_elastic_net_model,
        # "Extra Trees": regression.build_extra_trees_model,
        # "KNN": regression.build_knn_model,
        # "Lasso": regression.build_lasso_model,
        # "Random Forest": regression.build_random_forest_model,
        # "Ridge": regression.build_ridge_model,
        "XGBoost": regression.build_xgboost_model,
    }.items():
        df = df_original.copy()
        if filter_to_only_mid_contracts:
            df = df[df["contract_type"].apply(lambda x: x is None or x != x)]
        print(f"starting {name} ...")
        res[name] = optimize_regression_pipeline(
            test_season=test_season,
            model_builder=model,
            n_trials=n_trials,
            df=df,
            get_feature_importance=feature_importance,
        )

    tables_names: list[tuple[DataFrame, str]] = [
        (build_performance_dataframe(res), "performance")
    ]
    if feature_importance:
        tables_names.append(
            (build_feature_importance_dataframe(res), "feature_importance")
        )
    for table, name in tables_names:
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
    main(n_trials=5)
    classify_contracts(n_trials=5)
