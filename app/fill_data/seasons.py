from pandas import read_csv

from app.data.connection import get_session
from app.data.league.season import Season


def parse_dollars(value: str) -> int:
    return int(value.replace("$", "").replace(",", ""))


if __name__ == "__main__":
    with get_session() as session:
        for year, cap, inflation_adjusted in read_csv(
            filepath_or_buffer="data/cap-by-year.csv", index_col=0
        ).itertuples():
            session.add(
                Season(
                    id=year,
                    max_salary_cap=parse_dollars(cap) if cap == cap else None,
                    inflation_adjusted_cap=parse_dollars(inflation_adjusted)
                    if inflation_adjusted == inflation_adjusted
                    else None,
                    luxury_tax_threshold=None,
                    first_apron=None,
                    second_apron=None,
                )
            )
            session.commit()
