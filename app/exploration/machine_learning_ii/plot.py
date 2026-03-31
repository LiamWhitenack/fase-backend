import os

from pandas import read_csv

from app.crud.read.contracts_for_ml import contracts_for_ml
from app.exploration.machine_learning_ii.plotting_utils import (
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
scatter_plot(df, "points_pg", "relative_dollars", title="Relative Dollars By Points")

scatter_plot(df, "assists_pg", "relative_dollars", title="Relative Dollars By Assists")

scatter_plot(
    df, "rebounds_pg", "relative_dollars", title="Relative Dollars By Rebounds"
)
