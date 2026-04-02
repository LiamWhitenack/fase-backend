import optuna
from sklearn.base import RegressorMixin
from xgboost import XGBRegressor


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
