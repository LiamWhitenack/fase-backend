from collections.abc import Callable
from typing import Any

import optuna
from pandas import DataFrame, Series
from sklearn.metrics import accuracy_score

from app.exploration.machine_learning_ii.custom_types import ModelBuilder
from app.exploration.machine_learning_ii.train_models import find_best_hyperparameters
from app.exploration.machine_learning_ii.training.helper_classes import (
    ClassificationResults,
    PreparedData,
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
