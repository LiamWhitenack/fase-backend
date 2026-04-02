from sklearn.model_selection import train_test_split

from app.exploration.machine_learning_ii.train_models.helper_classes import (
    PreparedData,
    SplitData,
)


def split_training_data(
    prepared_data: PreparedData,
    *,
    test_season: int,
) -> SplitData:
    train_indeces = prepared_data.features["season"] < test_season
    test_indeces = prepared_data.features["season"] == test_season

    return SplitData(
        X_train=prepared_data.features[train_indeces],
        X_test=prepared_data.features[test_indeces],
        y_train=prepared_data.target[train_indeces],
        y_test=prepared_data.target[test_indeces],
    )
