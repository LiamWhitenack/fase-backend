from pandas import Series, read_csv
from sqlalchemy.orm import Session

from app.data.connection import get_session
from app.data.league.team import Team

NBA_TEAM_ID = [
    1610612737,  # Atlanta Hawks
    1610612738,  # Boston Celtics
    1610612751,  # Brooklyn Nets
    1610612766,  # Charlotte Hornets
    1610612741,  # Chicago Bulls
    1610612739,  # Cleveland Cavaliers
    1610612765,  # Detroit Pistons
    1610612754,  # Indiana Pacers
    1610612748,  # Miami Heat
    1610612749,  # Milwaukee Bucks
    1610612752,  # New York Knicks
    1610612753,  # Orlando Magic
    1610612755,  # Philadelphia 76ers
    1610612761,  # Toronto Raptors
    1610612764,  # Washington Wizards
    1610612742,  # Dallas Mavericks
    1610612743,  # Denver Nuggets
    1610612744,  # Golden State Warriors
    1610612745,  # Houston Rockets
    1610612746,  # Los Angeles Clippers
    1610612747,  # Los Angeles Lakers
    1610612763,  # Memphis Grizzlies
    1610612750,  # Minnesota Timberwolves
    1610612740,  # New Orleans Pelicans
    1610612760,  # Oklahoma City Thunder
    1610612756,  # Phoenix Suns
    1610612757,  # Portland Trail Blazers
    1610612758,  # Sacramento Kings
    1610612759,  # San Antonio Spurs
    1610612762,  # Utah Jazz
]

team_id_map = {team_id: i for i, team_id in enumerate(NBA_TEAM_ID)}


def get_team_id(team_id: int) -> int:
    return team_id_map[team_id]


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


def upload_teams(session: Session) -> None:
    df = read_csv("data/teams.csv")
    with get_session() as session:
        for team in map(lambda row: team_from_row(*row), df.iterrows()):
            session.add(team)
        session.commit()


if __name__ == "__main__":
    with get_session() as session:
        upload_teams(session)
