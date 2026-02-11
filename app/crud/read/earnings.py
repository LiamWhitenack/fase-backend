from sqlalchemy import Select, or_, select

from app.data.league import PlayerSeason, TeamPlayerBuyout, TeamPlayerSalary


def get_all_earnings() -> Select[
    tuple[PlayerSeason, TeamPlayerSalary, TeamPlayerBuyout]
]:
    stmt = (
        select(PlayerSeason, TeamPlayerSalary, TeamPlayerBuyout)
        .outerjoin(
            TeamPlayerSalary,
            (TeamPlayerSalary.player_id == PlayerSeason.player_id)
            & (TeamPlayerSalary.season_id == PlayerSeason.season_id),
        )
        .outerjoin(
            TeamPlayerBuyout,
            (TeamPlayerBuyout.player_id == PlayerSeason.player_id)
            & (TeamPlayerBuyout.season_id == PlayerSeason.season_id),
        )
        .where(
            or_(
                TeamPlayerSalary.id.isnot(None),
                TeamPlayerBuyout.id.isnot(None),
            )
        )
    )

    return stmt
