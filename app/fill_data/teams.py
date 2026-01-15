from pandas import Series, read_csv

from app.data.connection import get_session
from app.data.league.team import Team


def team_from_row(id: int, row: Series) -> Team:
    return Team(
        id=id,
        city=row["city"],
        name=f"{row['city']} {row['nickname']}",
        nickname=row["nickname"],
        abbreviation=row["abbreviation"],
        conference=row["conference"],
        division=row["division"],
    )


def upload_teams() -> None:
    df = read_csv("data/teams.csv")
    with get_session() as session:
        for team in map(lambda row: team_from_row(*row), df.iterrows()):  # type: ignore
            session.add(team)
        session.commit()


if __name__ == "__main__":
    upload_teams()
