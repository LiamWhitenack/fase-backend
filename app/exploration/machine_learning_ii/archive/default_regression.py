from pandas import DataFrame

import app.exploration.machine_learning_ii.training.regression_models as regression
from app.exploration.machine_learning_ii.data_preparation.default import (
    default_feature_builder,
)
from app.exploration.machine_learning_ii.train_models import (
    optimize_regression_pipeline,
)
from app.exploration.machine_learning_ii.training.table_results import (
    build_feature_importance_dataframe,
    build_performance_dataframe,
)


def default_regression(
    filter_to_only_mid_contracts: bool = False,
    n_trials: int = 30,
    test_season: int = 2026,
    feature_importance: bool = False,
) -> None:
    res: dict[str, dict] = {}
    df_original = default_feature_builder()
    for name, model in {
        # "Decision Tree": regression.build_decision_tree_model,
        # "Elastic Net": regression.build_elastic_net_model,
        # "Extra Trees": regression.build_extra_trees_model,
        # "KNN": regression.build_knn_model,
        # "Lasso": regression.build_lasso_model,
        # "Random Forest": regression.build_random_forest_model,
        # "Ridge": regression.build_ridge_model,
        "XGBoost": regression.build_xgboost_model,
    }.items():
        df = df_original.copy()
        if filter_to_only_mid_contracts:
            df = df[df["contract_type"].apply(lambda x: x is None or x != x)]
        print(f"starting {name} ...")
        res[name] = optimize_regression_pipeline(
            test_season=test_season,
            model_builder=model,
            n_trials=n_trials,
            df=df,
            get_feature_importance=feature_importance,
        )

    tables_names: list[tuple[DataFrame, str]] = [
        (build_performance_dataframe(res), "performance")
    ]
    if feature_importance:
        tables_names.append(
            (build_feature_importance_dataframe(res), "feature_importance")
        )
    for table, name in tables_names:
        if filter_to_only_mid_contracts:
            name += "_filtered"
        if test_season != 2026:
            name += f"_{test_season}"
        table.to_latex(
            f"documentation/report/tables/{name}.tex",
            index=False,
            escape=True,
            float_format="%.4f",
            column_format="lccccccccc",
        )
