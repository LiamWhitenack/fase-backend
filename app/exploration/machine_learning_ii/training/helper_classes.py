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
from app.exploration.machine_learning_ii.training import hybrid_models
from app.exploration.machine_learning_ii.training.hybrid_models import XGBHybridModel
from app.exploration.machine_learning_ii.training.regression_models import (
    build_xgboost_model,
)


class PreparedData:
    def __init__(
        self,
        features: DataFrame,
        test_season: int,
        mode: Literal["regression", "classification", "hybrid"],
    ) -> None:
        self.features = features
        self.test_season = test_season
        self.validation_season = test_season - 1
        self.mode = mode
        train_indeces = self.features["season"] < self.validation_season
        validation_indeces = self.features["season"] == self.validation_season
        test_indeces = self.features["season"] == self.test_season

        self.features["validation"] = validation_indeces

        self.contract_type = self.features["contract_type"]
        self.relative_dollars = self.features.pop("relative_dollars")
        self.transformed_relative_dollars = transform_target(self.relative_dollars)

        self.numeric_columns, self.categorical_columns = (
            get_numeric_and_categorical_columns(self.features)
        )

        self.encooded_labels = self.encode_labels(self.contract_type)
        self.X_train = self.features[train_indeces]
        self.X_validation = self.features[validation_indeces]
        self.X_test = self.features[test_indeces]
        self.y_train = self.transformed_relative_dollars[train_indeces]
        self.y_validation = self.transformed_relative_dollars[validation_indeces]
        self.y_test = self.transformed_relative_dollars[test_indeces]
        self.labels_train = self.encooded_labels[train_indeces]
        self.labels_validation = self.encooded_labels[validation_indeces]
        self.labels_test = self.encooded_labels[test_indeces]

    @property
    def train(self) -> tuple[DataFrame, Series]:
        return self.X_train, self.y_train

    @property
    def validation(self) -> tuple[DataFrame, Series]:
        return self.X_validation, self.y_validation

    @property
    def test(self) -> tuple[DataFrame, Series]:
        return self.X_test, self.y_test

    def encode_labels(self, y: Series) -> Series:
        to_numeric = {"unsigned": 0, "rookie": 0, "minimum": 1, "maximum": 3}
        return y.apply(lambda c: to_numeric.get(c, 2))

    def decode_labels(self, y: Series) -> Series:
        to_string = {0: "unsigned", 1: "minimum", 2: "between", 3: "maximum"}
        return Series([to_string[round(val)] for val in y])

    def build_training_pipeline(
        self,
        model_builder: ModelBuilder,
        preprocessor_builder: PreprocessorBuilder = build_default_preprocessor,
        trial: optuna.Trial | None = None,
    ) -> Pipeline:
        features = self.features.copy()
        if self.mode != "hybrid":
            features = features.drop(columns=["validation", "contract_type"])
        steps = [
            (
                "preprocessor",
                preprocessor_builder(
                    features,
                    self.numeric_columns,
                ),
            ),
            ("model", model_builder(trial)),
        ]

        return Pipeline(steps=steps)

    def score_pipeline(
        self, pipeline: Pipeline, use_validation_in_fit: bool = False
    ) -> RegressionResults:
        train = TrainTest(
            self.X_train,
            self.y_train,
            self.X_train,
            self.y_train,
        )

        validation = TrainTest(
            self.X_train,
            self.y_train,
            self.X_validation,
            self.y_validation,
        )

        test = TrainTest(
            concat([self.X_train, self.X_validation]),
            concat([self.y_train, self.y_validation]),
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

        return RegressionResults(*results)

    def score_validated_pipeline(
        self, pipeline: Pipeline, hybrid: bool = True
    ) -> RegressionResults:
        X_train, X_validation, X_test = self.X_train, self.X_validation, self.X_test
        if hybrid:
            X_train.loc[:, "contract_type"] = self.labels_train
            X_validation.loc[:, "contract_type"] = self.labels_validation
            X_test.loc[:, "contract_type"] = self.labels_test
            X_train.loc[:, "validation"] = False
            X_validation.loc[:, "validation"] = True
        split = TrainTest(
            concat([X_train, X_validation]),
            concat([self.y_train, self.y_validation]),
            X_test,
            self.y_test,
        )

        with catch_warnings():
            warnings.simplefilter("ignore", PerformanceWarning)
            warnings.simplefilter("ignore", ConvergenceWarning)
            pipeline.fit(split.X_train, split.y_train)

        def transformed_predictions(X: DataFrame, y: Series) -> Series:
            return Series(
                pipeline.predict(X),
                index=y.index,
                name=y.name,
            )

        return RegressionResults(
            *[
                RegressionResult(
                    transformed_predictions(X, y),
                    y,
                )
                for X, y in (self.train, self.validation, self.test)
            ]
        )

    def get_permutation_feature_importance(
        self,
        *,
        pipeline: Any,
        scoring_function: Callable[[Series, Series], float],
        n_repeats: int = 10,
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
                random_state=42,
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
        self.mae = mean_absolute_error(
            inverse_transform_target(self.predictions),
            inverse_transform_target(self.actual),
        )
        self.mse = mean_squared_error(
            inverse_transform_target(self.predictions),
            inverse_transform_target(self.actual),
        )
        self.rmse = root_mean_squared_error(
            inverse_transform_target(self.predictions),
            inverse_transform_target(self.actual),
        )
        self.r2 = r2_score(
            inverse_transform_target(self.predictions),
            inverse_transform_target(self.actual),
        )


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
