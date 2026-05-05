import optuna
from sklearn.base import ClassifierMixin
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier


def build_extra_trees_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> ClassifierMixin:
    if trial is None:
        return ExtraTreesClassifier(
            random_state=random_state,
            n_jobs=-1,
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 100, 400),
            max_depth=trial.suggest_int("max_depth", 3, 15),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 10),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 5),
            max_features=trial.suggest_float("max_features", 0.5, 1.0),
        )

    return ExtraTreesClassifier(
        **params,
        random_state=random_state,
        n_jobs=-1,
    )


def build_logistic_regression_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> ClassifierMixin:
    if trial is None:
        return LogisticRegression(
            random_state=random_state,
            max_iter=10000,
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        penalty = trial.suggest_categorical("penalty", ["l1", "l2", "elasticnet"])
        solver = "saga"  # required for elasticnet/l1 support

        params = dict(
            C=trial.suggest_float("C", 1e-3, 10.0, log=True),
            penalty=trial.suggest_categorical("penalty", ["l1", "l2"]),
            solver="liblinear" if penalty == "l1" else "lbfgs",
        )

        # elasticnet requires l1_ratio
        if penalty == "elasticnet":
            params["l1_ratio"] = trial.suggest_float("l1_ratio", 0.0, 1.0)

    return LogisticRegression(
        **params,
        random_state=random_state,
        max_iter=10000,
    )


def build_knn_model(
    trial: optuna.Trial | None,
    random_state: int,  # unused but kept for consistency
) -> ClassifierMixin:
    if trial is None:
        return KNeighborsClassifier()

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_neighbors=trial.suggest_int("n_neighbors", 3, 25),
            weights=trial.suggest_categorical("weights", ["uniform", "distance"]),
            p=trial.suggest_int("p", 1, 2),
        )

    return KNeighborsClassifier(
        **params,
    )


def build_decision_tree_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> ClassifierMixin:
    if trial is None:
        return DecisionTreeClassifier(
            random_state=random_state,
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            max_depth=trial.suggest_int("max_depth", 3, 12),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 10),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 5),
            max_features=trial.suggest_float("max_features", 0.5, 1.0),
        )

    return DecisionTreeClassifier(
        **params,
        random_state=random_state,
    )


def build_random_forest_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> ClassifierMixin:
    if trial is None:
        return RandomForestClassifier(
            random_state=random_state,
            n_jobs=-1,
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 100, 300),
            max_depth=trial.suggest_int("max_depth", 3, 15),
            min_samples_split=trial.suggest_int("min_samples_split", 2, 10),
            min_samples_leaf=trial.suggest_int("min_samples_leaf", 1, 5),
            max_features=trial.suggest_float("max_features", 0.5, 1.0),
        )

    return RandomForestClassifier(
        **params,
        random_state=random_state,
        n_jobs=-1,
    )


def build_xgboost_model(
    trial: optuna.Trial | None,
    random_state: int,
) -> ClassifierMixin:
    if trial is None:
        return XGBClassifier(
            objective="binary:logistic",
            random_state=random_state,
            n_jobs=-1,
            eval_metric="logloss",
        )

    if hasattr(trial, "state"):
        params = trial.params
    else:
        params = dict(
            n_estimators=trial.suggest_int("n_estimators", 100, 400),
            max_depth=trial.suggest_int("max_depth", 3, 8),
            learning_rate=trial.suggest_float("learning_rate", 0.03, 0.2, log=True),
            subsample=trial.suggest_float("subsample", 0.7, 1.0),
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.7, 1.0),
            min_child_weight=trial.suggest_int("min_child_weight", 1, 10),
        )

    return XGBClassifier(
        **params,
        objective="binary:logistic",
        random_state=random_state,
        n_jobs=-1,
        eval_metric="logloss",
    )
