import os
from pathlib import Path
from re import sub

import matplotlib.pyplot as plt
import numpy as np
from pandas import DataFrame, Series, read_csv

from app.crud.read.contracts_for_ml import contracts_for_ml
from app.exploration.machine_learning_ii.plotting_utils import (
    THEME,
    bar_plot,
    line_plot,
    line_plot_with_predictions,
    line_show_save_clustered,
    scatter_plot,
)

# Load your data
df = contracts_for_ml()

for filename in os.listdir("documentation/report/plots"):
    os.remove(f"documentation/report/plots/{filename}")


PLOTS_DIR = Path("documentation/report/plots")
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def to_filename(title: str) -> str:
    cleaned = title.strip().lower()
    cleaned = sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = sub(r"-+", "-", cleaned).strip("-")
    return f"{cleaned}.png"


def save_figure(fig: plt.Figure, title: str) -> None:  # pyright: ignore[reportPrivateImportUsage]
    save_path = Path("documentation/report/plots") / to_filename(title)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _valid_numeric_columns(df: DataFrame, exclude: set[str] | None = None) -> list[str]:
    if exclude is None:
        exclude = set()

    numeric_columns = [
        column
        for column in df.select_dtypes(include=[np.number]).columns
        if column not in exclude
    ]
    return numeric_columns


