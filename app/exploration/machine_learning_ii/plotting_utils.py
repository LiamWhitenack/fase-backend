import math
from collections.abc import Callable, Iterable
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from pandas import DataFrame, Series, concat, to_datetime
from sklearn.metrics import confusion_matrix

from app.exploration.machine_learning_ii.training.helper_classes import PreparedData
from app.exploration.machine_learning_ii.utils import to_filename

THEME = {
    # Core NBA colors
    "blue": "#17408B",  # NBA blue
    "red": "#C9082A",  # NBA red (accent)
    # Neutrals
    "dark_gray": "#1D1D1D",
    "gray": "#8A8A8A",
    "light_gray": "#E5E5E5",
    "white": "#FFFFFF",
    # Additional high-contrast colors
    "orange": "#FF7F0E",  # strong contrast (matplotlib default)
    "green": "#2CA02C",  # clear, distinct green
    "purple": "#9467BD",  # strong purple
    "teal": "#17BECF",  # blue-green, highly distinguishable
    "gold": "#DAA520",  # warm gold
    "pink": "#E377C2",  # soft but distinct
    "brown": "#8C564B",  # earthy tone
    "lime": "#BCBD22",  # yellow-green
}

plt.rcParams.update(
    {
        "figure.figsize": (8, 5),
        "axes.edgecolor": THEME["gray"],
        "axes.labelcolor": THEME["gray"],
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.color": THEME["gray"],
        "ytick.color": THEME["gray"],
        # "grid.color": THEME["light_gray"],
        "grid.linestyle": "-",
        "grid.linewidth": 0.8,
        # "axes.grid": True,
        "grid.alpha": 0.5,
    }
)


def bar_plot(
    df: DataFrame,
    x_col: str,
    y_col: str,
    *,
    show: bool = False,
    color_col: str | None = None,
    agg: Callable[[Series], float] = Series.mean,
    title: str,
    figsize: tuple[float, float] = (8, 5),
    sort_by_index: bool = False,  # NEW
    ascending: bool = True,  # NEW
) -> Path:
    working = df[[x_col, y_col] + ([color_col] if color_col else [])].copy()

    # Replace missing category values with "None"
    working[x_col] = (
        working[x_col]
        .astype("object")
        .where(working[x_col].notna(), "None")
        .replace("", "None")
    )

    if color_col:
        working[color_col] = (
            working[color_col]
            .astype("object")
            .where(working[color_col].notna(), "None")
            .replace("", "None")
        )

    grouped = (
        working.dropna(subset=[y_col]).groupby(x_col, observed=True)[y_col].apply(agg)
    )
    if sort_by_index:
        grouped = grouped.sort_index(ascending=ascending)
    else:
        grouped = grouped.sort_values(ascending=ascending)

    fig, ax = plt.subplots(figsize=figsize)

    # Default single color
    if not color_col:
        ax.barh(
            grouped.index.astype(str),
            grouped.values,  # ty:ignore[invalid-argument-type]
            color=THEME["blue"],
            edgecolor=THEME["gray"],
            alpha=0.9,
        )

    # Color by feature (consistent palette cycling)
    else:
        # Map each category to a color
        categories = working[[x_col, color_col]].drop_duplicates()
        color_map = {}
        palette = list(THEME.values())

        for i, value in enumerate(
            working.groupby(x_col)[color_col].agg(lambda s: s.mode().iloc[0])
        ):
            color_map[value] = palette[i % len(palette)]

        colors = [
            color_map[working.loc[working[x_col] == idx, color_col].mode().iloc[0]]
            for idx in grouped.index
        ]

        ax.barh(
            grouped.index.astype(str),
            grouped.values,  # ty:ignore[invalid-argument-type]
            color=colors,
            edgecolor=THEME["gray"],
            alpha=0.9,
        )

    ax.invert_yaxis()
    ax.grid(False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_ylabel(x_col)
    ax.set_xlabel(f"{agg.__name__}({y_col})")  # type: ignore

    if title:
        ax.set_title(title)

    plt.tight_layout()

    save_path = Path("documentation/report/plots") / to_filename(title)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()
    plt.close(fig)

    return save_path


def line_plot_with_predictions(
    df: DataFrame,
    x_col: str,
    y_col: str,
    group_cols: str | Iterable[str] | None,
    pred_col: str,
    *,
    show: bool = False,
    agg: Callable[[Series], float] = Series.mean,
    title: str,
    linear_scale: bool = True,
    figsize: tuple[float, float] = (8, 5),
) -> Path:
    if group_cols is None:
        group_cols_list: list[str] = []
    elif isinstance(group_cols, str):
        group_cols_list = [group_cols]
    else:
        group_cols_list = list(group_cols)

    required_cols = [x_col, y_col] + group_cols_list
    required_cols.append(pred_col)

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in DataFrame: {missing}")

    working = df[required_cols].copy()

    for col in group_cols_list + [x_col]:
        working[col] = (
            working[col]
            .astype("object")
            .where(working[col].notna(), "None")
            .replace("", "None")
        )

    group_keys = [x_col] + group_cols_list

    grouped_actual = (
        working.groupby(group_keys, observed=True)[y_col].apply(agg).reset_index()
    )

    grouped_pred = (
        working.groupby(group_keys, observed=True)[pred_col].apply(agg).reset_index()
    )

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    if not linear_scale:
        ax.set_yscale("log")

    if group_cols_list:
        for name, sub_actual in grouped_actual.groupby(group_cols_list):
            label_base = name if isinstance(name, str) else " | ".join(map(str, name))
            sub_actual = sub_actual.sort_values(x_col)

            ax.plot(
                sub_actual[x_col],
                sub_actual[y_col],
                linewidth=2,
                alpha=0.9,
                label=f"{label_base} (Actual)",
            )

            sub_pred = grouped_pred[grouped_pred[group_cols_list] == name]
            sub_pred = sub_pred.sort_values(x_col)

            ax.plot(
                sub_pred[x_col],
                sub_pred[pred_col],
                linestyle="--",
                linewidth=2,
                alpha=0.9,
                label=f"{label_base} (Predicted)",
            )

        ax.legend(frameon=False)

    else:
        grouped_actual = grouped_actual.sort_values(x_col)

        ax.plot(
            grouped_actual[x_col],
            grouped_actual[y_col],
            linewidth=2,
            label="Actual",
        )

        grouped_pred = grouped_pred.sort_values(x_col)

        ax.plot(
            grouped_pred[x_col],
            grouped_pred[pred_col],
            linestyle="--",
            linewidth=2,
            label="Predicted",
        )

        ax.legend(frameon=False)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    ax.set_xlabel(x_col)
    ax.set_ylabel(f"{agg.__name__}({y_col})")  # ty:ignore[unresolved-attribute]

    if title:
        ax.set_title(title)

    plt.tight_layout()

    save_path = Path("documentation/report/plots") / to_filename(title)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)

    return save_path


