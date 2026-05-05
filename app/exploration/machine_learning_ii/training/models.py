import optuna
from sklearn.base import RegressorMixin
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet, Lasso, Ridge
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor


def build_extra_trees_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return ExtraTreesRegressor(
            random_state=random_state,
            n_jobs=-1,
        )

    return ExtraTreesRegressor(
        n_estimators=trial.suggest_int("et_n_estimators", 100, 1000),
        max_depth=trial.suggest_int("et_max_depth", 3, 30),
        min_samples_split=trial.suggest_int("et_min_samples_split", 2, 20),
        min_samples_leaf=trial.suggest_int("et_min_samples_leaf", 1, 10),
        max_features=trial.suggest_float("et_max_features", 0.3, 1.0),
        random_state=random_state,
        n_jobs=-1,
    )


def build_elastic_net_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return ElasticNet(random_state=random_state)

    return ElasticNet(
        alpha=trial.suggest_float("enet_alpha", 1e-4, 10.0, log=True),
        l1_ratio=trial.suggest_float("enet_l1_ratio", 0.0, 1.0),
        random_state=random_state,
        max_iter=10000,
    )


def build_lasso_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return Lasso(random_state=random_state)

    return Lasso(
        alpha=trial.suggest_float("lasso_alpha", 1e-4, 10.0, log=True),
        random_state=random_state,
        max_iter=10000,
    )


def build_ridge_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return Ridge(random_state=random_state)

    return Ridge(
        alpha=trial.suggest_float("ridge_alpha", 1e-4, 100.0, log=True),
        solver=trial.suggest_categorical(
            "ridge_solver",
            ["auto", "svd", "cholesky", "lsqr", "sag", "saga"],
        ),
        random_state=random_state,
    )


def build_knn_model(
    trial: optuna.Trial | None,
    random_state: int,  # unused but kept for consistency
) -> RegressorMixin:
    if trial is None:
        return KNeighborsRegressor()

    return KNeighborsRegressor(
        n_neighbors=trial.suggest_int("knn_n_neighbors", 3, 50),
        weights=trial.suggest_categorical("knn_weights", ["uniform", "distance"]),
        p=trial.suggest_int("knn_p", 1, 2),  # 1=manhattan, 2=euclidean
    )


def build_decision_tree_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return DecisionTreeRegressor(
            random_state=random_state,
        )

    return DecisionTreeRegressor(
        max_depth=trial.suggest_int("dt_max_depth", 2, 30),
        min_samples_split=trial.suggest_int("dt_min_samples_split", 2, 20),
        min_samples_leaf=trial.suggest_int("dt_min_samples_leaf", 1, 10),
        max_features=trial.suggest_float("dt_max_features", 0.3, 1.0),
        random_state=random_state,
    )


def build_random_forest_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return RandomForestRegressor(
            random_state=random_state,
            n_jobs=-1,
        )

    return RandomForestRegressor(
        n_estimators=trial.suggest_int("rf_n_estimators", 100, 1000),
        max_depth=trial.suggest_int("rf_max_depth", 3, 30),
        min_samples_split=trial.suggest_int("rf_min_samples_split", 2, 20),
        min_samples_leaf=trial.suggest_int("rf_min_samples_leaf", 1, 10),
        max_features=trial.suggest_float("rf_max_features", 0.3, 1.0),
        random_state=random_state,
        n_jobs=-1,
    )


def build_xgboost_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> RegressorMixin:
    if trial is None:
        return XGBRegressor(
            objective="reg:squarederror",
            random_state=random_state,
            n_jobs=-1,
        )

    return XGBRegressor(
        n_estimators=trial.suggest_int("n_estimators", 100, 1200),
        max_depth=trial.suggest_int("max_depth", 2, 10),
        learning_rate=trial.suggest_float("learning_rate", 0.005, 0.3, log=True),
        subsample=trial.suggest_float("subsample", 0.5, 1.0),
        colsample_bytree=trial.suggest_float("colsample_bytree", 0.5, 1.0),
        min_child_weight=trial.suggest_int("min_child_weight", 1, 20),
        reg_alpha=trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
        gamma=trial.suggest_float("gamma", 1e-8, 10.0, log=True),
        objective="reg:squarederror",
        random_state=random_state,
        n_jobs=-1,
    )
