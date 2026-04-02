import matplotlib.pyplot as plt
from numpy import expm1, log1p, ndarray
from pandas import Series
from sklearn.preprocessing import PowerTransformer

from app.exploration.machine_learning_ii.utils import save_figure


def plot_target_distributions(y_raw: Series, y_transformed: Series) -> None:
    plt.figure(figsize=(10, 5))
    plt.hist(y_raw, bins=40)
    plt.title("Raw Target Distribution: relative_dollars")
    plt.xlabel("relative_dollars")
    plt.ylabel("Count")
    save_figure("target_distribution_raw.png")

    plt.figure(figsize=(10, 5))
    plt.hist(y_transformed, bins=40)
    plt.title("Transformed Target Distribution: relative_dollars")
    plt.xlabel("transformed relative_dollars")
    plt.ylabel("Count")
    save_figure("target_distribution_transformed.png")


def transform_target(y: Series) -> Series:
    return Series(log1p(y.astype(float)), index=y.index, name=y.name)


def inverse_transform_target(y_transformed: Series | ndarray) -> Series:
    values = (
        y_transformed.to_numpy() if isinstance(y_transformed, Series) else y_transformed
    )
    return Series(expm1(values))