def line_plot(
    df: DataFrame,
    x_col: str,
    y_col: str,
    group_cols: str | Iterable[str] | None,
    *,
    show: bool = False,
    agg: Callable[[Series], float] = Series.mean,
    title: str,
    linear_scale: bool = True,
    figsize: tuple[float, float] = (8, 5),
) -> Path:
    if group_cols is None:
        group_cols_list: list[str] = []
    elif isinstance(group_cols, str):
        group_cols_list = [group_cols]
    else:
        group_cols_list = list(group_cols)

    required_cols = [x_col, y_col] + group_cols_list

    # Only select columns that actually exist
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in DataFrame: {missing}")

    working = df[required_cols].copy()

    # Replace missing values in grouping + x columns
    for col in group_cols_list + [x_col]:
        working[col] = (
            working[col]
            .astype("object")
            .where(
                working[col].notna(),
                "None",
            )
            .replace("", "None")
        )

    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)

    if not linear_scale:
        ax.set_yscale("log")

    if group_cols_list:
        for name, sub in df.groupby(group_cols_list):
            label = name if isinstance(name, str) else " | ".join(map(str, name))
            ax.plot(
                sub[x_col],
                sub[y_col],
                label=label,
                linewidth=2,
                alpha=0.9,
            )
        ax.legend(frameon=False)
    else:
        grouped = df.sort_index(level="season")
        ax.plot(
            grouped[x_col],
            grouped[y_col],
            color=THEME["blue"],
            linewidth=2,
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    ax.set_xlabel(x_col)
    ax.set_ylabel(f"{agg.__name__}({y_col})")  # type: ignore

    if title:
        ax.set_title(title)

    plt.tight_layout()

    save_path = Path("documentation/report/plots") / to_filename(title)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()
    plt.close(fig)

    return save_path


def line_show_save_clustered(
    df: DataFrame,
    x_col: str,
    y_col: str,
    group_cols: str | Iterable[str] | None,
    *,
    agg: Callable[[Series], float] = Series.mean,
    corr_threshold: float = 0.8,
    title: str,
    figsize: tuple[float, float] = (12, 8),
    linear_scale: bool = True,
    show: bool = False,
    smooth_window: int = 5,  # NEW: smoothing window
) -> Path:
    if group_cols is None:
        group_cols_list: list[str] = []
    elif isinstance(group_cols, str):
        group_cols_list = [group_cols]
    else:
        group_cols_list = list(group_cols)

    required_cols = [x_col, y_col] + group_cols_list
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in DataFrame: {missing}")

    working = df[required_cols].copy()

    # Clean values
    for col in group_cols_list + [x_col]:
        working[col] = (
            working[col]
            .astype("object")
            .where(working[col].notna(), "None")
            .replace("", "None")
        )

    # Combine group columns into a single series identifier
    if group_cols_list:
        working["_series"] = (
            working[group_cols_list].astype(str).agg(" | ".join, axis=1)
        )
    else:
        working["_series"] = "all"

    wide = (
        working.drop(columns=["season"])
        .pivot_table(
            index=x_col,
            columns="_series",
            values=y_col,
            aggfunc=agg,
        )
        .sort_index()
    )

    # --- COLOR MAP ---
    palette = [
        THEME["blue"],
        THEME["red"],
        THEME["gray"],
        THEME["dark_gray"],
    ]

    color_map = {col: palette[i % len(palette)] for i, col in enumerate(wide.columns)}

    # --- CORRELATION (optional grouping, but no subplots now) ---
    corr = wide.corr().abs()

    # --- PLOT ---
    fig, ax = plt.subplots(figsize=figsize)

    if not linear_scale:
        ax.set_yscale("log")

    for col in wide.columns:
        series = wide[col]

        # Smooth using rolling mean
        if smooth_window and smooth_window > 1:
            series = series.rolling(window=smooth_window, min_periods=1).mean()

        ax.plot(
            wide.index,
            series,
            linewidth=2,
            alpha=0.9,
            color=color_map[col],
            label=col,
        )

    # --- Styling ---
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    ax.set_xlabel(x_col)
    ax.set_ylabel(f"{agg.__name__}({y_col})")  # type: ignore

    if title:
        ax.set_title(title)

    ax.legend(frameon=False, fontsize=8, ncol=2)

    plt.tight_layout()

    save_path = Path("documentation/report/plots") / to_filename(title)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()

    plt.close(fig)

    return save_path


def compute_density_alpha(x: Series, y: Series, bins: int = 30) -> Series:
    # Remove NaNs
    mask = x.notna() & y.notna()
    x_vals = x[mask].to_numpy()
    y_vals = y[mask].to_numpy()

    # 2D histogram
    counts, x_edges, y_edges = np.histogram2d(x_vals, y_vals, bins=bins)

    # Assign each point to a bin
    x_idx = np.clip(np.digitize(x_vals, x_edges) - 1, 0, bins - 1)
    y_idx = np.clip(np.digitize(y_vals, y_edges) - 1, 0, bins - 1)

    bin_counts = counts[x_idx, y_idx]

    # Normalize (log scale works better for heavy skew)
    bin_counts = np.log1p(bin_counts)
    normalized = (bin_counts - bin_counts.min()) / (
        bin_counts.max() - bin_counts.min() + 1e-9
    )

    # Invert so dense = more transparent
    alpha = 1.0 - normalized * 0.8  # keep some visibility floor

    result = Series(1.0, index=x.index)
    result.loc[mask] = alpha

    return result


def scatter_plot(
    df: DataFrame,
    x_col: str,
    y_col: str,
    *,
    group_cols: str | Iterable[str] | None = None,
    color_col: str | None = None,
    size_col: str | None = None,
    show: bool = False,
    title: str,
    figsize: tuple[float, float] = (8, 5),
    linear_scale: bool = True,
    alpha: float = 0.7,
) -> Path:
    if group_cols is None:
        group_cols_list: list[str] = []
    elif isinstance(group_cols, str):
        group_cols_list = [group_cols]
    else:
        group_cols_list = list(group_cols)

    required_cols = [x_col, y_col] + group_cols_list
    if color_col:
        required_cols.append(color_col)
    if size_col:
        required_cols.append(size_col)

    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in DataFrame: {missing}")

    working = df[required_cols].copy()

    # Clean categorical columns
    for col in group_cols_list + [color_col] if color_col else []:
        if col:
            working[col] = (
                working[col]
                .astype("object")
                .where(working[col].notna(), "None")
                .replace("", "None")
            )

    fig, ax = plt.subplots(figsize=figsize)

    if not linear_scale:
        ax.set_yscale("log")

    # --- Plot logic ---
    if group_cols_list:
        grouped = working.groupby(group_cols_list, observed=True)

        for name, sub in grouped:
            label = name if isinstance(name, str) else " | ".join(map(str, name))

            ax.scatter(
                working[x_col],
                working[y_col],
                alpha=alpha,
                color=THEME["blue"],
                edgecolors=None,
            )

        ax.legend(frameon=False)

    else:
        scatter_kwargs = {
            "x": working[x_col],
            "y": working[y_col],
            "alpha": alpha,
            "color": THEME["blue"],
            "edgecolors": None,
        }

        if color_col:
            scatter_kwargs["c"] = working[color_col]
            scatter_kwargs["cmap"] = "coolwarm"

        if size_col:
            scatter_kwargs["s"] = working[size_col]

        ax.scatter(**scatter_kwargs)  # ty:ignore[invalid-argument-type]

    # --- Styling ---
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col)

    if title:
        ax.set_title(title)

    plt.tight_layout()

    save_path = Path("documentation/report/plots") / to_filename(title)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")

    if show:
        plt.show()
    plt.close(fig)

    return save_path


