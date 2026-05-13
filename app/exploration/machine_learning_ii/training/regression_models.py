from typing import Any

import optuna
from sklearn.base import RegressorMixin
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor


def build_extra_trees_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return ExtraTreesRegressor(
            n_jobs=-1,
        )
    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 100, 1000),
            max_depth=trial.suggest_int("max_depth", 3, 30),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            max_features=trial.suggest_float("max_features", 0.3, 1.0),
        )

    return ExtraTreesRegressor(
        **params,
        n_jobs=-1,
        random_state=42,
    )


def build_elastic_net_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return ElasticNet()

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            alpha=trial.suggest_float("alpha", 1e-4, 10.0, log=True),
            l1_ratio=trial.suggest_float("l1_ratio", 0.0, 1.0),
        )
    return ElasticNet(
        **params,
        max_iter=10000,
        random_state=42,
    )


def build_lasso_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return Lasso()

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            alpha=trial.suggest_float("alpha", 1e-4, 10.0, log=True),
        )
    return Lasso(
        **params,
        max_iter=10000,
        random_state=42,
    )


def build_ridge_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return Ridge()

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            alpha=trial.suggest_float("alpha", 1e-4, 100.0, log=True),
            solver=trial.suggest_categorical(
                "solver",
                ["auto", "svd", "cholesky", "lsqr", "sag", "saga"],
            ),
        )
    return Ridge(
        **params,
        random_state=42,
    )


def build_knn_model(
    trial: optuna.Trial | None,
    # unused but kept for consistency
) -> RegressorMixin:
    if trial is None:
        return KNeighborsRegressor()

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_neighbors=trial.suggest_int("n_neighbors", 3, 50),
            weights=trial.suggest_categorical("weights", ["uniform", "distance"]),
            p=trial.suggest_int("p", 1, 2),  # 1=manhattan, 2=euclidean
        )
    return KNeighborsRegressor(
        **params,
    )


def build_decision_tree_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return DecisionTreeRegressor()

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            max_depth=trial.suggest_int("max_depth", 2, 30),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            max_features=trial.suggest_float("max_features", 0.3, 1.0),
        )
    return DecisionTreeRegressor(
        **params,
        random_state=42,
    )


def build_random_forest_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return RandomForestRegressor(
            n_jobs=-1,
            random_state=42,
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 100, 1000),
            max_depth=trial.suggest_int("max_depth", 3, 30),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 20),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 10),
            max_features=trial.suggest_float("max_features", 0.3, 1.0),
        )
    return RandomForestRegressor(
        **params,
        n_jobs=-1,
        random_state=42,
    )


def build_xgboost_model(
    trial: optuna.Trial | None,
) -> RegressorMixin:
    if trial is None:
        return XGBRegressor(
            objective="reg:squarederror",
            n_jobs=-1,
            random_state=42,
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 300, 900),
            # allow a bit more complexity back
            max_depth=trial.suggest_int("max_depth", 4, 8),
            # keep improved but slightly wider
            learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
            # still stochastic, but less restrictive
            subsample=trial.suggest_float("subsample", 0.7, 1.0),
            # IMPORTANT: loosen this a bit
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 0.9),
            # allow smaller splits again
            min_child_weight=trial.suggest_int("min_child_weight", 1, 8),
            # keep regularization but allow near-zero
            reg_alpha=trial.suggest_float("reg_alpha", 1e-6, 1.0, log=True),
            reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 5.0, log=True),
            # same idea
            gamma=trial.suggest_float("gamma", 1e-6, 3.0, log=True),
        )

    return XGBRegressor(
        **params,
        objective="reg:squarederror",
        n_jobs=-1,
        early_stopping_rounds=50,
        random_state=42,
    )


def build_xgboost_model_params(
    trial: optuna.Trial | None,
) -> dict[str, Any]:
    if trial is None:
        return dict(
            objective="reg:squarederror",
            n_jobs=-1,
            random_state=42,
        )
    else:
        params = dict(
            # n_estimators=trial.suggest_int("n_estimators", 300, 900),
            # allow a bit more complexity back
            max_depth=trial.suggest_int("regression_max_depth", 4, 8),
            # keep improved but slightly wider
            learning_rate=trial.suggest_float(
                "regression_learning_rate", 0.01, 0.2, log=True
            ),
            # still stochastic, but less restrictive
            subsample=trial.suggest_float("regression_subsample", 0.7, 1.0),
            # IMPORTANT: loosen this a bit
            colsample_bytree=trial.suggest_float(
                "regression_colsample_bytree", 0.5, 0.9
            ),
            # allow smaller splits again
            min_child_weight=trial.suggest_int("regression_min_child_weight", 1, 8),
            # keep regularization but allow near-zero
            reg_alpha=trial.suggest_float("regression_reg_alpha", 1e-6, 1.0, log=True),
            reg_lambda=trial.suggest_float(
                "regression_reg_lambda", 1e-3, 5.0, log=True
            ),
            # same idea
            gamma=trial.suggest_float("regression_gamma", 1e-6, 3.0, log=True),
            # early_stopping_rounds=trial.suggest_int("early_stopping_rounds", 5, 75),
        )

    return dict(
        **params,
        objective="reg:squarederror",
        n_jobs=-1,
        random_state=42,
    )
