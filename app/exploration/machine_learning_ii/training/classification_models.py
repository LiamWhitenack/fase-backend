from typing import Any

import optuna
from sklearn.base import ClassifierMixin
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier


def build_extra_trees_model(
    trial: optuna.Trial | None,
) -> ClassifierMixin:
    if trial is None:
        return ExtraTreesClassifier(
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
        n_jobs=-1,
    )


def build_logistic_regression_model(
    trial: optuna.Trial | None,
) -> ClassifierMixin:
    if trial is None:
        return LogisticRegression(
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
        max_iter=10000,
    )


def build_knn_model(
    trial: optuna.Trial | None,
    # unused but kept for consistency
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
) -> ClassifierMixin:
    if trial is None:
        return DecisionTreeClassifier()

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
    )


def build_random_forest_model(
    trial: optuna.Trial | None,
) -> ClassifierMixin:
    if trial is None:
        return RandomForestClassifier(
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
        n_jobs=-1,
    )


def build_xgboost_model(
    trial: optuna.Trial | None,
) -> ClassifierMixin:
    if trial is None:
        return XGBClassifier(
            n_jobs=-1,
        )
    params = dict(
        # Slightly higher upper bound; classification often benefits from more rounds
        n_estimators=trial.suggest_int("classification_n_estimators", 200, 1200),
        # Keep trees controlled
        max_depth=trial.suggest_int("classification_max_depth", 3, 8),
        # Slightly wider but still safe
        learning_rate=trial.suggest_float(
            "classification_learning_rate", 0.02, 0.15, log=True
        ),
        # Encourage stochasticity
        subsample=trial.suggest_float("classification_subsample", 0.6, 0.9),
        # KEY: much more aggressive feature subsampling
        colsample_bytree=trial.suggest_float(
            "classification_colsample_bytree", 0.3, 0.7
        ),
        # Avoid splits on tiny one-hot groups
        min_child_weight=trial.suggest_int("classification_min_child_weight", 3, 8),
        # Add regularization (missing in your version)
        reg_alpha=trial.suggest_float("classification_reg_alpha", 1e-4, 1.0, log=True),
        reg_lambda=trial.suggest_float(
            "classification_reg_lambda", 1e-3, 5.0, log=True
        ),
        # Optional but useful for classification boundaries
        gamma=trial.suggest_float("classification_gamma", 1e-4, 3.0, log=True),
    )

    return XGBClassifier(
        **params,
        n_jobs=-1,
    )


def build_xgboost_model_params(
    trial: optuna.Trial | None,
) -> dict[str, Any]:
    if trial is None:
        params = {}
    else:
        params = {}
        dict(
            # Slightly higher upper bound; classification often benefits from more rounds
            # n_estimators=trial.suggest_int("n_estimators", 200, 1200),
            # Keep trees controlled
            max_depth=trial.suggest_int("max_depth", 3, 8),
            # Slightly wider but still safe
            learning_rate=trial.suggest_float("learning_rate", 0.02, 0.15, log=True),
            # Encourage stochasticity
            subsample=trial.suggest_float("subsample", 0.6, 0.9),
            # KEY: much more aggressive feature subsampling
            colsample_bytree=trial.suggest_float("colsample_bytree", 0.3, 0.7),
            # Avoid splits on tiny one-hot groups
            min_child_weight=trial.suggest_int("min_child_weight", 3, 8),
            # Add regularization (missing in your version)
            reg_alpha=trial.suggest_float("reg_alpha", 1e-4, 1.0, log=True),
            reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 5.0, log=True),
            # Optional but useful for classification boundaries
            gamma=trial.suggest_float("gamma", 1e-4, 3.0, log=True),
            # early_stopping_rounds=trial.suggest_int("early_stopping_rounds", 5, 75),
        )

    return dict(
        **params,
        n_jobs=-1,
        random_state=42,
        objective="multi:softprob",
        num_class=4,
        eval_metric="mlogloss",
    )
