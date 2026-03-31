import numpy as np
from pandas import DataFrame, read_csv


def contracts_for_ml() -> DataFrame:
    df = read_csv("data/contracts-for-ml.csv")
    df = df[df["season"] < 2027]

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

    leakage_columns = ["buyout", "ascending", "duration", "voided", "dollars"]
    return df.drop(columns=leakage_columns)
