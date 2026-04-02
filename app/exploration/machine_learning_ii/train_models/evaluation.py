from collections.abc import Callable
from typing import Any

from pandas import DataFrame, Series
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from app.exploration.machine_learning_ii.data_preparation.transformation import (
    inverse_transform_target,
)
from app.exploration.machine_learning_ii.train_models.helper_classes import (
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