def plot_residuals_to_downloads(
    *,
    pipeline,
    prepared_data: PreparedData,
    file_name: str = "regression_residuals.png",
) -> None:
    # Predict on each split (adjust attribute names if your PreparedData differs)
    y_train_true, X_train = prepared_data.y_train, prepared_data.X_train
    y_val_true, X_val = prepared_data.y_validation, prepared_data.X_validation
    y_test_true, X_test = prepared_data.y_test, prepared_data.X_test

    y_train_pred = pipeline.predict(X_train)
    y_val_pred = pipeline.predict(X_val)
    y_test_pred = pipeline.predict(X_test)

    data = concat(
        [
            DataFrame(
                {
                    "predicted": y_train_pred,
                    "residual": y_train_true - y_train_pred,
                    "split": "train",
                }
            ),
            DataFrame(
                {
                    "predicted": y_val_pred,
                    "residual": y_val_true - y_val_pred,
                    "split": "validation",
                }
            ),
            DataFrame(
                {
                    "predicted": y_test_pred,
                    "residual": y_test_true - y_test_pred,
                    "split": "test",
                }
            ),
        ]
    )

    plt.figure()

    for split_name in ["train", "validation", "test"]:
        subset = data[data["split"] == split_name].sort_values("predicted")

        plt.scatter(
            subset["predicted"],
            subset["residual"],
            label=split_name,
            s=10,
            alpha=0.6,
        )

    plt.axhline(0)
    plt.xlabel("Predicted value")
    plt.ylabel("Residual (actual - predicted)")
    plt.title("Residuals vs Predicted Value")
    plt.legend()


