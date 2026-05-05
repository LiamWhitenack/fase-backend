from collections.abc import Callable

import optuna
from pandas import DataFrame
from sklearn.base import RegressorMixin
from sklearn.compose import ColumnTransformer

ModelBuilder = Callable[[optuna.Trial | None, int], RegressorMixin]
PreprocessorBuilder = Callable[[DataFrame, list[str]], ColumnTransformer]
