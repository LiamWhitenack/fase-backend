from collections.abc import Iterable

import sqlalchemy
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.static import teams as static_teams
from pandas import DataFrame
from sqlalchemy.orm import Session

from app.data.connection import get_session
from app.data.league import Team, TeamSeason
from app.fill_data.save_to_csv.scrape_spotrac_team_seasons import delay_seconds
from app.utils.team_id_map import TEAM_ID


def season_str_from_year(season: int) -> str:
    return f"{season - 1}-{str(season)[-2:]}"


def create_team_seasons(
    session: Session,
    season: int,
) -> Iterable[TeamSeason]:
    records: DataFrame = leaguestandings.LeagueStandings(
        season=season_str_from_year(season), season_type="Regular Season"
    ).get_data_frames()[0]

    for _, row in records.iterrows():
        team = (
            session.query(Team)
            .filter(Team.id == list(TEAM_ID).index(row.pop("TeamID")))
            .one_or_none()
        )

        if team is None:
            continue  # team not in DB

        exists = (
            session.query(TeamSeason)
            .filter_by(team_id=team.id, season=season)
            .one_or_none()
        )

        if exists:
            continue

        yield TeamSeason.from_league_standings_row(team.id, season, row)


def upload_team_seasons(session: Session) -> None:
    for year in range(2000, 2026):
        for team_season in create_team_seasons(session, year):
            session.add(team_season)
            session.commit()
        delay_seconds(0.5, 2)


if __name__ == "__main__":
    with get_session() as session:
        upload_team_seasons(session)