def save_multiclass_confusion_matrices(
    *,
    prepared_data: PreparedData,
    pipeline,
    labels=None,
    file_name: str = "confusion_matrices.csv",
    plot_name: str = "confusion_matrices.png",
) -> None:
    splits = {
        "train": (
            pipeline.predict(prepared_data.X_train),
            prepared_data.decode_labels(prepared_data.y_train),
        ),
        "validation": (
            pipeline.predict(prepared_data.X_validation),
            prepared_data.decode_labels(prepared_data.y_validation),
        ),
        "test": (
            pipeline.predict(prepared_data.X_test),
            prepared_data.decode_labels(prepared_data.y_test),
        ),
    }

    downloads_path = Path.home() / "Downloads"
    downloads_path.mkdir(exist_ok=True)

    all_rows = []
    matrices = {}

    for split_name, (y_pred, y_true) in splits.items():
        cm = confusion_matrix(
            prepared_data.decode_labels(y_true)
            if y_true.dtype.name == "int64"
            else y_true,
            prepared_data.decode_labels(y_pred),
            labels=labels,
        )
        matrices[split_name] = cm

        # flatten for CSV storage
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                all_rows.append(
                    {
                        "split": split_name,
                        "true_label": i,
                        "pred_label": j,
                        "count": cm[i, j],
                    }
                )

    # ---- CSV ----
    DataFrame(all_rows).to_csv(downloads_path / file_name, index=False)

    # ---- Plot ----
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm)

    ax.set_title("Test Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")

    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(downloads_path / plot_name, bbox_inches="tight")
    plt.close()