def _make_scatter_plot(
    df: DataFrame,
    x_column: str,
    y_column: str,
    title: str,
) -> None:
    if x_column not in df.columns or y_column not in df.columns:
        return

    working = df[[x_column, y_column]].dropna()
    if working.empty:
        return

    fig, ax = plt.subplots()
    ax.scatter(
        working[x_column],
        working[y_column],
        alpha=0.65,
        s=55,
        edgecolors=THEME["blue"],
        linewidths=1.2,
    )
    ax.set_title(title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(y_column)
    save_figure(fig, title)


def _make_binned_line_plot(
    df: DataFrame,
    x_column: str,
    y_column: str,
    bins: int,
    title: str,
) -> None:
    if x_column not in df.columns or y_column not in df.columns:
        return

    working = df[[x_column, y_column]].dropna()
    if working.empty:
        return

    if working[x_column].nunique() < bins:
        return

    working = working.copy()
    working["bin"] = np.linspace(0, bins - 1, len(working), dtype=int)
    working = working.sort_values(x_column)
    working["bin"] = np.repeat(
        np.arange(bins),
        repeats=int(np.ceil(len(working) / bins)),
    )[: len(working)]

    grouped = (
        working.groupby("bin", as_index=False)
        .agg(
            x_mean=(x_column, "mean"),
            y_mean=(y_column, "mean"),
        )
        .dropna()
    )

    if grouped.empty:
        return

    fig, ax = plt.subplots()
    ax.plot(grouped["x_mean"], grouped["y_mean"], linewidth=3)
    ax.set_title(title)
    ax.set_xlabel(x_column)
    ax.set_ylabel(f"mean({y_column})")
    save_figure(fig, title)


def plot_target_distribution(df: DataFrame) -> None:
    if "relative_dollars" not in df.columns:
        return

    values = df["relative_dollars"].dropna()
    if values.empty:
        return

    fig, ax = plt.subplots()
    ax.hist(values, bins=40, edgecolor=THEME["dark_gray"])
    ax.set_title("Relative Dollars Distribution")
    ax.set_xlabel("relative_dollars")
    ax.set_ylabel("count")
    save_figure(fig, "Relative Dollars Distribution")

    fig, ax = plt.subplots()
    ax.boxplot(values, vert=True, patch_artist=True)
    ax.set_title("Relative Dollars Boxplot")
    ax.set_ylabel("relative_dollars")
    ax.set_xticks([])
    save_figure(fig, "Relative Dollars Boxplot")

    log_values = np.log1p(values)
    fig, ax = plt.subplots()
    ax.hist(log_values, bins=40, edgecolor=THEME["dark_gray"])
    ax.set_title("Log Relative Dollars Distribution")
    ax.set_xlabel("log1p(relative_dollars)")
    ax.set_ylabel("count")
    save_figure(fig, "Log Relative Dollars Distribution")


def plot_average_relative_dollars_over_time(df: DataFrame) -> None:
    required_columns = {"season", "relative_dollars"}
    if not required_columns.issubset(df.columns):
        return

    grouped = (
        df[["season", "relative_dollars"]]
        .dropna()
        .groupby("season", as_index=False)
        .agg(mean_relative_dollars=("relative_dollars", "mean"))
        .sort_values("season")
    )

    if grouped.empty:
        return

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(grouped["season"], grouped["mean_relative_dollars"], linewidth=3)
    ax.set_title("Average Relative Value Over Time")
    ax.set_xlabel("season")
    ax.set_ylabel("mean(relative_dollars)")
    save_figure(fig, "Average Relative Value Over Time")


def plot_relative_dollars_by_season_boxplot(df: DataFrame) -> None:
    required_columns = {"season", "relative_dollars"}
    if not required_columns.issubset(df.columns):
        return

    working = df[["season", "relative_dollars"]].dropna()
    if working.empty:
        return

    seasons = sorted(working["season"].unique())
    grouped_values = [
        working.loc[working["season"] == season, "relative_dollars"].values
        for season in seasons
    ]

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.boxplot(grouped_values, labels=seasons, showfliers=False)  # ty:ignore[unknown-argument, invalid-argument-type]
    ax.set_title("Relative Dollars By Season")
    ax.set_xlabel("season")
    ax.set_ylabel("relative_dollars")
    plt.xticks(rotation=45)
    save_figure(fig, "Relative Dollars By Season")


def plot_position_boxplot(df: DataFrame) -> None:
    required_columns = {"position", "relative_dollars"}
    if not required_columns.issubset(df.columns):
        return

    working = df[["position", "relative_dollars"]].dropna()
    if working.empty:
        return

    grouped = working.groupby("position")["relative_dollars"].apply(list).sort_index()

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.boxplot(grouped.tolist(), labels=grouped.index, showfliers=False)  # ty:ignore[unknown-argument]
    ax.set_title("Relative Dollars By Position")
    ax.set_xlabel("position")
    ax.set_ylabel("relative_dollars")
    plt.xticks(rotation=30)
    save_figure(fig, "Relative Dollars By Position")


def plot_clustered_position_trends(df: DataFrame) -> None:
    required_columns = {"season", "position", "relative_dollars"}
    if not required_columns.issubset(df.columns):
        return

    working = df[["season", "position", "relative_dollars"]].dropna()
    if working.empty:
        return

    grouped = (
        working.groupby(["season", "position"], as_index=False)
        .agg(mean_relative_dollars=("relative_dollars", "mean"))
        .sort_values(["position", "season"])
    )

    fig, ax = plt.subplots(figsize=(14, 8))
    for position in sorted(grouped["position"].unique()):
        position_data = grouped[grouped["position"] == position]
        ax.plot(
            position_data["season"],
            position_data["mean_relative_dollars"],
            linewidth=2.5,
            label=position,
        )

    ax.set_title("Clustered Relative Value Trends")
    ax.set_xlabel("season")
    ax.set_ylabel("mean(relative_dollars)")
    ax.legend(ncol=2, fontsize=10)
    save_figure(fig, "Clustered Relative Value Trends")


def plot_correlation_heatmap(df: DataFrame) -> None:
    numeric_columns = _valid_numeric_columns(df)
    if "relative_dollars" not in numeric_columns:
        return

    correlations = df[numeric_columns].corr(numeric_only=True)
    target_correlations = (
        correlations["relative_dollars"]
        .drop(labels=["relative_dollars"])
        .abs()
        .sort_values(ascending=False)
    )

    top_features = target_correlations.head(15).index.tolist()
    selected_columns = ["relative_dollars"] + top_features
    matrix = df[selected_columns].corr(numeric_only=True)

    fig, ax = plt.subplots(figsize=(12, 10))
    image = ax.imshow(matrix.values, aspect="auto")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=90)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_title("Top Correlations With Relative Dollars")
    fig.colorbar(image, ax=ax)
    save_figure(fig, "Top Correlations With Relative Dollars")


