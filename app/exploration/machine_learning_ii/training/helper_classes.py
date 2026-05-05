from __future__ import annotations

import warnings
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, overload
from warnings import catch_warnings

import optuna
from joblib import parallel_backend
from numpy import ndarray
from pandas import DataFrame, Series, concat
from pandas.errors import PerformanceWarning
from sklearn.exceptions import ConvergenceWarning
from sklearn.exceptions import DataConversionWarning as PerformanceWarning
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    root_mean_squared_error,
)
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
from app.exploration.machine_learning_ii.training.regression_models import (
    build_xgboost_model,
)


class PreparedData:
    def __init__(
        self,
        features: DataFrame,
        test_season: int,
        mode: Literal["regression", "classification"],
    ) -> None:
        self.features = features
        self.test_season = test_season
        self.validation_season = test_season - 1
        self.mode = mode
        train_indeces = self.features["season"] < self.validation_season
        validation_indeces = self.features["season"] == self.validation_season
        test_indeces = self.features["season"] == self.test_season

        self.contract_type = self.features.pop("contract_type")
        self.relative_dollars = self.features.pop("relative_dollars")
        self.transformed_relative_dollars = transform_target(self.relative_dollars)

        self.numeric_columns, self.categorical_columns = (
            get_numeric_and_categorical_columns(self.features)
        )

        y = (
            self.transformed_relative_dollars
            if mode == "regression"
            else self.encode_labels(self.contract_type)
        )

        self.X_train = self.features[train_indeces]
        self.X_validation = self.features[validation_indeces]
        self.X_test = self.features[test_indeces]
        self.y_train = y[train_indeces]
        self.y_validation = y[validation_indeces]
        self.y_test = y[test_indeces]

    def encode_labels(self, y: Series) -> Series:
        to_numeric = {"unsigned": 0, "rookie": 0, "minimum": 1, "maximum": 2}
        return y.apply(lambda c: to_numeric.get(c, 3))

    def decode_labels(self, y: Series) -> Series:
        to_string = {0: "unsigned", 1: "minimum", 2: "maximum", 3: "between"}
        return y.apply(lambda c: to_string.get(c, 3))

    def build_training_pipeline(
        self,
        trial: optuna.Trial | None = None,
        *,
        model_builder: ModelBuilder,
        preprocessor_builder: PreprocessorBuilder = build_default_preprocessor,
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
        self,
        pipeline: Pipeline,
    ) -> RegressionResults | ClassificationResults:
        train = TrainTest(
            self.X_train,
            self.y_train,
            self.X_train,
            self.y_train,
        )

        validation = TrainTest(
            concat([self.X_train, self.X_validation]),
            concat([self.y_train, self.y_validation]),
            self.X_validation,
            self.y_validation,
        )

        test = TrainTest(
            self.X_train,
            self.y_train,
            self.X_test,
            self.y_test,
        )

        results = []

        for data in (train, validation, test):
            if data is not validation:
                with catch_warnings():
                    warnings.simplefilter("ignore", PerformanceWarning)
                    warnings.simplefilter("ignore", ConvergenceWarning)
                    pipeline.fit(data.X_train, data.y_train)

            predictions_raw = Series(
                pipeline.predict(data.X_test),
                index=data.y_test.index,
                name=data.y_test.name,
            )

            if self.mode == "regression":
                predictions = inverse_transform_target(predictions_raw)
                actual = inverse_transform_target(data.y_test)

                results.append(RegressionResult(predictions, actual))

            else:
                probabilities = pipeline.predict_proba(data.X_test)

                results.append(
                    ClassificationResult(
                        actual=data.y_test,
                        predictions=predictions_raw,
                        probabilities=probabilities,
                    )
                )

        if self.mode == "regression":
            return RegressionResults(*results)

        return ClassificationResults(*results)

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

            if self.mode == "regression":
                y_original = inverse_transform_target(y_series)
                predictions_original = inverse_transform_target(prediction_series)
            else:
                y_original = y_series
                predictions_original = prediction_series

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


@dataclass
class TrainTest:
    X_train: DataFrame
    y_train: Series
    X_test: DataFrame
    y_test: Series


@dataclass
class RegressionResult:
    predictions: Series
    actual: Series

    def __post_init__(self) -> None:
        self.mae = mean_absolute_error(self.predictions, self.actual)
        self.mse = mean_squared_error(self.predictions, self.actual)
        self.rmse = root_mean_squared_error(self.predictions, self.actual)
        self.r2 = r2_score(self.predictions, self.actual)


@dataclass
class RegressionResults:
    train: RegressionResult
    validation: RegressionResult
    test: RegressionResult


@dataclass
class ClassificationResult:
    actual: Series
    predictions: Series
    probabilities: ndarray

    def __post_init__(self) -> None:
        self.accuracy = accuracy_score(self.actual, self.predictions)

        self.f1 = f1_score(
            self.actual,
            self.predictions,
            average="weighted",
        )

        self.precision = precision_score(
            self.actual,
            self.predictions,
            average="weighted",
            zero_division=0,
        )

        self.recall_weighted = recall_score(
            self.actual,
            self.predictions,
            average="weighted",
            zero_division=0,
        )

        if self.probabilities is not None:
            self.log_loss = log_loss(self.actual, self.probabilities)

            self.auc = roc_auc_score(
                self.actual,
                self.probabilities,
                multi_class="ovr",
                average="weighted",
            )


@dataclass
class ClassificationResults:
    train: ClassificationResult
    validation: ClassificationResult
    test: ClassificationResult
