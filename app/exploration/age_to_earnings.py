# Prepare data
from collections.abc import Iterable

from matplotlib import pyplot as plt

from app.data.league import PlayerSeason, TeamPlayerBuyout, TeamPlayerSalary


def save_age_to_earnings_boxplot(
    rows: Iterable[tuple[PlayerSeason, TeamPlayerSalary, TeamPlayerBuyout]],
) -> None:
    ages = sorted({int(ps.age) for ps, _, _ in rows if ps.age is not None})
    dollars: dict[int, list[int]] = {age: [] for age in ages}
    relative_dollars: dict[int, list[float]] = {age: [] for age in ages}

    for ps, tps, tpb in rows:
        if ps.season_id < 2011:
            continue
        if (age := ps.age) is None:
            print(f"missing age for {ps.player.name}")
            continue
        dollars[int(age)].append(0)
        relative_dollars[int(age)].append(0)
        if tps:
            dollars[int(age)][-1] += tps.dollars
            relative_dollars[int(age)][-1] += tps.relative_dollars
        if tpb:
            dollars[int(age)][-1] += tpb.dollars
            relative_dollars[int(age)][-1] += tpb.relative_dollars

    # Convert dict to list of lists for boxplot
    ages = sorted(relative_dollars.keys())
    data_to_plot = [relative_dollars[age] for age in ages]

    # Create boxplot
    plt.figure(figsize=(10, 6))
    plt.boxplot(data_to_plot, labels=ages)
    plt.xlabel("Age")
    plt.ylabel("Relative Dollars")
    plt.title("Distribution of Relative Earnings Compared to the Cap by Age")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.savefig("documentation/images/relative_earnings_by_age.png")
