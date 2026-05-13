from pandas import DataFrame

import app.exploration.machine_learning_ii.training.classification_models as classification
from app.exploration.machine_learning_ii.archive.optimize_classification_pipeline import (
    optimize_classification_pipeline,
)
from app.exploration.machine_learning_ii.data_preparation.default import (
    default_feature_builder,
)
from app.exploration.machine_learning_ii.training.table_results import (
    build_feature_importance_dataframe,
    build_performance_dataframe_classification,
)


def classify_contracts(
    n_trials: int = 30, test_season: int = 2026, feature_importance: bool = False
) -> None:
    # warnings.filterwarnings("error", category=UserWarning)
    res: dict[str, dict] = {}
    df_original = default_feature_builder()
    for name, model in {
        # "Decision Tree": classification.build_decision_tree_model,
        # "Extra Trees": classification.build_extra_trees_model,
        # "KNN": classification.build_knn_model,
        # "Random Forest": classification.build_random_forest_model,
        "XGBoost": classification.build_xgboost_model,
        # "logistic_regression": classification.build_logistic_regression_model,
    }.items():
        df = df_original.copy()
        print(f"starting {name} ...")
        res[name] = optimize_classification_pipeline(
            test_season=test_season,
            model_builder=model,
            n_trials=n_trials,
            df=df,
            get_feature_importance=feature_importance,
        )

    tables_names: list[tuple[DataFrame, str]] = [
        (build_performance_dataframe_classification(res), "performance")
    ]
    if feature_importance:
        tables_names.append(
            (build_feature_importance_dataframe(res), "feature_importance")
        )

    for table, name in tables_names:
        if test_season != 2026:
            name += f"_{test_season}"
        table.to_latex(
            f"documentation/report/tables/{name}_classification.tex",
            escape=True,
            float_format="%.4f",
            column_format="lccccccccc",
        )
