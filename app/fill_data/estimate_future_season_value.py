from datetime import datetime

from sqlalchemy import select

from app.data.connection import get_session
from app.data.league import Season

if __name__ == "__main__":
    with get_session() as session:
        seasons = session.execute(select(Season)).scalars()
        sorted_seasons = sorted(seasons, key=lambda s: s.id)
        caps = [s for s in sorted_seasons if s.max_salary_cap is not None][-5:]
        first, last = caps[0], caps[-1]
        interest = (last.max_salary_cap / first.max_salary_cap) ** (
            1 / last.id - first.id
        )
        for last_season, season in zip(sorted_seasons, sorted_seasons[1:]):
            if season.id < datetime.now().year:
                season.expected_cap = None
            elif season.id < datetime.now().year + 10:
                this_cap = (
                    last_season.max_salary_cap
                    if last_season.max_salary_cap
                    else last_season.expected_cap
                )
                season.expected_cap = round(this_cap * interest)
                session.commit()
