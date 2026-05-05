from collections.abc import Callable

import optuna
from pandas import DataFrame
from sklearn.base import ClassifierMixin, RegressorMixin
from sklearn.compose import ColumnTransformer

ModelBuilder = Callable[[optuna.Trial | None, int], RegressorMixin | ClassifierMixin]
PreprocessorBuilder = Callable[[DataFrame, list[str]], ColumnTransformer]
