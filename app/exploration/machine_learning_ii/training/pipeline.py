from collections.abc import Callable

import optuna
from pandas import DataFrame
from sklearn.base import RegressorMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from app.exploration.machine_learning_ii.data_preparation.default import (
    build_default_preprocessor,
)
from app.exploration.machine_learning_ii.training.models import build_xgboost_model


def build_training_pipeline(
    *,
    trial: optuna.Trial | None,
    features: DataFrame,
    numeric_columns: list[str],
    categorical_columns: list[str],
    random_state: int,
    preprocessor_builder: PreprocessorBuilder = build_default_preprocessor,
    model_builder: ModelBuilder = build_xgboost_model,
) -> Pipeline:
    preprocessor = preprocessor_builder(
        features,
        numeric_columns,
    )
    model = model_builder(trial, random_state)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


PreprocessorBuilder = Callable[[DataFrame, list[str]], ColumnTransformer]
ModelBuilder = Callable[[optuna.Trial | None, int], RegressorMixin]
