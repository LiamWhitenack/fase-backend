import numpy as np
from pandas import DataFrame, read_csv, read_parquet


def contracts_for_ml() -> DataFrame:
    df = read_parquet("data/contracts-for-ml.parquet")
    df = df[df["season"] < 2027 & df["contract_num"] > 1]

    df["draft_round"] = df["draft_round"].replace({np.nan: 3})
    df["draft_number"] = df["draft_number"].replace({np.nan: 61})
    contract_columns = [
        "cap_hit_percent",
        "salary",
        "apron_salary",
        "luxury_tax",
        "cash_total",
        "cash_garunteed",
    ]
    df = df.drop(columns=contract_columns)

    leakage_columns = [
        "buyout",
        "team",
        "team_id",
        "ascending",
        "duration",
        "dollars",
    ]
    return df.drop(columns=leakage_columns)
