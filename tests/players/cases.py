from app.data.connection import Player
from tests.data.player_contract_data import THOMPSON_CONTRACT_DATA
from tests.players.dataclasses import GetSalaryYearsTestCase

GET_SALARY_TEST_DATA_TEST_CASES = [
    GetSalaryYearsTestCase(
        id="Active Veteran",
        name="Klay Thompson",
        expected_seasons=range(2011, 2028),
        seed_data=THOMPSON_CONTRACT_DATA,
    ),
    GetSalaryYearsTestCase(
        id="Active Veteran",
        name="Klay Thompson",
        expected_seasons=range(2011, 2028),
        seed_data=THOMPSON_CONTRACT_DATA,
    ),
]
