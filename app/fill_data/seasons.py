from pandas import read_csv
from sqlalchemy import and_, select

from app.data.connection import get_session
from app.data.league.season import Season


def parse_dollars(value: str) -> int:
    return int(value.replace("$", "").replace(",", ""))


if __name__ == "__main__":
    with get_session() as session:
        for year, cap, inflation_adjusted in read_csv(
            filepath_or_buffer="data/cap-by-year.csv", index_col=0
        ).itertuples():
            if (
                session.execute(
                    select(Season).where(Season.id == year)
                ).scalar_one_or_none()
                is not None
            ):
                continue
            session.add(
                Season(
                    id=year,
                    max_salary_cap=parse_dollars(cap) if cap == cap else None,
                    inflation_adjusted_cap=parse_dollars(inflation_adjusted)
                    if inflation_adjusted == inflation_adjusted
                    else None,
                )
            )
            session.commit()

        for year in range(1950, 2099):
            if (
                session.execute(
                    select(Season).where(Season.id == year)
                ).scalar_one_or_none()
                is not None
            ):
                continue
            session.add(Season(id=year))
            session.commit()
