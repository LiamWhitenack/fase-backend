import time

from nba_api.stats.endpoints import leaguedashplayerstats, playergamelog
from nba_api.stats.static import players, teams
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.connection import get_session
from app.data.league.payroll import TeamPlayerSalary
from app.data.league.player import PlayerSeason
from app.data.league.team import Team
from app.fill_data.teams import NBA_TEAM_ID, get_team_id
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

    stats = leaguedashplayerstats.LeagueDashPlayerStats(
        season=f"{season}-{str(season)[-2:]}",
        measure_type_detailed_defense="Advanced",
    ).get_dict()["resultSets"][0]
    headers = stats["headers"]
    data = stats["rowSet"]
    readable_data = [dict(zip(headers, d)) for d in data]
    return {d.pop("PLAYER_ID"): d for d in readable_data}


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
                PlayerSeason.season,
            )
        ).all()
    )


def upload_player_seasons(session: Session) -> None:
    player_season: set[tuple[int, int]] = player_season_ids(session)

    for season in range(2011, 2026):  # up to 2025-26
        stats = fetch_player_season_stats(season)
        for player_id in set(stats).intersection(player_ids_to_get(session)):
            data = stats[player_id]
            if (player_id, season) in player_season:
                continue

            # Map NBA API stats to your model fields

            ps = PlayerSeason(
                player_id=player_id,
                team_id=get_team_id(data["TEAM_ID"]),
                season=season,
                age=data["AGE"],
                games_played=data["GP"],
                wins=data["W"],
                losses=data["L"],
                win_pct=data["W_PCT"],
                minutes_per_game=data["MIN"],
                offensive_rating=data["OFF_RATING"],
                defensive_rating=data["DEF_RATING"],
                net_rating=data["NET_RATING"],
                estimated_offensive_rating=data["E_OFF_RATING"],
                estimated_defensive_rating=data["E_DEF_RATING"],
                estimated_net_rating=data["E_NET_RATING"],
                assist_percentage=data["AST_PCT"],
                assist_to_turnover=data["AST_TO"],
                assist_ratio=data["AST_RATIO"],
                offensive_rebound_pct=data["OREB_PCT"],
                defensive_rebound_pct=data["DREB_PCT"],
                rebound_pct=data["REB_PCT"],
                turnover_pct=data["TM_TOV_PCT"],
                effective_fg_pct=data["EFG_PCT"],
                true_shooting_pct=data["TS_PCT"],
                usage_pct=data["USG_PCT"],
                pace=data["PACE"],
                pace_per_40=data["PACE_PER40"],
                estimated_pace=data["E_PACE"],
                possessions=data["POSS"],
                pie=data["PIE"],
                field_goals_made=data["FGM"],
                field_goals_attempted=data["FGA"],
                field_goal_pct=data["FG_PCT"],
                field_goals_made_pg=data["FGM_PG"],
                field_goals_attempted_pg=data["FGA_PG"],
            )

            session.add(ps)
            session.commit()


if __name__ == "__main__":
    with get_session() as session:
        upload_player_seasons(session)
