from dataclasses import dataclass
from typing import Any

from pandas import DataFrame, Series


@dataclass(slots=True)
class PreparedData:
    features: DataFrame
    target: Series
    numeric_columns: list[str]
    categorical_columns: list[str]


@dataclass(slots=True)
class SplitData:
    X_train: DataFrame
    X_test: DataFrame
    y_train: Series
    y_test: Series


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
