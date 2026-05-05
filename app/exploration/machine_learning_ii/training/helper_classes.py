from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import optuna
from joblib import parallel_backend
from pandas import DataFrame, Series, concat
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, r2_score, root_mean_squared_error
from sklearn.pipeline import Pipeline

from app.exploration.machine_learning_ii.custom_types import (
    ModelBuilder,
    PreprocessorBuilder,
)
from app.exploration.machine_learning_ii.data_preparation.basic import (
    get_numeric_and_categorical_columns,
)
from app.exploration.machine_learning_ii.data_preparation.default import (
    build_default_preprocessor,
)
from app.exploration.machine_learning_ii.data_preparation.transformation import (
    inverse_transform_target,
    transform_target,
)
from app.exploration.machine_learning_ii.training.models import build_xgboost_model


class PreparedData:
    def __init__(self, features: DataFrame, test_season: int) -> None:
        self.features = features
        self.test_season = test_season
        self.validation_season = test_season - 1
        train_indeces = self.features["season"] < self.validation_season
        validation_indeces = self.features["season"] == self.validation_season
        test_indeces = self.features["season"] == self.test_season

        self.contract_type = self.features.pop("contract_type")
        self.relative_dollars = self.features.pop("relative_dollars")
        self.transformed_relative_dollars = transform_target(self.relative_dollars)

        self.numeric_columns, self.categorical_columns = (
            get_numeric_and_categorical_columns(self.features)
        )

        self.X_train = self.features[train_indeces]
        self.X_validation = self.features[validation_indeces]
        self.X_test = self.features[test_indeces]
        self.y_train = self.transformed_relative_dollars[train_indeces]
        self.y_validation = self.transformed_relative_dollars[validation_indeces]
        self.y_test = self.transformed_relative_dollars[test_indeces]

    def build_training_pipeline(
        self,
        trial: optuna.Trial | None = None,
        *,
        preprocessor_builder: PreprocessorBuilder = build_default_preprocessor,
        model_builder: ModelBuilder = build_xgboost_model,
    ) -> Pipeline:
        preprocessor = preprocessor_builder(
            self.features,
            self.numeric_columns,
        )
        model = model_builder(trial, 42)

        return Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

    def score_pipeline(
        self, pipeline: Pipeline, use_validation: bool = False
    ) -> EvaluationResult:
        if use_validation:
            X_train, y_train = self.X_train, self.y_train
            X_test, y_test = self.X_validation, self.y_validation
        else:
            X_train, y_train = (
                concat([self.X_train, self.X_validation]),
                concat([self.y_train, self.y_validation]),
            )
            X_test, y_test = self.X_test, self.y_test
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

        train_predictions = inverse_transform_target(
            train_predictions_transformed,
        )
        test_predictions = inverse_transform_target(
            test_predictions_transformed,
        )
        y_train_original = inverse_transform_target(y_train)
        y_test_original = inverse_transform_target(y_test)

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

    def get_permutation_feature_importance(
        self,
        *,
        pipeline: Any,
        scoring_function: Callable[[Series, Series], float],
        n_repeats: int = 10,
        random_state: int = 42,
    ) -> list[tuple[float, str]]:
        def scorer(estimator: Any, X: DataFrame, y: Series) -> float:
            predictions = estimator.predict(X)

            y_series = Series(y, index=X.index)
            prediction_series = Series(predictions, index=X.index)

            y_original = inverse_transform_target(y_series)
            predictions_original = inverse_transform_target(prediction_series)

            return scoring_function(y_original, predictions_original)

        with parallel_backend("threading"):
            result = permutation_importance(
                estimator=pipeline,
                X=self.X_test,
                y=self.y_test,
                scoring=scorer,
                n_repeats=n_repeats,
                random_state=random_state,
                n_jobs=-1,
            )

        return sorted(
            zip(result.importances_mean.tolist(), self.X_test.columns.tolist()),
            key=lambda pair: pair[0],
            reverse=True,
        )


@dataclass(slots=True)
class EvaluationResult:
    train_predictions: Series
    test_predictions: Series
    y_train_original: Series
    y_test_original: Series
    train_mae: float
    test_mae: float
    train_rmse: float
    test_rmse: float
    train_r2: float
    test_r2: float
