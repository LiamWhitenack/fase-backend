from sqlalchemy import select
from sqlalchemy.orm import Session

from app.data.league import TeamPlayerSalary
from app.data.league.player import Player
from tests.conftest import parametrize
from tests.players.cases import GET_SALARY_TEST_DATA_TEST_CASES
from tests.players.dataclasses import GetSalaryDataTestCase
from tests.utils import seed_test_data


@parametrize()
def test_get_active_players(session: Session) -> None:
    active_players = (
        session.execute(select(Player.name).where(Player.roster_status == 1))
        .scalars()
        .all()
    )
    assert "Carmelo Anthony" not in active_players


@parametrize(GET_SALARY_TEST_DATA_TEST_CASES)
def test_get_career_earnings_for_players(
    session: Session, case: GetSalaryDataTestCase
) -> None:
    seed_test_data(session, case.seed_data)
    active_players = (
        session.execute(select(Player.name).where(Player.roster_status == 1))
        .scalars()
        .all()
    )
    assert "Amen Thompson" in active_players
