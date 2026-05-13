from collections.abc import Callable
from typing import Any

import optuna
from pandas import DataFrame
from sklearn.base import ClassifierMixin, RegressorMixin
from sklearn.compose import ColumnTransformer
from xgboost import XGBClassifier, XGBRegressor

ModelBuilder = Callable[[optuna.Trial | None], RegressorMixin | ClassifierMixin]
XGBClassifierParams = Callable[[optuna.Trial | None], dict[str, Any]]
XGBRegressorParams = Callable[[optuna.Trial | None], dict[str, Any]]
PreprocessorBuilder = Callable[[DataFrame, list[str]], ColumnTransformer]