def plot_missing_values(df: DataFrame) -> None:
    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_counts = missing_counts[missing_counts > 0]

    if missing_counts.empty:
        return

    top_missing = missing_counts.head(20)

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(top_missing.index, top_missing.values)  # ty:ignore[invalid-argument-type]
    ax.set_title("Top Missing Value Counts")
    ax.set_xlabel("column")
    ax.set_ylabel("missing count")
    plt.xticks(rotation=90)
    save_figure(fig, "Top Missing Value Counts")


def plot_feature_vs_target_suite(df: DataFrame) -> None:
    candidate_columns = [
        "points_pg",
        "assists_pg",
        "rebounds_pg",
        "minutes_per_game",
        "age",
        "draft_number",
        "games_played",
        "field_goal_pct",
        "three_point_pct",
        "free_throw_pct",
        "contract_season_points_pg",
        "contract_season_assists_pg",
        "contract_season_rebounds_pg",
        "contract_season_minutes_per_game",
        "contract_season_usage_pct",
        "contract_season_net_rating",
        "previous_season_points_pg",
        "previous_season_assists_pg",
        "previous_season_rebounds_pg",
        "previous_season_minutes_per_game",
        "previous_season_usage_pct",
        "previous_season_net_rating",
    ]

    for column in candidate_columns:
        if column not in df.columns:
            continue

        _make_scatter_plot(
            df=df,
            x_column=column,
            y_column="relative_dollars",
            title=f"Relative Dollars By {column}",
        )

        _make_binned_line_plot(
            df=df,
            x_column=column,
            y_column="relative_dollars",
            bins=20,
            title=f"Average Relative Dollars Across {column}",
        )


def plot_top_numeric_target_relationships(df: DataFrame, top_n: int = 8) -> None:
    numeric_columns = _valid_numeric_columns(df, exclude={"relative_dollars", "season"})
    if "relative_dollars" not in df.columns:
        return

    correlations = []
    for column in numeric_columns:
        working = df[[column, "relative_dollars"]].dropna()
        if len(working) < 10:
            continue
        correlation = working[column].corr(working["relative_dollars"])
        if np.isnan(correlation):
            continue
        correlations.append((column, abs(correlation)))

    correlations.sort(key=lambda item: item[1], reverse=True)

    for column, _ in correlations[:top_n]:
        _make_scatter_plot(
            df=df,
            x_column=column,
            y_column="relative_dollars",
            title=f"Relative Dollars By {column}",
        )


def main() -> None:
    df = contracts_for_ml()

    # 2. Relative Value Trends Over Time
    line_plot(
        df,
        x_col="season",
        y_col="relative_dollars",
        group_cols=None,
        title="Average Relative Value Over Time",
    )

    line_show_save_clustered(
        df,
        x_col="season",
        y_col="relative_dollars",
        group_cols=["position"],
        title="Clustered Relative Value Trends",
    )

    # 6. Feature Exploration vs Target
    scatter_plot(
        df, "points_pg", "relative_dollars", title="Relative Dollars By Points"
    )

    scatter_plot(
        df, "assists_pg", "relative_dollars", title="Relative Dollars By Assists"
    )

    scatter_plot(
        df, "rebounds_pg", "relative_dollars", title="Relative Dollars By Rebounds"
    )

    plot_target_distribution(df)
    plot_average_relative_dollars_over_time(df)
    plot_relative_dollars_by_season_boxplot(df)
    plot_position_boxplot(df)
    plot_clustered_position_trends(df)
    plot_correlation_heatmap(df)
    plot_missing_values(df)
    plot_feature_vs_target_suite(df)
    plot_top_numeric_target_relationships(df, top_n=8)


if __name__ == "__main__":
    main()
