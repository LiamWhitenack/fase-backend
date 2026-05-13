import numpy as np
from pandas import DataFrame, Series, concat

narrow_locales = {
    "USA": "USA",
    # New World Countries
    "Canada": "New World (Not USA)",
    "Bahamas": "New World (Not USA)",
    "Jamaica": "New World (Not USA)",
    "Haiti": "New World (Not USA)",
    "Dominican Republic": "New World (Not USA)",
    "US Virgin Islands": "New World (Not USA)",
    "Argentina": "New World (Not USA)",
    "Brazil": "New World (Not USA)",
    "Venezuela": "New World (Not USA)",
    "Mexico": "New World (Not USA)",
    "Puerto Rico": "New World (Not USA)",
    "Antigua and Barbuda": "New World (Not USA)",
    "Saint Lucia": "New World (Not USA)",
    # Europe
    "Serbia": "Europe",
    "Croatia": "Europe",
    "Sweden": "Europe",
    "Latvia": "Europe",
    "France": "Europe",
    "Lithuania": "Europe",
    "Ukraine": "Europe",
    "Czech Republic": "Europe",
    "Poland": "Europe",
    "Bosnia and Herzegovina": "Europe",
    "Greece": "Europe",
    "Spain": "Europe",
    "Portugal": "Europe",
    "United Kingdom": "Europe",
    "Montenegro": "Europe",
    "Switzerland": "Europe",
    "Finland": "Europe",
    "Slovenia": "Europe",
    "Germany": "Europe",
    "Austria": "Europe",
    "Italy": "Europe",
    "Denmark": "Europe",
    "Netherlands": "Europe",
    "Estonia": "Europe",
    "North Macedonia": "Europe",
    "Russia": "Europe",
    # Africa
    "Senegal": "Africa",
    "Egypt": "Africa",
    "Mali": "Africa",
    "Democratic Republic of the Congo": "Africa",
    "DRC": "Africa",
    "Nigeria": "Africa",
    "South Sudan": "Africa",
    "Sudan": "Africa",
    "Cameroon": "Africa",
    "Angola": "Africa",
    "Gabon": "Africa",
    "Tunisia": "Africa",
    "Guinea": "Africa",
    "Cabo Verde": "Africa",
    # Asia
    "Israel": "Asia",
    "Georgia": "Asia",
    "Turkey": "Asia",
    "Japan": "Asia",
    "Iran": "Asia",
    "China": "Asia",
    # Oceania
    "Australia": "Oceania",
    "New Zealand": "Oceania",
}


def add_lag_features(df: DataFrame) -> DataFrame:
    working = df.copy()

    for col in ("buyout", "ascending", "duration", "relative_dollars"):
        working[f"prev_{col}"] = (
            working.groupby(level="player_id")[col].shift(1).fillna(0)
        )
    working["prev_team_id"] = (
        working.groupby(level="player_id")["team_id"].shift(1).fillna(0)
    ).astype(str)

    working["any_prev_buyout"] = working.groupby(level="player_id")["buyout"].transform(
        lambda s: s.fillna(False).astype(bool).shift().astype(bool).cummax()
    )

    return working


def add_engineered_features(df: DataFrame) -> DataFrame:
    working = df.copy()

    new_features = {}

    # --- existing features ---
    new_features["estimated_strength"] = safe_divide(
        working["weight_pounds"], (working["height_inches"] ** 2)
    )

    new_features["season_centered"] = working["season"] - working["season"].median()
    new_features["season_squared"] = new_features["season_centered"] ** 2

    working["locale"] = working.pop("country").map(narrow_locales)

    # --- seasonal features ---
    for season in ("contract_season_", "previous_season_"):
        new_features[season + "free_throw_rate"] = safe_divide(
            working[season + "free_throws_attempted_pg"],
            working[season + "field_goals_attempted_pg"],
        )

        new_features[season + "low_sample_size"] = (
            working[season + "games_played"] * working[season + "minutes_pg"]
        )

        # --- shrinkage ---
        C = 150
        minutes = working[season + "minutes_pg"] * working[season + "games_played"]
        alpha = minutes / (minutes + C)

        stat_cols = [
            col
            for col in working.columns
            if season in col
            and any(
                key in col
                for key in [
                    "_pg",
                    "_rate",
                    "percent",
                    "percentage",
                    "per_36",
                    "per_100",
                ]
            )
        ]

        pct = "career_"

        for col in stat_cols:
            career_col = col.replace("contract_season_", pct).replace(
                "previous_season_", pct
            )

            career_values = working.get(career_col, None)

            if career_values is None:
                career_values = working[col].mean()

            new_features[f"{col}_shrunk"] = (
                alpha * working[col] + (1 - alpha) * career_values
            )

    # --- single concat = no fragmentation ---
    return concat([working, DataFrame(new_features)], axis=1)


def add_position_ordinal(df: DataFrame, col: str = "position") -> DataFrame:
    working = df.copy()

    mapping = {
        "guard": 0,
        "forward": 2,
        "center": 4,
    }

    def map_position(pos: str | None) -> int | None:
        if pos is None:
            return None

        pos = pos.lower()

        values = []

        if "guard" in pos:
            values.append(mapping["guard"])
        if "forward" in pos:
            values.append(mapping["forward"])
        if "center" in pos:
            values.append(mapping["center"])

        if not values:
            return None

        return sum(values) // len(values)  # average → integer

    if col in working.columns:
        working["position_ordinal"] = working.pop(col).apply(map_position)

    return working


def add_season_deltas(df: DataFrame) -> DataFrame:
    working = df.copy()

    contract_prefix = "contract_season_"
    previous_prefix = "previous_season_"

    contract_cols = [col for col in working.columns if col.startswith(contract_prefix)]

    for contract_col in contract_cols:
        base_name = contract_col.replace(contract_prefix, "")
        previous_col = f"{previous_prefix}{base_name}"

        if previous_col in working.columns:
            working[f"delta_{base_name}"] = (
                working[contract_col] - working[previous_col]
            )

    return working


def safe_divide(numerator: Series, denominator: Series) -> Series:
    denominator_safe = denominator.replace(0, 1)
    return numerator / denominator_safe
