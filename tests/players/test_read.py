from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.crud.read.player import get_player_by_name
from app.data.league import TeamPlayerSalary
from app.data.league.player import Player
from tests.conftest import parametrize
from tests.data.thompson_contract_data import THOMPSON_CONTRACT_DATA
from tests.players.cases import (
    GET_AGGREGATE_SALARY_TEST_CASES,
    GET_SALARY_YEARS_TEST_CASES,
)
from tests.players.dataclasses import GetAggregateSalaryTestCase, GetSalaryYearsTestCase
from tests.utils import seed_test_data


@parametrize()
def test_get_active_players(session: Session) -> None:  # @IgnoreException
    seed_test_data(session, THOMPSON_CONTRACT_DATA)
    active_players = (
        session.execute(select(Player.name).where(Player.roster_status == 1))
        .scalars()
        .all()
    )
    assert "Amen Thompson" in active_players


@parametrize(GET_SALARY_YEARS_TEST_CASES)
def test_get_salaries_for_player(  # @IgnoreException
    session: Session, case: GetSalaryYearsTestCase
) -> None:
    seed_test_data(session, case.seed_data)
    player = get_player_by_name(session, case.name)
    salaries = player.salaries
    assert {s.season for s in salaries} == set(case.expected_seasons)


@parametrize(GET_AGGREGATE_SALARY_TEST_CASES)
def test_get_aggregate_earnings_for_player(  # @IgnoreException
    session: Session, case: GetAggregateSalaryTestCase
) -> None:
    seed_test_data(session, case.seed_data)
    player = get_player_by_name(session, case.name)
    salaries: Iterable[TeamPlayerSalary] = player.salaries
    assert case.expected_aggregate_salary == sum(s.salary for s in salaries)
