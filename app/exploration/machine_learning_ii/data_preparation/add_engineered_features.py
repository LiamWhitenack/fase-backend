import numpy as np
from pandas import DataFrame, Series

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
    # Asia
    "Israel": "Asia",
    "Georgia": "Asia",
    "Turkey": "Asia",
    "Japan": "Asia",
    # Oceania
    "Australia": "Oceania",
    "New Zealand": "Oceania",
}


def add_engineered_features(df: DataFrame) -> DataFrame:
    working = df.copy()

    # --- existing features ---
    working["estimated_strength"] = safe_divide(
        working["weight_pounds"], (working["height_inches"] ** 2)
    )

    working["season_centered"] = working["season"] - working["season"].median()
    working["season_squared"] = working["season_centered"] ** 2

    working["locale"] = working.pop("country").map(narrow_locales)

    for season in ("contract_season_", "previous_season_"):
        working[season + "free_throw_rate"] = safe_divide(
            working[season + "free_throws_attempted_pg"],
            working[season + "field_goals_attempted_pg"],
        )
        working[season + "low_sample_size"] = (
            working[season + "games_played"] * working[season + "minutes_per_game"]
        )

        # --- NEW: shrink stats toward league 33rd percentile of their career ---

        C = 150  # controls shrink strength
        minutes = (
            working[season + "minutes_per_game"] * working[season + "games_played"]
        )
        alpha = minutes / (minutes + C)

        STAT_COLS_TO_SHRINK = [
            col
            for col in working.columns
            if season in col
            and any(
                key in col
                for key in [
                    "_per_game",
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
        for col in STAT_COLS_TO_SHRINK:
            career_col = col.replace("contract_season_", pct).replace(
                "previous_season_", pct
            )
            working[f"{col}_shrunk"] = (
                alpha * working.pop(col) + (1 - alpha) * working[career_col]
            )

    return working


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
    denominator_safe = denominator.replace(0, np.nan)
    return numerator / denominator_safe
