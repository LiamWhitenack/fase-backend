from __future__ import annotations

from collections.abc import Callable
from typing import Any

import optuna
from pandas import DataFrame, Series
from sklearn.metrics import r2_score

from app.exploration.machine_learning_ii.data_preparation.basic import PreparedData
from app.exploration.machine_learning_ii.data_preparation.default import (
    build_default_preprocessor,
    prepare_training_data,
)
from app.exploration.machine_learning_ii.data_preparation.transformation import (
    inverse_transform_target,
    transform_target,
)
from app.exploration.machine_learning_ii.train_models.evaluation import score_pipeline
from app.exploration.machine_learning_ii.train_models.helper_classes import SplitData
from app.exploration.machine_learning_ii.train_models.models import build_xgboost_model
from app.exploration.machine_learning_ii.train_models.pipeline import (
    ModelBuilder,
    PreprocessorBuilder,
    build_training_pipeline,
)
from app.exploration.machine_learning_ii.train_models.split_training_data import (
    split_training_data,
)


def _get_validation_season(
    features: DataFrame,
    *,
    test_season: int,
    validation_season: int | None,
) -> int:
    available_train_seasons = sorted(
        season
        for season in features["season"].dropna().unique().tolist()
        if season < test_season
    )

    if not available_train_seasons:
        raise ValueError("No seasons exist before test_season.")

    if validation_season is not None:
        if validation_season not in available_train_seasons:
            raise ValueError(
                "validation_season must be present in the data and earlier than test_season."
            )
        return validation_season

    if len(available_train_seasons) < 2:
        raise ValueError(
            "At least two seasons before test_season are required: "
            "one for inner training and one for validation."
        )

    return available_train_seasons[-1]


def optimize_regression_pipeline(
    *,
    test_season: int,
    validation_season: int | None = None,
    random_state: int = 42,
    n_trials: int = 1,
    target_column: str = "relative_dollars",
    feature_builder: Callable[[], DataFrame] | None = None,
    target_transform: Callable[[Series], Series] = transform_target,
    inverse_target_transform: Callable[[Series], Series] = inverse_transform_target,
    preprocessor_builder: PreprocessorBuilder = build_default_preprocessor,
    model_builder: ModelBuilder = build_xgboost_model,
    scoring_function: Callable[[Series, Series], float] = r2_score,
    study_direction: str = "maximize",
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    prepared_data = prepare_training_data(
        target_column=target_column,
        feature_builder=feature_builder,
        target_transform=target_transform,
    )

    if "season" not in prepared_data.features.columns:
        raise ValueError("prepared_data.features must contain a 'season' column.")

    outer_split = split_training_data(
        prepared_data,
        test_season=test_season,
    )

    chosen_validation_season = _get_validation_season(
        prepared_data.features,
        test_season=test_season,
        validation_season=validation_season,
    )

    inner_train_mask = outer_split.X_train["season"] < chosen_validation_season
    inner_valid_mask = outer_split.X_train["season"] == chosen_validation_season

    X_inner_train = outer_split.X_train.loc[inner_train_mask]
    y_inner_train = outer_split.y_train.loc[inner_train_mask]
    X_inner_valid = outer_split.X_train.loc[inner_valid_mask]
    y_inner_valid = outer_split.y_train.loc[inner_valid_mask]

    if X_inner_train.empty:
        raise ValueError(
            "Inner training set is empty. Choose a later test_season or validation_season."
        )

    if X_inner_valid.empty:
        raise ValueError(
            "Validation set is empty. The chosen validation_season has no rows."
        )

    def build_pipeline(trial: optuna.Trial | None) -> Any:
        return build_training_pipeline(
            trial=trial,
            features=outer_split.X_train,
            numeric_columns=prepared_data.numeric_columns,
            categorical_columns=prepared_data.categorical_columns,
            random_state=random_state,
            preprocessor_builder=preprocessor_builder,
            model_builder=model_builder,
        )

    if n_trials == 1:
        pipeline = build_pipeline(trial=None)

        # Optional sanity fit on inner train/validation so we do not touch test_season
        _ = score_pipeline(
            pipeline,
            X_train=X_inner_train,
            X_test=X_inner_valid,
            y_train=y_inner_train,
            y_test=y_inner_valid,
            inverse_target_transform=inverse_target_transform,
        )

        final_pipeline = build_pipeline(trial=None)

        evaluation = score_pipeline(
            final_pipeline,
            X_train=outer_split.X_train,
            X_test=outer_split.X_test,
            y_train=outer_split.y_train,
            y_test=outer_split.y_test,
            inverse_target_transform=inverse_target_transform,
        )

        return {
            "best_params": None,
            "best_value": scoring_function(
                evaluation.y_test_original,
                evaluation.test_predictions,
            ),
            "validation_season": chosen_validation_season,
            "test_season": test_season,
            "train_mae": evaluation.train_mae,
            "test_mae": evaluation.test_mae,
            "train_rmse": evaluation.train_rmse,
            "test_rmse": evaluation.test_rmse,
            "train_r2": evaluation.train_r2,
            "test_r2": evaluation.test_r2,
            "pipeline": final_pipeline,
            "model": final_pipeline.named_steps["model"],
            "preprocessor": final_pipeline.named_steps["preprocessor"],
            "study": None,
        }

    def objective(trial: optuna.Trial) -> float:
        pipeline = build_pipeline(trial=trial)

        evaluation = score_pipeline(
            pipeline,
            X_train=X_inner_train,
            X_test=X_inner_valid,
            y_train=y_inner_train,
            y_test=y_inner_valid,
            inverse_target_transform=inverse_target_transform,
        )

        return scoring_function(
            evaluation.y_test_original,
            evaluation.test_predictions,
        )

    study = optuna.create_study(direction=study_direction)
    study.optimize(objective, n_trials=n_trials)

    best_pipeline = build_pipeline(trial=study.best_trial)

    evaluation = score_pipeline(
        best_pipeline,
        X_train=outer_split.X_train,
        X_test=outer_split.X_test,
        y_train=outer_split.y_train,
        y_test=outer_split.y_test,
        inverse_target_transform=inverse_target_transform,
    )

    return {
        "best_params": study.best_params,
        "best_value": study.best_value,
        "validation_season": chosen_validation_season,
        "test_season": test_season,
        "train_mae": evaluation.train_mae,
        "test_mae": evaluation.test_mae,
        "train_rmse": evaluation.train_rmse,
        "test_rmse": evaluation.test_rmse,
        "train_r2": evaluation.train_r2,
        "test_r2": evaluation.test_r2,
        "pipeline": best_pipeline,
        "model": best_pipeline.named_steps["model"],
        "preprocessor": best_pipeline.named_steps["preprocessor"],
        "study": study,
    }


if __name__ == "__main__":
    optimize_regression_pipeline(test_season=2026)
