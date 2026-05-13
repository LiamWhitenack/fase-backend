from __future__ import annotations

from typing import Any, Protocol

import numpy as np
import numpy.typing as npt
import xgboost as xgb
from numpy.typing import NDArray
from optuna import Trial
from pandas import DataFrame, Series
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted
from xgboost import XGBClassifier, XGBRegressor

import app.exploration.machine_learning_ii.training.classification_models as classification
import app.exploration.machine_learning_ii.training.regression_models as regression
from app.exploration.machine_learning_ii.custom_types import (
    ModelBuilder,
    XGBClassifierParams,
    XGBRegressorParams,
)


class ClassifierLike(Protocol):
    classes_: NDArray

    def fit(self, X: Any, y: Any) -> "ClassifierLike": ...
    def predict_proba(self, X: Any) -> NDArray: ...


class RegressorLike(Protocol):
    def fit(self, X: Any, y: Any) -> "RegressorLike": ...
    def predict(self, X: Any) -> NDArray: ...


class XGBHybridModel(BaseEstimator, RegressorMixin):
    def __init__(
        self,
        classifier: XGBClassifierParams,
        regressor: XGBRegressorParams,
        uncertain_class_index: int = 2,
        trial: Trial | None = None,
    ) -> None:
        self.classifier_builder = classifier
        self.regressor_builder = regressor
        self.trial = trial
        self.uncertain_class_index = uncertain_class_index

    def fit(
        self,
        X: DataFrame,
        relative_dollars: Series,
    ) -> "XGBHybridModel":
        validation = X.pop("validation").astype(bool)
        labels = X.pop("contract_type")
        X_train, X_val = X[~validation], X[validation]
        y_reg_train, y_reg_val = (
            relative_dollars[~validation],
            relative_dollars[validation],
        )
        y_cls_train, y_cls_val = labels[~validation], labels[validation]

        cls_params = self.classifier_builder(self.trial)
        reg_params = self.regressor_builder(self.trial)

        dtrain_cls = xgb.DMatrix(X_train, label=y_cls_train)
        dval_cls = xgb.DMatrix(X_val, label=y_cls_val)

        dtrain_reg = xgb.DMatrix(X_train, label=y_reg_train)
        dval_reg = xgb.DMatrix(X_val, label=y_reg_val)

        self.classifier = xgb.train(
            cls_params,
            dtrain_cls,
            evals=[(dval_cls, "val")],
            verbose_eval=False,
        )

        self.regressor = xgb.train(
            reg_params,
            dtrain_reg,
            evals=[(dval_reg, "val")],
            verbose_eval=False,
        )

        self.is_fitted_ = True  # 👈 mark fitted
        return self

    def predict(self, X: DataFrame) -> NDArray:
        if "validation" in X.columns:
            del X["validation"]
        if "contract_type" in X.columns:
            del X["contract_type"]
        check_is_fitted(self, ["classifier", "regressor"])

        dmatrix = xgb.DMatrix(X)

        # ---- Classification ----
        class_proba: NDArray = self.classifier.predict(dmatrix)

        # If binary, xgboost returns shape (n,)
        if class_proba.ndim == 1:
            class_proba = np.column_stack([1 - class_proba, class_proba])

        # You must store this during fit if you want it dynamic
        class_values = np.array([0, 1, 2, 3])  # <-- adjust or store on self

        class_expected: NDArray = class_proba @ class_values

        # ---- Regression ----
        reg_pred: NDArray = self.regressor.predict(dmatrix)

        # ---- Blend ----
        p_uncertain: NDArray = class_proba[:, self.uncertain_class_index]
        p_confident: NDArray = 1 - p_uncertain

        return reg_pred

        return p_confident * class_expected + p_uncertain * reg_pred

    def _to_xgb_params(self, sk_model: XGBClassifier | XGBRegressor, task: str) -> dict:
        sk_params = sk_model.get_params()

        base = {
            "nthread": -1,
        }

        if task == "classification":
            base.update(
                {
                    "objective": "multi:softprob",
                    "eval_metric": "mlogloss",
                    "base_score": 0.5,  # 🔥 fixes your crash
                    "num_class": 4,
                }
            )
        else:
            base.update(
                {
                    "objective": "reg:squarederror",
                    "eval_metric": "rmse",
                }
            )

        passthrough = [
            "max_depth",
            "learning_rate",
            "subsample",
            "colsample_bytree",
            "min_child_weight",
            "gamma",
            "reg_alpha",
            "reg_lambda",
            "tree_method",
            "seed",
        ]

        for k in passthrough:
            if k in sk_params:
                base[k] = sk_params[k]

        return base


def build_hybrid_model(
    trial: Trial | None,
    build_classification_model: XGBClassifierParams = classification.build_xgboost_model_params,
    build_regression_model: XGBRegressorParams = regression.build_xgboost_model_params,
) -> XGBHybridModel:
    return XGBHybridModel(
        classifier=build_classification_model,
        regressor=build_regression_model,
        trial=trial,
    )
