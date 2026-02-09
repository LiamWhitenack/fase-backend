import time
from typing import Any, Literal

from nba_api.stats.endpoints import leaguedashplayerstats, playergamelog
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.static import players, teams
from requests.exceptions import JSONDecodeError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.connection import get_session
from app.data.league.player import PlayerSeason
from app.data.league.team.core import Team
from app.data.league.team.payroll import TeamPlayerSalary
from app.fill_data.teams import NBA_TEAM_ID, get_team_id
from app.utils.math_utils import delay_seconds
from app.utils.team_id_map import TEAM_ID

# Constants
REQUEST_DELAY = 1.5  # seconds between requests to avoid IP block


def get_all_players() -> list[dict]:
    """Return all NBA players."""
    return players.get_players()


def get_team_id_map(session: Session) -> dict[str, int]:
    """Return dict mapping team abbreviation to Team.id from DB."""
    return {
        team.abbreviation: team.id for team in session.execute(select(Team)).scalars()
    }


def fetch_player_season_stats(season: int) -> dict[int, dict]:
    """Fetch per-season aggregated stats using leaguedashplayerstats endpoint."""
    time.sleep(REQUEST_DELAY)
    res: dict[int, dict[str, Any]] = {}

    for prefix, stats_type in (
        (None, "Base"),
        (None, "Advanced"),
        (None, "Misc"),
        (None, "Usage"),
        # ("opp_", "Opponent"),
        # (None, "Four Factors"),
    ):
        pass
        for index, data in get_stats(season, stats_type, prefix).items():
            res[index] = res.get(index, {}) | data

    return res


def get_stats(
    season: int,
    type: Literal[
        "Base", "Advanced", "Misc", "Opponent", "Four Factors", "Usage", "All-in-One"
    ],
    prefix: str | None = None,
) -> dict[int, dict[str, Any]]:
    try:
        stats = leaguedashplayerstats.LeagueDashPlayerStats(
            season=f"{season - 1}-{str(season)[-2:]}",
            measure_type_detailed_defense=type,
            timeout=100,
        ).get_dict()["resultSets"][0]
    except JSONDecodeError:
        return {}
    if prefix:
        headers = [prefix + h for h in stats["headers"]]
    else:
        headers = stats["headers"]
    data = stats["rowSet"]
    readable = [dict(zip(headers, d)) for d in data]
    return {d.pop("PLAYER_ID"): d for d in readable}


def player_ids_to_get(session: Session) -> list[int]:
    stmt = (
        select(TeamPlayerSalary.player_id).distinct()
        # .where(
        #     TeamPlayerSalary.player_id
        # )  # .not_in(select(PlayerSeason.player_id)))
    )

    return set(session.execute(stmt).scalars().all())  # type: ignore


def player_season_ids(session: Session) -> set[tuple[int, int]]:
    return set(  # type: ignore
        session.execute(
            select(
                PlayerSeason.player_id,
                PlayerSeason.season_id,
            )
        ).all()
    )


def upload_player_seasons(session: Session) -> None:
    player_season: set[tuple[int, int]] = player_season_ids(session)

    for season in range(2004, 2027):  # up to 2025-26
        stats = fetch_player_season_stats(season)
        for player_id in set(stats).intersection(player_ids_to_get(session)):
            data = stats[player_id]
            if (player_id, season) in player_season:
                continue

            # Map NBA API stats to your model fields

            ps = PlayerSeason.from_nba_api_json(
                player_id, get_team_id(data["TEAM_ID"]), season, data
            )

            session.add(ps)
            session.commit()

        delay_seconds(5, 5)


if __name__ == "__main__":
    with get_session() as session:
        upload_player_seasons(session)
