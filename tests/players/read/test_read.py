from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.league.player import Player
from tests.conftest import parametrize


@parametrize()
def test_get_active_players(session: Session) -> None:
    active_players = (
        session.execute(select(Player.name).where(Player.roster_status == 1))
        .scalars()
        .all()
    )
    assert "Carmelo Anthony" not in active_players
